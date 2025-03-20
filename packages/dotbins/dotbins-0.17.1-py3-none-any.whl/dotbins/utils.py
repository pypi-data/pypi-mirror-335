"""Utility functions for dotbins."""

from __future__ import annotations

import functools
import hashlib
import os
import sys
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from rich.console import Console

if TYPE_CHECKING:
    from .config import Config

console = Console()


@functools.cache
def _maybe_github_token_header(quiet: bool = False) -> dict[str, str]:  # pragma: no cover
    """Return a dictionary of headers with GitHub token if it exists."""
    headers = {}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {token}"
        if not quiet:
            log("Using GitHub token for authentication", "info", "🔑")
    return headers


@functools.cache
def latest_release_info(repo: str, quiet: bool = False) -> dict:
    """Fetch release information from GitHub for a single repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    if not quiet:
        log(f"Fetching latest release from {url}", "info", "🔍")
    headers = _maybe_github_token_header(quiet)
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        msg = f"Failed to fetch latest release for {repo}: {e}"
        raise RuntimeError(msg) from e


def _try_fetch_release_info(repo: str) -> dict | None:
    """Try to fetch release information from GitHub for a single repository."""
    try:
        return latest_release_info(repo, quiet=True)
    except Exception:
        return None


def fetch_releases_in_parallel(repos: list[str]) -> dict[str, dict | None]:
    """Fetch release information for multiple repositories in parallel.

    Args:
        repos: List of repository names in format 'owner/repo'

    Returns:
        Dictionary mapping repository names to their release information

    """
    results: dict[str, dict | None] = {}
    with ThreadPoolExecutor(max_workers=min(16, len(repos) or 1)) as ex:
        future_to_repo = {ex.submit(_try_fetch_release_info, repo): repo for repo in repos}
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            results[repo] = future.result()  # type: ignore[assignment]
    return results


def download_file(url: str, destination: str, verbose: bool) -> str:
    """Download a file from a URL to a destination path."""
    log(f"Downloading from {url}", "info", "📥")
    # Already verbose when fetching release info
    headers = _maybe_github_token_header(quiet=verbose)
    try:
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return destination
    except requests.RequestException as e:
        log(f"Download failed: {e}", "error", print_exception=verbose)
        msg = f"Failed to download {url}: {e}"
        raise RuntimeError(msg) from e


def current_platform() -> tuple[str, str]:
    """Detect the current platform and architecture.

    Returns:
        Tuple containing (platform, architecture)
        platform: 'linux' or 'macos'
        architecture: 'amd64' or 'arm64'

    """
    # Detect platform
    platform = "linux"
    if sys.platform == "darwin":
        platform = "macos"

    # Detect architecture
    arch = "amd64"
    machine = os.uname().machine.lower()
    if machine in ["arm64", "aarch64"]:
        arch = "arm64"

    return platform, arch


def print_shell_setup(config: Config) -> None:
    """Print shell setup instructions."""
    tools_path = config.tools_dir.absolute()
    tools_dir = str(tools_path).replace(os.path.expanduser("~"), "$HOME")
    print("\n# Add this to your shell configuration file (e.g., .bashrc, .zshrc):")
    print(
        f"""
# dotbins - Add platform-specific binaries to PATH
_os=$(uname -s | tr '[:upper:]' '[:lower:]')
[[ "$_os" == "darwin" ]] && _os="macos"

_arch=$(uname -m)
[[ "$_arch" == "x86_64" ]] && _arch="amd64"
[[ "$_arch" == "aarch64" || "$_arch" == "arm64" ]] && _arch="arm64"

export PATH="{tools_dir}/$_os/$_arch/bin:$PATH"
""",
    )


STYLE_EMOJI_MAP = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "🔍",
    "default": "",
}

STYLE_FORMAT_MAP = {
    "success": "green",
    "error": "bold red",
    "warning": "yellow",
    "info": "cyan",
    "default": "",
}


def log(
    message: str,
    style: str = "default",
    emoji: str = "",
    *,
    print_exception: bool = False,
) -> None:
    """Print a formatted message to the console."""
    if not emoji:
        emoji = STYLE_EMOJI_MAP.get(style, "")

    prefix = f"{emoji} " if emoji else ""

    if style != "default":
        rich_format = STYLE_FORMAT_MAP.get(style, "")
        console.print(f"{prefix}[{rich_format}]{message}[/{rich_format}]")
    else:
        console.print(f"{prefix}{message}")
    if style == "error" and print_exception:
        console.print_exception()


def calculate_sha256(file_path: str | Path) -> str:
    """Calculate SHA256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal SHA256 hash string

    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_archive(archive_path: str | Path, dest_dir: str | Path) -> None:
    """Extract an archive to a destination directory."""
    archive_path = Path(archive_path)
    dest_dir = Path(dest_dir)
    try:
        is_gzip = False
        with archive_path.open("rb") as f:
            header = f.read(3)
            if header.startswith(b"\x1f\x8b"):
                is_gzip = True

        if is_gzip or archive_path.name.endswith((".tar.gz", ".tgz")):
            with tarfile.open(archive_path, mode="r:gz") as tar:
                tar.extractall(path=dest_dir)
        elif archive_path.name.endswith((".tar.bz2", ".tbz2")):
            with tarfile.open(archive_path, mode="r:bz2") as tar:
                tar.extractall(path=dest_dir)
        elif archive_path.name.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as zip_file:
                zip_file.extractall(path=dest_dir)
        else:
            msg = f"Unsupported archive format: {archive_path}"
            raise ValueError(msg)  # noqa: TRY301
    except Exception as e:
        log(f"Extraction failed: {e}", "error", print_exception=True)
        raise


def github_url_to_raw_url(repo_url: str) -> str:
    """Convert a GitHub repository URL to a raw URL."""
    # e.g.,
    # https://github.com/basnijholt/dotbins/blob/main/dotbins.yaml
    # becomes
    # https://raw.githubusercontent.com/basnijholt/dotbins/refs/heads/main/dotbins.yaml
    if "github.com" not in repo_url or "/blob/" not in repo_url:
        return repo_url
    return repo_url.replace(
        "github.com",
        "raw.githubusercontent.com",
    ).replace(
        "/blob/",
        "/refs/heads/",
    )
