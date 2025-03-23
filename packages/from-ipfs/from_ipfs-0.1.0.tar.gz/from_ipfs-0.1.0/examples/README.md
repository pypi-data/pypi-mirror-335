# from_ipfs Examples

This directory contains example scripts to demonstrate the usage of the `from_ipfs` package.

## Setup

Before running the examples, make sure you have installed the package:

```bash
# Install the package with all dependencies
pip install "from_ipfs[all,dev]"

# Or install with specific dependencies
pip install "from_ipfs[transformers]"  # Just for transformers support
pip install "from_ipfs[llama-cpp]"     # Just for llama-cpp-python support
```

## Available Examples

### 1. Minimal Examples

These examples demonstrate the basic functionality without requiring IPFS:

- [`test_minimal_transformers.py`](test_minimal_transformers.py): Simple example loading a TinyBERT model from Hugging Face.

  ```bash
  python examples/test_minimal_transformers.py
  ```

- [`test_minimal_llama.py`](test_minimal_llama.py): Simple example using llama-cpp-python with a local GGUF model.
  ```bash
  # Set the path to your GGUF model file first
  export LLAMA_MODEL_PATH=/path/to/your/model.gguf
  python examples/test_minimal_llama.py
  ```

### 2. IPFS URI Handling

- [`test_ipfs_uri_manual.py`](test_ipfs_uri_manual.py): Demonstrates how IPFS URIs are handled without requiring an actual IPFS connection.
  ```bash
  python examples/test_ipfs_uri_manual.py
  ```

### 3. CLI Examples

- [`test_cli.py`](test_cli.py): Demonstrates the CLI commands provided by the package.

  ```bash
  python examples/test_cli.py
  ```

- [`test_config_cmd.py`](test_config_cmd.py): Tests the new `config` command that shows current environment settings.
  ```bash
  python examples/test_config_cmd.py
  ```

### 4. Complete Examples

- [`load_transformers_model.py`](load_transformers_model.py): Complete example showing how to download a model from Hugging Face, upload it to IPFS, and load it back from IPFS.

  ```bash
  python examples/load_transformers_model.py
  ```

- [`load_llama_cpp_model.py`](load_llama_cpp_model.py): Complete example showing how to download a GGUF model, upload it to IPFS, and load it back from IPFS.
  ```bash
  python examples/load_llama_cpp_model.py
  ```

## Requirements for IPFS Examples

For examples that interact with IPFS, you'll need:

1. **Web3.Storage CLI** for uploading models to IPFS:

   ```bash
   npm install -g @web3-storage/w3cli
   w3 login your-email@example.com
   w3 space create Models
   ```

2. **Local IPFS node** (optional) for downloading models from IPFS:
   - Install [Kubo IPFS daemon](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions)
   - Start the daemon: `ipfs daemon`

## Troubleshooting

- If you encounter issues with the examples, make sure you have installed all the required dependencies.
- For GGUF model examples, you need to have a GGUF model file locally. You can download a small one from Hugging Face like [TinyLlama](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF).
- The IPFS features require either a local IPFS node or access to IPFS gateways.
- If you encounter recursion errors when loading from IPFS, ensure you're using the latest version of the library which includes fixes for this issue.

## CLI Commands

The `from_ipfs` CLI includes the following commands:

```bash
# Show help
from_ipfs --help

# Show version
from_ipfs --version

# Download a model from IPFS
from_ipfs download ipfs://QmYourModelCID

# Download a specific file from an IPFS CID
from_ipfs download ipfs://QmYourModelCID filename.gguf

# List all cached models
from_ipfs list

# Show current configuration (cache path, gateways)
from_ipfs config

# Clear all cached models
from_ipfs clear

# Clear a specific model from cache
from_ipfs clear QmYourModelCID
```
