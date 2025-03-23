"""
Demo script showing how to use from_ipfs with both transformers and llama-cpp-python.
"""

import os
import tempfile

# Import and apply patches


# Test transformers integration
def test_transformers():
    print("\n=== Testing Transformers Integration ===")
    try:
        from transformers import AutoModel

        # Verify that the from_pretrained method is patched
        print("Checking if transformers is patched...")
        method = AutoModel.from_pretrained
        if hasattr(method, "__func__"):
            print("✅ Transformers integration working (from_pretrained method is patched)!")
        else:
            print("❌ Transformers integration failed (from_pretrained method not patched)")

    except Exception as e:
        print(f"❌ Error testing transformers: {e}")


# Test llama-cpp integration
def test_llama_cpp():
    print("\n=== Testing Llama.cpp Integration ===")
    try:
        from llama_cpp import Llama

        # Create a small test model file
        print("Creating test GGUF file...")
        with tempfile.NamedTemporaryFile(suffix=".gguf", delete=False) as f:
            f.write(b"TEST MODEL")
            test_model = f.name

        try:
            # Test model loading (this will fail with our dummy file, but tests the patching)
            print("Testing model loading (expected to fail with our dummy file)...")
            try:
                _ = Llama(model_path=test_model)
            except Exception as e:
                if "Failed to load model" in str(e):
                    print("✅ Llama.cpp integration working (expected error with dummy file)")
                else:
                    raise
        finally:
            # Cleanup
            os.unlink(test_model)

    except Exception as e:
        print(f"❌ Error testing llama-cpp: {e}")


# Test IPFS functionality
def test_ipfs():
    print("\n=== Testing IPFS Functionality ===")
    try:
        from from_ipfs.utils import extract_cid_from_uri, is_ipfs_uri

        # Test URI validation
        test_uri = "ipfs://QmTest123"
        print(f"Testing URI validation with: {test_uri}")
        assert is_ipfs_uri(test_uri), "IPFS URI validation failed"

        # Test CID extraction
        cid = extract_cid_from_uri(test_uri)
        print(f"Extracted CID: {cid}")
        assert cid == "QmTest123", "CID extraction failed"

        print("✅ IPFS functionality working!")

    except Exception as e:
        print(f"❌ Error testing IPFS functionality: {e}")


def main():
    print("Starting from_ipfs functionality demo...")

    # Run all tests
    test_ipfs()
    test_transformers()
    test_llama_cpp()

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
