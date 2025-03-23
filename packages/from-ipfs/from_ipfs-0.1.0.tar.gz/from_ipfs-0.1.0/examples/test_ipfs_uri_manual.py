"""
Test IPFS URI handling with a mock IPFS model.

This script demonstrates how from_ipfs handles IPFS URIs by:
1. Creating a mock model directory
2. Showing how the library processes IPFS URIs
3. No need to actually use IPFS in this example

This is useful for testing that the from_ipfs package handles URIs correctly
without requiring an actual IPFS connection.
"""

import json
import os

from transformers import AutoModel, AutoTokenizer

# Import from_ipfs to ensure patching is applied
import from_ipfs
from from_ipfs.utils import download_from_ipfs, is_ipfs_uri


def create_mock_model_in_cache():
    """Create a mock model directory in the from_ipfs cache."""
    # Get the cache directory from from_ipfs
    cache_dir = from_ipfs.CACHE_DIR

    # Create a test CID
    test_cid = "QmTestModelCID123456789"

    # Full path for this model in cache
    model_cache_path = os.path.join(cache_dir, test_cid)

    # Only create if it doesn't already exist
    if os.path.exists(model_cache_path):
        print(f"Mock model already exists at: {model_cache_path}")
        return test_cid

    # Create the directory
    os.makedirs(model_cache_path, exist_ok=True)

    # Create a small mock model (just enough to verify loading)
    # Create config.json
    config = {
        "architectures": ["BertModel"],
        "model_type": "bert",
        "hidden_size": 4,
        "intermediate_size": 16,
        "num_attention_heads": 1,
        "num_hidden_layers": 1,
        "vocab_size": 100,
    }
    with open(os.path.join(model_cache_path, "config.json"), "w") as f:
        json.dump(config, f)

    # Create tokenizer_config.json
    tokenizer_config = {
        "model_type": "bert",
        "special_tokens_map_file": "special_tokens_map.json",
        "tokenizer_class": "BertTokenizer",
    }
    with open(os.path.join(model_cache_path, "tokenizer_config.json"), "w") as f:
        json.dump(tokenizer_config, f)

    # Create special_tokens_map.json
    special_tokens = {
        "cls_token": "[CLS]",
        "mask_token": "[MASK]",
        "pad_token": "[PAD]",
        "sep_token": "[SEP]",
        "unk_token": "[UNK]",
    }
    with open(os.path.join(model_cache_path, "special_tokens_map.json"), "w") as f:
        json.dump(special_tokens, f)

    # Create vocab.txt (minimal)
    with open(os.path.join(model_cache_path, "vocab.txt"), "w") as f:
        vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "hello", "world", "test", ".", "!"]
        f.write("\n".join(vocab))

    print(f"Created mock model at: {model_cache_path}")
    return test_cid


def test_ipfs_uri_handling():
    """Test from_ipfs URI handling with a mock model."""
    # Create a mock model in cache
    test_cid = create_mock_model_in_cache()

    # Create an IPFS URI for this model
    ipfs_uri = f"ipfs://{test_cid}"

    # Check if from_ipfs correctly identifies this as an IPFS URI
    print(f"Is '{ipfs_uri}' an IPFS URI? {is_ipfs_uri(ipfs_uri)}")

    # Get the local path for this URI (should be in cache already)
    local_path = download_from_ipfs(ipfs_uri)
    print(f"Local path for {ipfs_uri}: {local_path}")

    # Now try loading the model using transformers with the IPFS URI
    print("\nTrying to load tokenizer from IPFS URI...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(ipfs_uri)
        print("Success! Tokenizer loaded successfully")

        # Test tokenizer
        tokens = tokenizer("hello world!")
        print(f"Tokenized 'hello world!': {tokens}")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")

    print("\nTrying to load model from IPFS URI...")
    try:
        AutoModel.from_pretrained(ipfs_uri)
        print("Success! Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")


if __name__ == "__main__":
    test_ipfs_uri_handling()
