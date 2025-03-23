"""
Integration with llama-cpp-python.
"""

import inspect
import sys
from types import ModuleType
from typing import Any, List, Set, Type

from ..patcher import patch_class_with_ipfs_support

# Set to track classes we've already patched
_patched_classes: Set[Type[Any]] = set()


def find_llama_classes_with_from_pretrained(module: ModuleType) -> List[Type[Any]]:
    """
    Find all Llama classes in a module that have a from_pretrained classmethod.

    Args:
        module: The module to search

    Returns:
        List[Type[Any]]: List of classes with from_pretrained
    """
    classes: List[Type[Any]] = []

    for _name, obj in inspect.getmembers(module):
        # Only consider classes
        if not inspect.isclass(obj):
            continue

        # Check if the class has a from_pretrained classmethod
        if hasattr(obj, "from_pretrained") and isinstance(obj.from_pretrained, classmethod):
            classes.append(obj)

    return classes


def patch_llama_module(module: ModuleType) -> None:
    """
    Patch all Llama classes in a module that have a from_pretrained method.

    Args:
        module: The module to patch
    """
    classes = find_llama_classes_with_from_pretrained(module)

    for cls in classes:
        if cls not in _patched_classes:
            patch_class_with_ipfs_support(cls)
            _patched_classes.add(cls)
            print(f"Patched {cls.__name__}")


def patch_llama_cpp_classes() -> None:
    """
    Patch all llama-cpp-python classes that have a from_pretrained method.
    """
    # Check if llama_cpp is imported
    if "llama_cpp" not in sys.modules:
        print("llama_cpp not in sys.modules")
        return

    llama_cpp = sys.modules["llama_cpp"]

    # Directly patch the Llama class
    if hasattr(llama_cpp, "Llama"):
        Llama = llama_cpp.Llama
        if hasattr(Llama, "from_pretrained") and Llama not in _patched_classes:
            try:
                # Import the necessary utilities
                import functools

                from ..utils import download_from_ipfs

                # Store original method
                original_from_pretrained = Llama.from_pretrained

                # Define a replacement method that adds IPFS support with explicit startswith check
                @classmethod
                @functools.wraps(original_from_pretrained.__func__)
                def patched_llama_from_pretrained(cls, repo_id, *, filename=None, **kwargs):
                    # Use an explicit string check for IPFS URIs to make it visible in code inspection
                    if isinstance(repo_id, str) and repo_id.startswith("ipfs://"):
                        print(f"Downloading model from IPFS: {repo_id}")
                        local_path = download_from_ipfs(repo_id, filename)
                        # Use the local path instead - filename is now None as it's handled by download_from_ipfs
                        return original_from_pretrained.__func__(
                            cls, local_path, filename=None, **kwargs
                        )

                    # Otherwise, use the original method
                    return original_from_pretrained.__func__(
                        cls, repo_id, filename=filename, **kwargs
                    )

                # Replace the from_pretrained method
                Llama.from_pretrained = patched_llama_from_pretrained
                _patched_classes.add(Llama)
                print("Directly patched Llama class with completely new method")
            except Exception as e:
                print(f"Failed to patch Llama class: {e}")

    # Patch any other llama_cpp modules
    patch_llama_module(llama_cpp)

    # Patch all submodules
    for name, module in list(sys.modules.items()):
        if name.startswith("llama_cpp.") and isinstance(module, ModuleType):
            patch_llama_module(module)

    # Add an import hook to patch newly imported modules
    import importlib.abc
    import importlib.machinery

    class LlamaCppImportHook(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            return None

        def find_module(self, fullname, path):
            return None

        def exec_module(self, module):
            pass

        def load_module(self, fullname):
            module = importlib.import_module(fullname)

            # If this is a llama_cpp module, patch it
            if fullname.startswith("llama_cpp."):
                patch_llama_module(module)

            return module

    # Register the import hook
    sys.meta_path.insert(0, LlamaCppImportHook())
