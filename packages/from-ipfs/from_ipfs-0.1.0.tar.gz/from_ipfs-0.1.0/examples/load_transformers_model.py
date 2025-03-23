"""
Example script for loading a Hugging Face Transformers model from IPFS.

This script shows how to use the from_ipfs package to load a model from IPFS.

Prerequisites:
1. Install the package: pip install from_ipfs transformers torch
2. If the model isn't already on IPFS, you'll need to upload it first.

For this example, we'll use a small model called TinyBERT,
which is a distilled version of BERT that's much smaller but still useful.
"""

import os
import subprocess
from pathlib import Path

# Define the model name and IPFS CID (example - will be replaced with real CID later)
MODEL_NAME = "prajjwal1/bert-tiny"
CID = None  # Will be set later

# Define the path to save the model locally (for uploading to IPFS)
SAVE_DIR = Path("./tiny-bert")


def download_and_upload_model():
    """Download a model from Hugging Face and upload it to IPFS."""
    global CID

    print(f"Downloading {MODEL_NAME} from Hugging Face...")

    # First, import transformers to make sure from_ipfs is applied
    import transformers

    # Then load the model
    model = transformers.AutoModel.from_pretrained(MODEL_NAME)
    tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_NAME)

    # Save the model locally
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Saving model to {SAVE_DIR}...")
    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)

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

    # Import transformers (from_ipfs will be applied automatically)
    import transformers

    # Load the model from IPFS
    model = transformers.AutoModel.from_pretrained(f"ipfs://{CID}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(f"ipfs://{CID}")

    print("Model loaded successfully!")

    # Test the model with a simple input
    inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
    outputs = model(**inputs)

    print(f"Model output shape: {outputs.last_hidden_state.shape}")
    print("Model loaded and working correctly!")


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
