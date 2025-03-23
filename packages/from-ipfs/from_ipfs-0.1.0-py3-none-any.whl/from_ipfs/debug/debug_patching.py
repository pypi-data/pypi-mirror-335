"""
Debug script to test the patching mechanism directly.
"""


def main():
    print("Importing from_ipfs...")
    import from_ipfs

    print("\nImporting transformers and checking for patching...")
    from transformers import AutoModel

    # Check if patch functions exist
    print("\nChecking if patch functions exist:")
    print(f"- from_ipfs.patch_transformers exists: {hasattr(from_ipfs, 'patch_transformers')}")

    # Call patching directly
    print("\nCalling patch_transformers directly...")
    from_ipfs.patch_transformers()

    # Import and call the patching function directly
    print("\nImporting and calling patch_all_transformers_classes directly...")
    from from_ipfs.transformers import _patched_classes, patch_all_transformers_classes

    patch_all_transformers_classes()

    # Check the patched classes
    print(f"\nNumber of patched classes: {len(_patched_classes)}")
    for cls in _patched_classes:
        print(f"- {cls.__name__}")

    # Try manual patching
    print("\nManually patching AutoModel...")
    from from_ipfs.patcher import patch_class_with_ipfs_support

    patch_class_with_ipfs_support(AutoModel)

    # Check if from_pretrained is now patched
    print("\nChecking if AutoModel.from_pretrained is patched:")

    from_pretrained = AutoModel.from_pretrained
    func = from_pretrained.__func__
    code = func.__code__

    print(f"- Has download_from_ipfs in co_names: {'download_from_ipfs' in code.co_names}")
    print(f"- Co_names: {code.co_names}")

    # Try llama_cpp
    print("\nChecking llama_cpp patching:")
    try:
        import llama_cpp

        print("- llama_cpp imported successfully")

        from from_ipfs.llama_cpp import patch_llama_cpp_classes

        patch_llama_cpp_classes()

        from_pretrained = llama_cpp.Llama.from_pretrained
        func = from_pretrained.__func__
        code = func.__code__

        print(f"- Has download_from_ipfs in co_names: {'download_from_ipfs' in code.co_names}")
    except Exception as e:
        print(f"- Error with llama_cpp: {e}")

    print("\nDebugging complete!")


if __name__ == "__main__":
    main()
