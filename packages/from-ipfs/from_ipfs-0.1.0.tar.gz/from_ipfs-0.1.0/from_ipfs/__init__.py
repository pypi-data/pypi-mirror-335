"""
from_ipfs - Use IPFS URIs with Hugging Face transformers and llama-cpp-python.

This module patches transformers and llama-cpp-python libraries to add IPFS support.
"""

import os

__version__ = "0.1.0"

# Set up cache directory
CACHE_DIR = os.environ.get("FROM_IPFS_CACHE", os.path.expanduser("~/.cache/from_ipfs"))
os.makedirs(CACHE_DIR, exist_ok=True)

# Default IPFS gateways
DEFAULT_GATEWAYS = [
    "https://cloudflare-ipfs.com/ipfs/",
    "https://gateway.ipfs.io/ipfs/",
    "https://ipfs.io/ipfs/",
    "https://dweb.link/ipfs/",
]

# User-defined gateways
if "FROM_IPFS_GATEWAYS" in os.environ:
    user_gateways = os.environ["FROM_IPFS_GATEWAYS"].split(",")
    GATEWAYS = [g.strip() for g in user_gateways if g.strip()]
else:
    GATEWAYS = DEFAULT_GATEWAYS

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

# Import other modules to make them available
from .utils import (  # noqa: E402
    clear_cache,
    download_from_ipfs,
    is_ipfs_uri,
    list_cached_models,
    show_config,
)


def patch_transformers():
    """
    Patch the transformers library to support IPFS URIs.
    """
    try:
        from .transformers_patch import apply_patch

        apply_patch()
        print("Patched transformers with IPFS support")
        return True
    except ImportError:
        print("transformers not installed, skipping patching")
        return False


def patch_llama_cpp():
    """
    Patch the llama_cpp library to support IPFS URIs.
    """
    try:
        from .llama_cpp_patch import apply_patch

        apply_patch()
        print("Patched llama-cpp-python with IPFS support")
        return True
    except ImportError:
        print("llama-cpp-python not installed, skipping patching")
        return False


def patch_all():
    """Patch all supported libraries with IPFS functionality."""
    transformers_patched = patch_transformers()
    llama_cpp_patched = patch_llama_cpp()
    return transformers_patched, llama_cpp_patched


# Run the patching automatically on import
patch_all()

__all__ = [
    "is_ipfs_uri",
    "download_from_ipfs",
    "patch_all",
    "patch_transformers",
    "patch_llama_cpp",
    "list_cached_models",
    "clear_cache",
    "show_config",
]
