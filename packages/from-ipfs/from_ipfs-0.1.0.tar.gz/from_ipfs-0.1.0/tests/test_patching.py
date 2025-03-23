# Import from_ipfs first to ensure patching happens
import from_ipfs

# Define a simple mock for download_from_ipfs
download_calls = []
original_download = from_ipfs.utils.download_from_ipfs


def mock_download_from_ipfs(uri, filename=None):
    print(f"Mock downloading from IPFS URI: {uri}")
    download_calls.append(uri)
    return "/tmp/mock_model_path"


# Track calls to patched methods
def test_transformers_patching():
    """Test if transformers.AutoModel.from_pretrained detects IPFS URIs."""
    print("\nTesting transformers patching:")

    # Use an IPFS URI

    # Replace download_from_ipfs for testing
    from_ipfs.utils.download_from_ipfs = mock_download_from_ipfs

    # Import transformers after patching
    from transformers import AutoModel

    # Check if the method includes download_from_ipfs code
    patched_method = AutoModel.from_pretrained
    patched_code = patched_method.__func__.__code__.co_names

    print(f"AutoModel.from_pretrained method names: {patched_code}")

    if "startswith" in patched_code:
        print("✅ AutoModel.from_pretrained appears to be patched to handle IPFS URIs")
    else:
        print("❌ AutoModel.from_pretrained does not seem to be patched for IPFS")


def test_llama_cpp_patching():
    """Test if llama_cpp.Llama.from_pretrained detects IPFS URIs."""
    print("\nTesting llama_cpp patching:")

    # Import llama_cpp after patching
    try:
        import llama_cpp

        # Check if the method includes download_from_ipfs code
        patched_method = llama_cpp.Llama.from_pretrained
        patched_code = patched_method.__func__.__code__.co_names

        print(f"Llama.from_pretrained method names: {patched_code}")

        if "startswith" in patched_code:
            print("✅ llama_cpp.Llama.from_pretrained appears to be patched to handle IPFS URIs")
        else:
            print("❌ llama_cpp.Llama.from_pretrained does not seem to be patched for IPFS")
    except ImportError:
        print("Skipping llama_cpp tests as it is not installed.")


# Run the tests
test_transformers_patching()
test_llama_cpp_patching()

# Restore original download function
from_ipfs.utils.download_from_ipfs = original_download

print("\nPatching test complete!")
