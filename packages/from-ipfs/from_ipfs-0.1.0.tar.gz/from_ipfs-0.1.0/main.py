"""
Main module for from_ipfs package.

This is a simple example of how to use the package.
"""

from from_ipfs import __version__
from from_ipfs.cli import main


def show_info():
    """Show package info and usage."""
    print(f"from_ipfs v{__version__}")
    print("Use IPFS URIs with Hugging Face transformers and llama-cpp-python")
    print("\nExamples:")
    print("  1. Import transformers and use it with IPFS URIs:")
    print("     from transformers import AutoModel")
    print("     model = AutoModel.from_pretrained('ipfs://QmYourModelCID')")
    print("\n  2. Import llama_cpp and use it with IPFS URIs:")
    print("     from llama_cpp import Llama")
    print("     llm = Llama.from_pretrained('ipfs://QmYourModelCID', filename='model.gguf')")
    print("\n  3. Use the CLI to download models:")
    print("     from_ipfs download ipfs://QmYourModelCID")
    print("     from_ipfs list")
    print("     from_ipfs clear")


if __name__ == "__main__":
    show_info()
    main()
