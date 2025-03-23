"""
Utility functions for working with IPFS.
"""

import os
import re
import shutil
import subprocess
from typing import List, Optional
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from . import CACHE_DIR, GATEWAYS


def is_ipfs_uri(uri: str) -> bool:
    """
    Check if a URI is an IPFS URI.

    Args:
        uri: The URI to check

    Returns:
        bool: True if the URI is an IPFS URI, False otherwise
    """
    return uri.startswith("ipfs://")


def extract_cid_from_uri(uri: str) -> str:
    """
    Extract the CID from an IPFS URI.

    Args:
        uri: The IPFS URI

    Returns:
        str: The CID part of the URI
    """
    if not is_ipfs_uri(uri):
        raise ValueError(f"Not an IPFS URI: {uri}")

    # Remove the ipfs:// prefix and any trailing path
    parsed = urlparse(uri)
    return parsed.netloc


def get_cache_path(cid: str) -> str:
    """
    Get the path to the cached model for a CID.

    Args:
        cid: The IPFS CID

    Returns:
        str: The path to the cached model
    """
    return os.path.join(CACHE_DIR, cid)


def is_cached(cid: str) -> bool:
    """
    Check if a model with a given CID is cached.

    Args:
        cid: The IPFS CID

    Returns:
        bool: True if the model is cached, False otherwise
    """
    cache_path = get_cache_path(cid)
    return os.path.exists(cache_path)


def download_file_from_gateway(
    gateway: str, cid: str, filename: Optional[str] = None, timeout: int = 30
) -> str:
    """
    Download a single file from an IPFS gateway.

    Args:
        gateway: The gateway URL (e.g., 'https://ipfs.io/ipfs/')
        cid: The IPFS CID
        filename: Optional specific filename to download
        timeout: Request timeout in seconds

    Returns:
        str: The path to the downloaded file
    """
    url = f"{gateway.rstrip('/')}/{cid}"
    if filename:
        url = f"{url}/{filename}"

    cache_dir = get_cache_path(cid)
    os.makedirs(cache_dir, exist_ok=True)

    local_path = os.path.join(cache_dir, filename if filename else "model")

    # Stream the download with progress bar
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(local_path, "wb") as f, tqdm(
        desc=f"Downloading {filename or cid}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    return local_path


def download_directory_from_gateway(gateway: str, cid: str, timeout: int = 30) -> str:
    """
    Download a directory from an IPFS gateway.

    Args:
        gateway: The gateway URL (e.g., 'https://ipfs.io/ipfs/')
        cid: The IPFS CID
        timeout: Request timeout in seconds

    Returns:
        str: The path to the downloaded directory
    """
    # First, try to get directory listing
    url = f"{gateway.rstrip('/')}/{cid}/"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Parse file links from HTML (very basic approach)
        files = re.findall(r'href="([^"]+)"', response.text)
        files = [f for f in files if f != "../"]

        cache_dir = get_cache_path(cid)
        os.makedirs(cache_dir, exist_ok=True)

        for file in files:
            file_url = f"{url}{file}"
            local_path = os.path.join(cache_dir, file)

            # Stream the download with progress bar
            file_response = requests.get(file_url, stream=True, timeout=timeout)
            file_response.raise_for_status()

            total_size = int(file_response.headers.get("content-length", 0))

            with open(local_path, "wb") as f, tqdm(
                desc=f"Downloading {file}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

        return cache_dir
    except requests.RequestException as e:
        print(f"Failed to download directory from {gateway}: {e}")
        return ""


def download_from_ipfs(uri: str, filename: Optional[str] = None, _recursion_depth: int = 0) -> str:
    """
    Download a model from IPFS.

    Args:
        uri: The IPFS URI
        filename: Optional specific filename to download
        _recursion_depth: Internal parameter to prevent infinite recursion

    Returns:
        str: The path to the downloaded model
    """
    # Prevent infinite recursion
    if _recursion_depth > 3:
        raise RuntimeError(f"Maximum recursion depth exceeded when downloading {uri}")

    # Guard against non-IPFS URIs
    if not is_ipfs_uri(uri):
        raise ValueError(f"Not an IPFS URI: {uri}")

    print(f"Downloading model from IPFS: {uri}")
    cid = extract_cid_from_uri(uri)

    # Check if already cached
    if is_cached(cid):
        cache_path = get_cache_path(cid)
        if filename and not os.path.exists(os.path.join(cache_path, filename)):
            # If specific file requested but not in cache, download it
            for gateway in GATEWAYS:
                try:
                    return download_file_from_gateway(gateway, cid, filename)
                except requests.RequestException:
                    continue
            raise RuntimeError(f"Failed to download {filename} from all gateways")
        return cache_path

    # Try each gateway until one works
    for gateway in GATEWAYS:
        try:
            if filename:
                local_path = download_file_from_gateway(gateway, cid, filename)
                if local_path:
                    return os.path.dirname(local_path)
            else:
                local_path = download_directory_from_gateway(gateway, cid)
                if local_path:
                    return local_path
        except requests.RequestException:
            continue

    # If we get here, all gateways failed
    raise RuntimeError(f"Failed to download {uri} from all gateways")


def push_to_ipfs(local_path: str) -> str:
    """
    Push a model to IPFS using the w3 CLI tool.

    Args:
        local_path: The path to the model to push

    Returns:
        str: The IPFS CID
    """
    try:
        subprocess.run(["w3", "--version"], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        raise RuntimeError(
            "w3 CLI tool not found. Install it with: npm install -g @web3-storage/w3cli"
        ) from e

    # Upload to IPFS
    result = subprocess.run(["w3", "up", local_path], check=True, capture_output=True, text=True)

    # Extract CID from output
    output = result.stdout
    match = re.search(r"(Qm[a-zA-Z0-9]{44}|bafy[a-zA-Z0-9]{44})", output)
    if not match:
        raise RuntimeError(f"Failed to extract CID from output: {output}")

    return match.group(0)


def list_cached_models() -> List[str]:
    """
    List all cached models.

    Returns:
        List[str]: A list of CIDs for all cached models
    """
    if not os.path.exists(CACHE_DIR):
        return []

    return [d for d in os.listdir(CACHE_DIR) if os.path.isdir(os.path.join(CACHE_DIR, d))]


def clear_cache(cid: Optional[str] = None) -> None:
    """
    Clear the model cache.

    Args:
        cid: Optional specific CID to clear
    """
    if cid:
        cache_path = get_cache_path(cid)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            print(f"Cleared cache for {cid}")
        else:
            print(f"No cache found for {cid}")
    else:
        if os.path.exists(CACHE_DIR):
            for item in os.listdir(CACHE_DIR):
                item_path = os.path.join(CACHE_DIR, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print("Cleared all caches")
        else:
            print("No cache directory found")


def show_config() -> None:
    """
    Show the current configuration.
    """
    from . import __version__

    print("from_ipfs configuration:")
    print(f"  - Version: {__version__}")
    print(f"  - Cache directory: {CACHE_DIR}")
    print("  - IPFS gateways:")
    for gateway in GATEWAYS:
        print(f"    - {gateway}")

    # Show environment variables
    print("\nEnvironment variables:")
    print(
        f"  - FROM_IPFS_CACHE: {'Set to ' + os.environ.get('FROM_IPFS_CACHE') if 'FROM_IPFS_CACHE' in os.environ else 'Not set (using default)'}"
    )
    print(
        f"  - FROM_IPFS_GATEWAYS: {'Set to ' + os.environ.get('FROM_IPFS_GATEWAYS') if 'FROM_IPFS_GATEWAYS' in os.environ else 'Not set (using default)'}"
    )
