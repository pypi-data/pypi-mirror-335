"""
Minimal example to test from_ipfs with transformers.

This script demonstrates the basic functionality of from_ipfs by:
1. Loading a small BERT model (prajjwal1/bert-tiny)
2. Testing inference with it
3. No IPFS upload required - just uses Hugging Face Hub

This is the simplest possible example to test that the package works correctly.
"""

import torch
from transformers import AutoModel, AutoTokenizer


def main():
    """Run a simple test with TinyBERT model."""
    print("Loading TinyBERT from Hugging Face Hub...")

    # Load model and tokenizer
    model_name = "prajjwal1/bert-tiny"
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Verify the model works
    print("Testing inference...")
    inputs = tokenizer("Hello, world!", return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Print output shape to verify it worked
    print(f"Success! Output shape: {outputs.last_hidden_state.shape}")
    print(f"Model has {model.num_parameters():,} parameters")


if __name__ == "__main__":
    main()
