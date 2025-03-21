# GitHubUpdater

**GitHubUpdater** is a Python tool that allows you to manage and apply updates to your application directly from a GitHub repository. It checks for the latest release or pre-release, downloads the necessary assets, and installs the update.

## Features

- Automatically fetches the latest release or pre-release from GitHub.
- Downloads and installs release assets.
- Supports a variety of archive formats (ZIP, GTAR, GZIP, etc.).
- Manages session cleanup and handles shutdown gracefully.
- Works with both frozen applications (like PyInstaller) and scripts.

## Installation

You can install **GitHubUpdater** directly from PyPI:

```bash
pip install gh_auto_updater
```

## Usage
### 1. Basic Usage
```python
import asyncio
from gh_auto_updater import update
from pathlib import Path

async def main():
    await update(
        repository_name="yourusername/your-repo",
        current_version="1.0.0",
        install_dir=Path("/path/to/install/dir")
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Using Pre-releases
If you want to apply pre-releases:
```python
await update(
    repository_name="yourusername/your-repo",
    current_version="1.0.0",
    install_dir=Path("/path/to/install/dir"),
    prerelease=True
)
```

### 3. Filter Assets by Name or Field
You can filter which assets to download by matching the asset name or other fields:
```python
await update(
    repository_name="yourusername/your-repo",
    current_version="1.0.0",
    install_dir=Path("/path/to/install/dir"),
    asset_name_pattern=r".*win64.*",  # Only download assets for Windows 64-bit
    content_type=lambda ctype: ctype == "application/zip"
)
```

### 4. Running the Update Process as Admin on Windows
The tool can also request admin privileges (UAC prompt) for installation, especially useful for system-level updates.
```python
await update(
    repository_name="yourusername/your-repo",
    current_version="1.0.0",
    install_dir=Path("/path/to/install/dir"),
    as_admin=True  # Runs the installation with admin rights
)
```

### 5. Applying an Update with a Timeout Between Checks
```python
await update(
    repository_name="yourusername/your-repo",
    current_version="1.0.0",
    install_dir=Path("/path/to/install/dir"),
    checks_rate_limit_secs=86400,  # Check for updates once every 24 hours
    last_check_date_path=Path("/path/to/last-check-file")
)
```

## Parameters
* `repository_name` (str): The GitHub repository in the format {username}/{repo_name}.
* `current_version` (str): The current version of the app.
* `install_dir` (Path): Path to the installation directory.
* `prerelease` (bool): Set to True if you want to apply pre-releases. (default: False)
* `asset_name_pattern` (str): A regex pattern to match the name of the asset you want to download.
* `checks_rate_limit_secs` (int): Rate limit checks in seconds between update checks (optional).
* `last_check_date_path` (Path): Path to store the last check date (optional).
* `allow_plain` (bool): Whether to allow plain scripts (default: False).

## Supported Archive Formats
* `application/zip`
* `application/x-gtar`
* `application/x-gzip`
* `application/x-zip-compressed`

## License
This project is licensed under the MIT License.