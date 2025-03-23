"""
Example script for loading a llama-cpp model from IPFS.

This script shows how to use the from_ipfs package to load a model from IPFS.

Prerequisites:
1. Install the package: pip install "from_ipfs[llama-cpp]"
2. If the model isn't already on IPFS, you'll need to upload it first.

For this example, we'll use a small GGUF model like TinyLlama or other small model.
"""

import os
import subprocess
from pathlib import Path

# Define the model filename and IPFS CID (example - will be replaced with real CID later)
MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
CID = None  # Will be set later

# Define the path to save the model locally (for uploading to IPFS)
SAVE_DIR = Path("./tiny-llama")
MODEL_PATH = SAVE_DIR / MODEL_FILENAME


def download_and_upload_model():
    """Download a model and upload it to IPFS."""
    global CID

    # Create the directory
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Download the model if it doesn't exist
    if not MODEL_PATH.exists():
        print(f"Downloading {MODEL_FILENAME} from {MODEL_URL}...")

        try:
            # Using wget for convenience
            subprocess.run(["curl", "-L", MODEL_URL, "-o", str(MODEL_PATH)], check=True)
            print(f"Downloaded to {MODEL_PATH}")
        except subprocess.SubprocessError:
            print("Failed to download the model. Make sure curl is installed.")
            print("You can manually download the model from:")
            print(MODEL_URL)
            print(f"And save it to: {MODEL_PATH}")
            return
    else:
        print(f"Model already exists at {MODEL_PATH}")

    # Upload to IPFS
    try:
        print("Uploading to IPFS...")
        result = subprocess.run(
            ["w3", "up", str(SAVE_DIR)], check=True, capture_output=True, text=True
        )

        # Extract CID from output
        import re

        output = result.stdout
        match = re.search(r"(Qm[a-zA-Z0-9]{44}|bafy[a-zA-Z0-9]{44})", output)
        if match:
            CID = match.group(0)
            print(f"Uploaded to IPFS: ipfs://{CID}")
        else:
            print("Failed to extract CID from output")
            print(f"Output: {output}")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error uploading to IPFS: {e}")
        print("Make sure w3 is installed: npm install -g @web3-storage/w3cli")
        print("And that you're logged in: w3 login your-email@example.com")


def load_from_ipfs():
    """Load the model from IPFS."""
    if not CID:
        print("No CID available. Run download_and_upload_model() first or set CID manually.")
        return

    print(f"Loading model from IPFS: ipfs://{CID}")

    try:
        # Import llama_cpp (from_ipfs will be applied automatically)
        from llama_cpp import Llama

        # Load the model from IPFS
        llm = Llama.from_pretrained(repo_id=f"ipfs://{CID}", filename=MODEL_FILENAME, verbose=False)

        print("Model loaded successfully!")

        # Test the model with a simple prompt
        response = llm("Q: What is the capital of France? A:", max_tokens=32)
        print("\nTest prompt: What is the capital of France?")
        print(f"Response: {response['choices'][0]['text']}")

        print("\nModel loaded and working correctly!")

    except ImportError:
        print("Failed to import llama_cpp. Make sure it's installed:")
        print("pip install llama-cpp-python")
    except Exception as e:
        print(f"Error loading model: {e}")


if __name__ == "__main__":
    # If we don't have a CID yet, upload the model to IPFS
    if CID is None:
        # Check if w3 is installed
        try:
            subprocess.run(["w3", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("w3 CLI tool not found.")
            print("Install it with: npm install -g @web3-storage/w3cli")
            print("Then run: w3 login your-email@example.com")
            print("And: w3 space create Models")
            print("\nFor this example, we'll set a dummy CID:")
            CID = "QmExampleCID"  # This is just a dummy CID for demonstration
        else:
            download_and_upload_model()

    # Load the model from IPFS
    load_from_ipfs()
