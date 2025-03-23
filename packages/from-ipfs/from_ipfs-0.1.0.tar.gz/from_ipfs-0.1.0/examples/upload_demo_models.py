import os

from huggingface_hub import snapshot_download


def download_transformers_model():
    """Download the sentiment analysis model"""
    print("Downloading sentiment analysis model...")
    model_name = "riturajpandey739/gpt2-sentiment-analysis-tweets"

    # Download model and tokenizer
    model_path = snapshot_download(repo_id=model_name, local_dir="./sentiment_model")
    print(f"Model downloaded to: {model_path}")
    return model_path


def download_gguf_model():
    """Download the GGUF model"""
    print("Downloading GGUF model...")
    model_name = "PrunaAI/openai-community-gpt2-GGUF-smashed"

    # Download GGUF file
    model_path = snapshot_download(repo_id=model_name, local_dir="./gguf_model")
    print(f"Model downloaded to: {model_path}")
    return model_path


def main():
    # Create temp directory
    os.makedirs("temp_models", exist_ok=True)

    # Download both models
    transformers_path = download_transformers_model()
    gguf_path = download_gguf_model()

    print("\nModels downloaded successfully!")
    print("\nNext steps:")
    print("1. Install IPFS CLI if not already installed")
    print("2. Run these commands to add models to IPFS:")
    print(f"\nw3 up {transformers_path}")
    print(f"w3 up {gguf_path}")
    print("\nThen update the notebook with the resulting CIDs")


if __name__ == "__main__":
    main()
