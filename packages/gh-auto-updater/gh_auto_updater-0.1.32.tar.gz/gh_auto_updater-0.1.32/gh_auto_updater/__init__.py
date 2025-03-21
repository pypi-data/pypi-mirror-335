#!/usr/bin/env python3
import asyncio
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime
from http.client import HTTPException
from pathlib import Path
from shutil import unpack_archive
from typing import Callable, Any, Mapping, Unpack

import aiofiles
import aiohttp
import tqdm
from dacite import from_dict as from_dict_og, Config
from loguru import logger
from packaging.version import Version

FROZEN = getattr(sys, 'frozen', False)
WIN_ROBOCOPY_OVERWRITE = (
    '/e',  # include subdirectories, even if empty
    '/move',  # deletes files and dirs from source dir after they've been copied
    '/v',  # verbose (show what is going on)
    '/w:2',  # set retry-timeout (default is 30 seconds)
    '/XD asset'
)
WIN_BATCH_DELETE_SELF = '(goto) 2>nul & del "%~f0"'
WIN_BATCH_TEMPLATE = """@echo off
echo Moving app files...
robocopy "{src_dir}" "{dst_dir}" {robocopy_options}
echo Done.
{restart_app}
{delete_self}
"""
WIN_BATCH_PREFIX = 'ghau'
WIN_BATCH_SUFFIX = '.bat'

ARCHIVE_CONTENT_TYPES = ["application/zip", "application/x-gtar", "application/x-gzip", "application/x-zip-compressed"]

BASE_REPOS_URL = "https://api.github.com/repos"

logger.configure(handlers=[dict(sink=sys.stdout, level="DEBUG")])


@dataclass
class BaseDataclass:
    def __post_init__(self):
        dt_fieldnames = [
            name
            for name, field in type(self).__dataclass_fields__.items()
            if field.type is datetime
        ]

        for fname in dt_fieldnames:
            setattr(
                self,
                fname,
                datetime.fromisoformat(getattr(self, fname))
            )


def from_dict[T](dclass: type[T], data: Mapping[str, Any]) -> T:
    return from_dict_og(dclass, data, config=Config(check_types=False))


@dataclass
class Item(BaseDataclass):
    id: int
    url: str
    created_at: datetime


@dataclass
class Asset(Item):
    name: str
    content_type: str
    browser_download_url: str
    updated_at: datetime
    label: str | None = None


@dataclass
class Release(Item):
    tag_name: str
    body: str
    prerelease: bool
    published_at: datetime
    assets: list[Asset]
    tarball_url: str | None = None
    zipball_url: str | None = None


class TooManyRequests(HTTPException):
    pass


class NotFound(HTTPException):
    pass


async def get_release(
        session_: aiohttp.ClientSession,
        releases_url: str,
        prerelease: bool = False,
) -> Release:
    """

    :raises TooManyRequests: if the rate limit is exceeded
    """
    url = releases_url + ("?per_page=1" if prerelease else "/latest")
    async with session_.get(url) as resp:
        data = await resp.json()

    if resp.status in [403, 429]:
        raise TooManyRequests("Got rate limited, x-ratelimit-reset=" + resp.headers["x-ratelimit-reset"])

    if resp.status == 404:
        raise NotFound("Repository was not found.")

    if prerelease:
        data = data[0]

    return from_dict(Release, data)


def _use_filters(asset: Asset, filters: dict[str, Callable[[Any], bool]]) -> bool:
    dumped = asdict(asset)
    for field_name, filter_ in filters.items():
        if field_name not in dumped.keys():
            logger.warning(f"Key {field_name} doesn't exist on the asset with id {asset.id}")
            return False

        if not filter_(dumped[field_name]):
            return False

    return True


def filter_assets(
        assets: list[Asset], *,
        name_pattern: re.Pattern | str,
        **extra_filters: Unpack[Callable[[Any], bool]]
) -> list[Asset]:
    result = []
    for asset in assets:
        if not re.match(name_pattern, asset.name):
            continue

        if not _use_filters(asset, extra_filters):
            continue

        result.append(asset)

    return result


async def download_asset(
        session_: aiohttp.ClientSession,
        download_url: str,
        local_asset_path: Path
):
    local_asset_path.parent.mkdir(exist_ok=True)

    asset_name = download_url.rpartition('/')[-1]
    chunk_size = 4096

    logger.info("Downloading update")
    async with session_.get(download_url) as resp:
        size = int(resp.headers.get('content-length', 0)) or None
        pbar = tqdm.tqdm(desc=asset_name, total=size, leave=False)

        async with aiofiles.open(local_asset_path, "wb") as f:
            async for data in resp.content.iter_chunked(chunk_size):
                # noinspection PyTypeChecker
                await f.write(data)
                # noinspection PyTypeChecker
                pbar.update(len(data))


