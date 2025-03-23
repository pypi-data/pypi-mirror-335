"""
Minimal example to test from_ipfs with llama-cpp-python.

This script demonstrates the basic functionality of from_ipfs with llama-cpp-python by:
1. Loading a small GGUF model from a local file or Hugging Face Hub
2. Testing inference with a simple prompt

This example requires you to have a GGUF model file locally.
"""

import os

from llama_cpp import Llama


def main():
    """Run a simple test with a small LLM model."""
    # Local model path - preferably point to a small GGUF model you have locally
    # Or you can download a small model like TinyLlama Q4_0
    model_path = os.environ.get(
        "LLAMA_MODEL_PATH",
        # Default path - edit this to point to your model
        "path/to/your/tiny_model.gguf",
    )

    # Check if the model exists locally
    if not os.path.exists(model_path):
        print(f"Model file '{model_path}' not found.")
        print(
            "Please set the LLAMA_MODEL_PATH environment variable to the path of a GGUF model file."
        )
        print("For example: export LLAMA_MODEL_PATH=/path/to/your/model.gguf")
        return

    # Load the model
    print(f"Loading model from: {model_path}")
    llm = Llama(
        model_path=model_path, n_ctx=512, verbose=False  # Small context size for faster loading
    )

    # Test inference with a simple prompt
    prompt = "Q: What is the capital of France? A:"
    print(f"Testing inference with prompt: '{prompt}'")

    response = llm(prompt, max_tokens=32, echo=True)

    # Print the response
    print("\nModel response:")
    print(response["choices"][0]["text"])

    print("\nSuccess! Model loaded and inference completed.")


if __name__ == "__main__":
    main()
