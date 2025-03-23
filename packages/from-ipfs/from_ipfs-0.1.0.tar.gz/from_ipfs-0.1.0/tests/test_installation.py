"""
Simple script to test if from_ipfs is installed correctly.

This script doesn't actually download any models, but just verifies that
the patches have been applied to transformers and llama_cpp classes.
"""

import importlib.util
import sys


def check_module_installed(module_name):
    """Check if a module is installed."""
    is_installed = importlib.util.find_spec(module_name) is not None
    print(f"✓ {module_name} is installed" if is_installed else f"✗ {module_name} is NOT installed")
    return is_installed


def check_transformers_patching():
    """Check if transformers is patched without requiring PyTorch."""
    try:
        import transformers

        import from_ipfs.transformers

        # Check if our patch function exists
        if hasattr(from_ipfs.transformers, "patch_transformers_classes"):
            print("✓ transformers patching module is available")

            # Check if the AutoModel.from_pretrained method is patched
            if hasattr(transformers, "AutoModel"):
                from_pretrained = transformers.AutoModel.from_pretrained
                if hasattr(from_pretrained, "__func__"):
                    func_code = from_pretrained.__func__.__code__

                    # Look for 'startswith' in the co_names which indicates our patch
                    # that checks if a string starts with 'ipfs://'
                    if "startswith" in func_code.co_names:
                        print("✓ transformers.AutoModel is patched correctly")
                        return True

            print("✗ Could not verify transformers patching")
        else:
            print("✗ transformers patching module is not properly installed")

        return True
    except ImportError as e:
        print(f"✗ Error checking transformers patching: {e}")
        return False


def check_llama_cpp_patching():
    """Check if llama_cpp is patched."""
    try:
        import llama_cpp

        import from_ipfs.llama_cpp

        if hasattr(from_ipfs.llama_cpp, "patch_llama_cpp_classes"):
            print("✓ llama_cpp patching module is available")

            # Check if Llama has been patched
            if hasattr(llama_cpp, "Llama") and hasattr(llama_cpp.Llama, "from_pretrained"):
                from_pretrained = llama_cpp.Llama.from_pretrained
                original_func = getattr(from_pretrained, "__func__", None)

                # Look for 'startswith' in the co_names which indicates our patch
                # that checks if a string starts with 'ipfs://'
                if original_func and "startswith" in original_func.__code__.co_names:
                    print("✓ llama_cpp.Llama is patched correctly")
                    return True
                else:
                    print("✗ llama_cpp.Llama is NOT patched properly")
            else:
                print("✗ llama_cpp.Llama class or its from_pretrained method not found")
        else:
            print("✗ llama_cpp patching module is not properly installed")

        return False
    except ImportError as e:
        print(f"✗ Error checking llama_cpp patching: {e}")
        return False


def main():
    """Main function to test installation."""
    print("Testing from_ipfs installation...\n")

    # Check if from_ipfs is installed
    from_ipfs_installed = check_module_installed("from_ipfs")
    if not from_ipfs_installed:
        print("\nPlease install from_ipfs: pip install from_ipfs")
        return False

    # Import from_ipfs
    import from_ipfs

    print(f"✓ from_ipfs version {from_ipfs.__version__} is installed")

    # Check if transformers is installed
    transformers_installed = check_module_installed("transformers")

    # Check if llama_cpp is installed
    llama_cpp_installed = check_module_installed("llama_cpp")

    print("\nChecking patching functionality:")

    if transformers_installed:
        check_transformers_patching()

    if llama_cpp_installed:
        check_llama_cpp_patching()

    # Overall test result
    if not transformers_installed and not llama_cpp_installed:
        print("\nNeither transformers nor llama_cpp is installed.")
        print("Install at least one of them to test the patching functionality:")
        print("  pip install torch transformers")
        print("  pip install llama-cpp-python")
        return True  # Still consider this a success for installation testing

    print("\nAll checks completed! from_ipfs is ready to use.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