def run_bat_as_admin(file_path: Path | str):
    """ **Taken from dennisvang/tufup**
    Request elevation for windows command interpreter (opens UAC prompt) and
    then run the specified .bat file.

    Returns True if successfully started, does not block, can continue after
    calling process exits.
    """
    from ctypes import windll

    # https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew
    result = windll.shell32.ShellExecuteW(
        None,  # handle to parent window
        'runas',  # verb
        'cmd.exe',  # file on which verb acts
        ' '.join(['/c', f'"{file_path}"']),  # parameters
        None,  # working directory (default is cwd)
        1,  # show window normally
    )
    success = result > 32
    if not success:
        logger.error(
            f'failed to run batch script as admin (ShellExecuteW returned {result})'
        )
    return success


def install_update_and_restart(
        src_dir: Path | str,
        dst_dir: Path | str,
        batch_template: str = WIN_BATCH_TEMPLATE,
        as_admin: bool = False,
        process_creation_flags=None,
        restart_cmd: str = None,
        **kwargs,  # noqa
):
    """ **Taken from dennisvang/tufup**
    Create a batch script that moves files from src to dst, then run the
    script in a new console, and exit the current process.

    The script is created in a default temporary directory, and deletes
    itself when done.

    The `as_admin` options allows installation as admin (opens UAC dialog).

    The `batch_template` option allows specification of custom batch-file
    content. This may be in the form of a template string, as in the default
    `WIN_BATCH_TEMPLATE`, or it may be a ready-made string without any
    template variables. The following default template variables are
    available for use in the custom template, although their use is optional:
    {log_lines}, {src_dir}, {dst_dir}, {robocopy_options}, {delete_self}.
    Custom template variables can be used as well, in which case you'll need
    to specify `batch_template_extra_kwargs`.

    The `process_creation_flags` option allows users to override creation flags for
    the subprocess call that runs the batch script. For example, one could specify
    `subprocess.CREATE_NO_WINDOW` to prevent a window from opening. See [2] and [3]
    for details.

    [1]: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy
    [2]: https://docs.python.org/3/library/subprocess.html#windows-constants
    [3]: https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
    """
    # write temporary batch file (NOTE: The file is placed in the system
    # default temporary dir, but the file is not removed automatically. So,
    # either the batch file should self-delete when done, or it should be
    # deleted by some other means, because windows does not clean the temp
    # dir automatically.)
    if not restart_cmd:
        if FROZEN:
            restart_cmd = f"start /d {dst_dir} {sys.executable} {" ".join(sys.argv)}"
        else:
            py = sys.executable
            restart_cmd = f"cd /d {dst_dir}\n{py} " + " ".join(sys.argv)

    robocopy_options = ' '.join(WIN_ROBOCOPY_OVERWRITE)
    script_content = batch_template.format(
        src_dir=src_dir,
        dst_dir=dst_dir,
        delete_self=WIN_BATCH_DELETE_SELF,
        robocopy_options=robocopy_options,
        restart_app=restart_cmd
    )
    logger.debug(f'writing windows batch script:\n{script_content}')
    with tempfile.NamedTemporaryFile(
            mode='w', prefix=WIN_BATCH_PREFIX, suffix=WIN_BATCH_SUFFIX, delete=False
    ) as temp_file:
        temp_file.write(script_content)
    logger.debug(f'temporary batch script created: {temp_file.name}')

    script_path = Path(temp_file.name).resolve()
    logger.debug(f'starting script in new console: {script_path}')
    # start the script in a separate process, non-blocking
    if as_admin:
        logger.debug('as admin')
        run_bat_as_admin(file_path=script_path)
    else:
        # by default, we create a new console with window, but user can override this
        # using the process_creation_flags argument
        if process_creation_flags is None:
            process_creation_flags = subprocess.CREATE_NEW_CONSOLE
        else:
            logger.debug('using custom process creation flags')
        # we use Popen() instead of run(), because the latter blocks execution
        subprocess.Popen([script_path], creationflags=process_creation_flags)
    logger.info('Successfully updated. Exiting and restarting.')
    # exit current process
    sys.exit(0)


def apply_update_and_restart(archive_path: str | Path, extract_dir: str | Path, install_dir: str | Path):
    unpack_archive(archive_path, extract_dir)
    logger.debug(f'files extracted to {extract_dir}')

    install_update_and_restart(extract_dir, install_dir)


async def write_last_check_date(date_path: Path | str):
    async with aiofiles.open(date_path, "w+") as f:
        await f.write(str(datetime.now().timestamp()))


