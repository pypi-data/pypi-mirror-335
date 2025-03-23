"""
Core patching utilities for from_ipfs.
"""

import functools
from typing import Any, Callable, Optional, Type, TypeVar

from .utils import download_from_ipfs, push_to_ipfs

T = TypeVar("T")


def patch_from_pretrained(cls: Type[T], original_method: Callable) -> Callable:
    """
    Create a patched version of the from_pretrained method.

    Args:
        cls: The class to patch
        original_method: The original from_pretrained method

    Returns:
        Callable: The patched method
    """

    @functools.wraps(original_method)
    def patched_from_pretrained(cls, pretrained_model_name_or_path: str, *args, **kwargs) -> T:
        # Print a message for debugging
        print(f"Patched from_pretrained called with: {pretrained_model_name_or_path}")

        # If it's an IPFS URI, download it first
        if isinstance(
            pretrained_model_name_or_path, str
        ) and pretrained_model_name_or_path.startswith("ipfs://"):
            try:
                # For llama-cpp-python, handle the 'filename' parameter
                filename = kwargs.pop("filename", None)
                print(f"Downloading model from IPFS: {pretrained_model_name_or_path}")
                local_path = download_from_ipfs(pretrained_model_name_or_path, filename)

                # Use the local path instead
                return original_method(cls, local_path, *args, **kwargs)
            except Exception as e:
                print(f"Error downloading from IPFS: {e}")
                raise

        # Otherwise, use the original method
        return original_method(cls, pretrained_model_name_or_path, *args, **kwargs)

    return classmethod(patched_from_pretrained)


def patch_push_to_hub(cls: Type[Any], original_method: Callable) -> Callable:
    """
    Create a patched version of the push_to_hub method.

    Args:
        cls: The class to patch
        original_method: The original push_to_hub method

    Returns:
        Callable: The patched method
    """

    # Define a new method push_to_ipfs
    def push_to_ipfs_method(self, local_dir: Optional[str] = None, *args, **kwargs) -> str:
        """
        Push the model to IPFS.

        Args:
            local_dir: Optional path to push instead of the model

        Returns:
            str: The IPFS CID
        """
        # If local_dir is not specified, create a temp directory and save the model there
        if local_dir is None:
            import tempfile

            # Create a temp directory
            temp_dir = tempfile.mkdtemp()

            # Save the model to the temp directory
            if hasattr(self, "save_pretrained"):
                self.save_pretrained(temp_dir)
            else:
                raise AttributeError(f"{cls.__name__} does not have a save_pretrained method")

            # Push to IPFS
            try:
                cid = push_to_ipfs(temp_dir)
                return cid
            finally:
                # Clean up
                import shutil

                shutil.rmtree(temp_dir)
        else:
            # Push the specified directory to IPFS
            return push_to_ipfs(local_dir)

    # Add the push_to_ipfs method to the class
    cls.push_to_ipfs = push_to_ipfs_method

    return original_method


def patch_class_with_ipfs_support(cls: Type, method_name: str) -> None:
    """
    Patch a class method to support IPFS URIs.

    Args:
        cls: The class to patch
        method_name: The name of the method to patch (typically 'from_pretrained')
    """
    # Get the original method
    original_method = getattr(cls, method_name)

    @functools.wraps(original_method)
    def patched_method(cls_or_self, pretrained_model_name_or_path, *args, **kwargs):
        """
        Patched method that checks for IPFS URIs and downloads them if needed.

        Args:
            cls_or_self: The class or self reference
            pretrained_model_name_or_path: The model path, which might be an IPFS URI
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            The result of the original method, but with local paths for IPFS URIs
        """
        # Check if the path is an IPFS URI
        if isinstance(
            pretrained_model_name_or_path, str
        ) and pretrained_model_name_or_path.startswith("ipfs://"):
            # Download the model from IPFS
            local_path = download_from_ipfs(pretrained_model_name_or_path)

            # Replace the IPFS URI with the local path
            pretrained_model_name_or_path = local_path

        # Call the original method with the local path
        return original_method(cls_or_self, pretrained_model_name_or_path, *args, **kwargs)

    # Replace the original method with the patched one
    if isinstance(original_method, classmethod):
        setattr(cls, method_name, classmethod(patched_method))
    else:
        setattr(cls, method_name, patched_method)
