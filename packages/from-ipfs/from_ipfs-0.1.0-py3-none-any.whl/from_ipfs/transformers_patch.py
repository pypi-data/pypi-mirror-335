"""
Module for patching transformers with IPFS support.
"""

import functools
from typing import Any, Type, TypeVar

from .utils import download_from_ipfs

T = TypeVar("T")


def patch_from_pretrained(cls: Type[T], original_method: Any) -> Any:
    """
    Create a patched version of the from_pretrained method.

    Args:
        cls: The class to patch
        original_method: The original from_pretrained method

    Returns:
        The patched method
    """

    @functools.wraps(original_method)
    def patched_from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
        """
        Patched from_pretrained method that supports IPFS URIs.

        Args:
            cls: The class reference
            pretrained_model_name_or_path: The model name/path or IPFS URI
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            The loaded model
        """
        if isinstance(
            pretrained_model_name_or_path, str
        ) and pretrained_model_name_or_path.startswith("ipfs://"):
            print(f"Downloading model from IPFS: {pretrained_model_name_or_path}")
            local_path = download_from_ipfs(pretrained_model_name_or_path)
            return original_method(cls, local_path, *args, **kwargs)
        return original_method(cls, pretrained_model_name_or_path, *args, **kwargs)

    return classmethod(patched_from_pretrained)


def apply_patch():
    """Apply the IPFS patches to transformers classes."""
    try:
        import transformers

        # Add more classes here as needed
        classes_to_patch = [
            (transformers.PreTrainedModel, "from_pretrained"),
            (transformers.PreTrainedTokenizer, "from_pretrained"),
            (transformers.PreTrainedTokenizerFast, "from_pretrained"),
            (transformers.ProcessorMixin, "from_pretrained"),
            (transformers.FeatureExtractionMixin, "from_pretrained"),
            (transformers.AutoModel, "from_pretrained"),
            (transformers.AutoTokenizer, "from_pretrained"),
            (transformers.AutoProcessor, "from_pretrained"),
            (transformers.AutoFeatureExtractor, "from_pretrained"),
        ]

        for cls, method_name in classes_to_patch:
            if hasattr(cls, method_name):
                original_method = getattr(cls, method_name)
                patched_method = patch_from_pretrained(cls, original_method)
                setattr(cls, method_name, patched_method)
                print(f"Patched {cls.__name__}.{method_name} with IPFS support")
    except ImportError:
        print("transformers not installed, skipping patching")
        return