async def get_last_check_date(date_path: Path | str) -> datetime:
    if not date_path.is_file():
        return datetime.fromtimestamp(0)

    async with aiofiles.open(date_path, "r") as f:
        data = await f.read()

        try:
            return datetime.fromtimestamp(float(data))
        except ValueError:
            logger.critical(data + r" is not a correct timestamp")
            raise


async def close_session_on_shutdown(cb):
    stopping = False
    loop = asyncio.get_running_loop()

    async def _stop():
        logger.debug("Executing on shutdown task")
        await cb()  # Await the callback to complete asynchronously

    def new_stop():
        nonlocal stopping
        if not stopping:
            stopping = True
            logger.debug("Loop is about to stop, running shutdown task")
            # Schedule the shutdown task and stop the loop once it's complete
            loop.create_task(_stop()).add_done_callback(lambda _: original_stop())
        else:
            original_stop()

    original_stop = loop.stop
    loop.stop = new_stop  # Override the stop method with our custom logic


async def update(
        *,
        repository_name: str,
        current_version: str,
        install_dir: Path,
        prerelease: bool = False,
        asset_name_pattern: re.Pattern | str = r".*",
        checks_rate_limit_secs: int = None,
        last_check_date_path: str | Path = None,
        allow_plain: bool = False,
        **asset_field_name_to_filter: Callable[[Any], bool]
) -> bool:
    """ Updates the application from the specified GitHub repository.

    :param repository_name: the name of repository in format {username}/{repo_name}
    :param current_version: the current version of the app
    :param install_dir: a path to the installation dir
    :param prerelease: apply prerelease if available
    :param asset_name_pattern: regex name_pattern for the target asset's name
    :param checks_rate_limit_secs: amount of seconds between update checks,
        if specified, last_check_date_path is required
    :param last_check_date_path: file in which last check's date is stored
    # :param requirements: if specified will install the requirements from the file specified
    :param asset_field_name_to_filter: Asset dataclass field name to filter function for it
    :param allow_plain: whether to allow plain scripts
    :returns: False if already latest version
    :raises ValueError: if wrong repository name, if there are none, more than one asset
        and if the asset is not an archive
    :raises NotFound: if repo with repository_name was not found
    """
    if not allow_plain and not FROZEN:
        logger.warning("The app is not frozen. Abort update")
        return False

    if not re.match(r"^.+/.+$", repository_name):
        raise ValueError("Incorrect repository name. Make sure it is in format {username}/{repo_name}")

    rate_limiting = False
    if checks_rate_limit_secs:
        if not last_check_date_path:
            logger.critical("Rate limit file was not found")
            raise ValueError("last_check_date_path is not specified. "
                             "When updates_rate_limit_secs is specified last_check_date_path is required.")

        last_check_date_path = Path(last_check_date_path)
        rate_limiting = True

        last_check_date_path.parent.mkdir(exist_ok=True, parents=True)
        since_last_check = datetime.now() - await get_last_check_date(last_check_date_path)
        if since_last_check.total_seconds() < checks_rate_limit_secs:
            logger.info(f"Last update check was {int(since_last_check.total_seconds()) // 60} minutes ago. "
                        f"Skipping")
            return False

    session = aiohttp.ClientSession()
    await close_session_on_shutdown(session.close)

    releases_url = BASE_REPOS_URL + f"/{repository_name}" + "/releases"
    current_version = Version(current_version)
    extract_dir = Path(tempfile.gettempdir()) / "ghautoupdater"

    extract_dir.mkdir(exist_ok=True, parents=True)
    install_dir.mkdir(exist_ok=True, parents=True)

    try:
        release = await get_release(session, releases_url, prerelease=prerelease)
    except TooManyRequests:
        logger.warning("Rate limit exceeded")
        return False
    except NotFound as e:
        logger.critical("Repository with name " + repository_name + " was not found")
        raise e

    if rate_limiting:
        await write_last_check_date(last_check_date_path)

    if current_version == Version(release.tag_name):
        logger.info("Latest version is already installed.")
        await session.close()
        return False

    assets = filter_assets(
        release.assets,
        name_pattern=asset_name_pattern,
        **asset_field_name_to_filter
    )

    if not assets:
        raise ValueError("No assets were found for the given parameters.")
    elif len(assets) > 1:
        raise ValueError("Multiple assets found for the given parameters.")
    else:
        asset = assets[0]

    if asset.content_type not in ARCHIVE_CONTENT_TYPES:
        raise ValueError(
            asset.content_type +
            " is not a supported archive type. Available options are: " +
            " ".join(ARCHIVE_CONTENT_TYPES)
        )

    archive_path = extract_dir / "asset" / asset.name
    await download_asset(session, asset.browser_download_url, archive_path)

    await session.close()

    apply_update_and_restart(archive_path, extract_dir, install_dir)
