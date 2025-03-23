"""
This module patches transformers library to support IPFS URIs.
"""

import inspect
import sys
from typing import Set, Type

# Set of classes that have been patched
_patched_classes: Set[Type] = set()


def patch_transformers_classes() -> None:
    """
    Patch all transformers classes that have a from_pretrained method.
    """
    # Check if transformers is imported
    if "transformers" not in sys.modules:
        print("transformers not in sys.modules")
        return

    # List of Auto* classes we want to patch
    auto_classes = [
        "AutoModel",
        "AutoModelForCausalLM",
        "AutoModelForSequenceClassification",
        "AutoModelForQuestionAnswering",
        "AutoModelForTokenClassification",
        "AutoModelForSeq2SeqLM",
        "AutoModelForImageClassification",
    ]

    transformers = sys.modules["transformers"]

    # Directly patch the Auto classes
    for class_name in auto_classes:
        if hasattr(transformers, class_name):
            cls = getattr(transformers, class_name)
            if hasattr(cls, "from_pretrained") and cls not in _patched_classes:
                try:
                    # Import these directly to ensure they're accessible in the closure
                    import functools

                    from ..utils import download_from_ipfs

                    # Store original method
                    original_from_pretrained = cls.from_pretrained

                    # Define a replacement method that adds IPFS support
                    @classmethod
                    @functools.wraps(original_from_pretrained.__func__)
                    def patched_from_pretrained(
                        cls, pretrained_model_name_or_path, *args, **kwargs
                    ):
                        # Debug output
                        print(
                            f"Patched from_pretrained called with: {pretrained_model_name_or_path}"
                        )

                        # If it's an IPFS URI, download it first
                        if (
                            pretrained_model_name_or_path
                            and isinstance(pretrained_model_name_or_path, str)
                            and pretrained_model_name_or_path.startswith("ipfs://")
                        ):
                            print(f"Downloading model from IPFS: {pretrained_model_name_or_path}")
                            local_path = download_from_ipfs(pretrained_model_name_or_path)
                            # Use the local path instead
                            return original_from_pretrained.__func__(
                                cls, local_path, *args, **kwargs
                            )

                        # Otherwise, use the original method
                        return original_from_pretrained.__func__(
                            cls, pretrained_model_name_or_path, *args, **kwargs
                        )

                    # Replace the from_pretrained method
                    cls.from_pretrained = patched_from_pretrained
                    _patched_classes.add(cls)
                    print(f"Directly patched {class_name} with completely new method")
                except Exception as e:
                    print(f"Failed to patch {class_name} class: {e}")

    # Also try to find and patch other model classes
    for attr_name in dir(transformers):
        # Skip special attributes and modules
        if attr_name.startswith("_") or attr_name in auto_classes:
            continue

        try:
            attr = getattr(transformers, attr_name)
            # Check if it's a class with a from_pretrained method
            if (
                inspect.isclass(attr)
                and hasattr(attr, "from_pretrained")
                and attr not in _patched_classes
            ):

                # Import these directly to ensure they're accessible in the closure
                from ..utils import download_from_ipfs

                # Store original method
                original_from_pretrained = attr.from_pretrained

                # Define a replacement method that adds IPFS support
                @classmethod
                @functools.wraps(original_from_pretrained.__func__)
                def patched_from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
                    # If it's an IPFS URI, download it first
                    if (
                        pretrained_model_name_or_path
                        and isinstance(pretrained_model_name_or_path, str)
                        and pretrained_model_name_or_path.startswith("ipfs://")
                    ):
                        local_path = download_from_ipfs(pretrained_model_name_or_path)
                        # Use the local path instead
                        return original_from_pretrained.__func__(cls, local_path, *args, **kwargs)

                    # Otherwise, use the original method
                    return original_from_pretrained.__func__(
                        cls, pretrained_model_name_or_path, *args, **kwargs
                    )

                # Replace the from_pretrained method
                attr.from_pretrained = patched_from_pretrained
                _patched_classes.add(attr)
                print(f"Patched {attr_name}")
        except Exception:
            # Ignore any errors
            pass

    print(f"Number of patched classes: {len(_patched_classes)}")
    print("- " + "\n- ".join([cls.__name__ for cls in _patched_classes]))


# Export the patch function
__all__ = ["patch_transformers_classes"]
