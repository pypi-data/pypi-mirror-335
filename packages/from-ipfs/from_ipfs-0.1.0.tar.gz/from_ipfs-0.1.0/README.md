# From IPFS

Use IPFS URIs with Hugging Face `transformers` and llama.cpp library `llama-cpp-python` - easily download, cache, and share ML models using IPFS.

## Overview

`from_ipfs` is a Python package that extends `transformers` and `llama-cpp-python` library to support IPFS (InterPlanetary File System) for model storage and distribution. This allows you to:

- Load models directly from IPFS using `ipfs://` URIs
- Cache models locally for faster access
- Push models to IPFS for decentralized storage and distribution

## Key Features

- **Universal Compatibility**: Works with any class having a `from_pretrained` method, not just predefined Transformers classes
- **Zero-Configuration**: Patches are applied automatically when `transformers` and `Llama` is imported, even if you don't explicitly `import from_ipfs`
- **Dynamic Discovery**: Automatically detects and patches new classes as they are imported
- **Non-Invasive**: Only modifies the necessary methods without changing other functionality

## Installation

You can install from PyPI using pip or uv:

```bash
# With pip
pip install from_ipfs

# With uv
uv pip install from_ipfs

# To include transformers support
pip install "from_ipfs[transformers]"

# To include llama-cpp-python support
pip install "from_ipfs[llama-cpp]"

# To include all dependencies including development tools
pip install "from_ipfs[all,dev]"
```

## Requirements:

- Python 3.8+
- For IPFS interaction (optional):
  - IPFS daemon (`ipfs`) - For local node operations
  - Web3.Storage CLI (`w3`) - For uploading to IPFS via Web3.Storage

## Usage

### Loading models from IPFS

The simplest way to use `from_ipfs` is to install it and use IPFS URIs with `transformers`:

```python
# No explicit import needed! The package automatically patches Transformers
from transformers import AutoModel, AutoTokenizer

# Works with any Transformers class that has from_pretrained
model = AutoModel.from_pretrained("ipfs://QmYourModelCID")
tokenizer = AutoTokenizer.from_pretrained("ipfs://QmYourModelCID")

# Use the model as usual
outputs = model(**tokenizer("Hello world", return_tensors="pt"))
```

Similarly, you can use it with `llama-cpp-python`:

```python
# No explicit import needed! The package automatically patches Llama
from llama_cpp import Llama

# Load a model from IPFS
llm = Llama.from_pretrained(
    repo_id="ipfs://QmYourModelCID",
    filename="model.gguf",  # Specify the GGUF file to load
    verbose=False
)

# Use the model as usual
response = llm("Q: What is the capital of France? A:", max_tokens=32)
print(response["choices"][0]["text"])
```

### Pushing models to IPFS

You can push models to IPFS using the `push_to_ipfs` method that's automatically added to model classes:

```python
from transformers import AutoModel

# Load your model
model = AutoModel.from_pretrained("bert-base-uncased")

# Push to IPFS (automatically added to any model class that has push_to_hub)
cid = model.push_to_ipfs()
print(f"Model uploaded to IPFS: ipfs://{cid}")
```

### CLI Usage

The package includes a command-line interface:

```bash
# Download a model from IPFS
from_ipfs download ipfs://QmYourModelCID

# Download a specific file from an IPFS directory
from_ipfs download ipfs://QmYourModelCID model.gguf

# List cached models
from_ipfs list

# Clear the cache
from_ipfs clear

# Clear a specific model from cache
from_ipfs clear QmYourModelCID

# View current configuration
from_ipfs config
```

## Configuration

The package can be configured using environment variables:

- `FROM_IPFS_CACHE`: Path to the directory where models are cached
  - Default: `~/.cache/from_ipfs`
- `FROM_IPFS_GATEWAYS`: Comma-separated list of IPFS gateways to use
  - Default: `https://cloudflare-ipfs.com/ipfs/,https://gateway.ipfs.io/ipfs/,https://ipfs.io/ipfs/,https://dweb.link/ipfs/`

You can check your current configuration by running:

```bash
# Using the alternative entry point if needed
from_ipfs_alt config
```

Alternatively, you can use the standalone configuration script:

```bash
# Directly run the configuration script
./from_ipfs_config.py
```

## Complete Example: Work with TinyBERT model

Here's a complete example of how to work with a small BERT model via IPFS:

```python
# This example uses a small model called TinyBERT
# First, let's download it from Hugging Face and push to IPFS

import transformers
from pathlib import Path
import os
import subprocess
import re

# 1. Download the model from Hugging Face
model_name = "prajjwal1/bert-tiny"
model = transformers.AutoModel.from_pretrained(model_name)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

# 2. Save it locally
save_dir = Path("./tiny-bert")
os.makedirs(save_dir, exist_ok=True)
model.save_pretrained(save_dir)
tokenizer.save_pretrained(save_dir)

# 3. Upload to IPFS using w3 CLI tool
result = subprocess.run(
    ["w3", "up", str(save_dir)],
    check=True, capture_output=True, text=True
)
output = result.stdout
cid = re.search(r'(Qm[a-zA-Z0-9]{44}|bafy[a-zA-Z0-9]{44})', output).group(0)
print(f"Model uploaded to IPFS: ipfs://{cid}")

# 4. Now let's load it back from IPFS
model_from_ipfs = transformers.AutoModel.from_pretrained(f"ipfs://{cid}")
tokenizer_from_ipfs = transformers.AutoTokenizer.from_pretrained(f"ipfs://{cid}")

# 5. Use the model
inputs = tokenizer_from_ipfs("Hello, world!", return_tensors="pt")
outputs = model_from_ipfs(**inputs)
print(f"Output shape: {outputs.last_hidden_state.shape}")
```

## Complete Example: Work with TinyLlama model

Here's a complete example for working with a small LLM via IPFS:

```python
# This example uses TinyLlama, a small 1.1B parameter LLM
import os
import subprocess
import re
from pathlib import Path
from llama_cpp import Llama

# 1. Download the model
model_url = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
model_filename = "tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
save_dir = Path("./tiny-llama")
model_path = save_dir / model_filename

# Create directory
os.makedirs(save_dir, exist_ok=True)

# Download if not exists
if not model_path.exists():
    subprocess.run(["curl", "-L", model_url, "-o", str(model_path)], check=True)

# 2. Upload to IPFS
result = subprocess.run(
    ["w3", "up", str(save_dir)],
    check=True, capture_output=True, text=True
)
output = result.stdout
cid = re.search(r'(Qm[a-zA-Z0-9]{44}|bafy[a-zA-Z0-9]{44})', output).group(0)
print(f"Model uploaded to IPFS: ipfs://{cid}")

# 3. Load from IPFS
llm = Llama.from_pretrained(
    repo_id=f"ipfs://{cid}",
    filename=model_filename,
    verbose=False
)

# 4. Use the model
response = llm("Q: What is the capital of France? A:", max_tokens=32)
print(f"Response: {response['choices'][0]['text']}")
```

## How It Works

`from_ipfs` works by:

1. Installing an import hook that patches classes with a `from_pretrained` method
2. Recognizing IPFS URIs (starting with `ipfs://`) passed to `from_pretrained` methods
3. Downloading models from IPFS gateways when an IPFS URI is provided
4. Caching models locally for faster access
5. Adding a `push_to_ipfs` method to models for easy uploading

## Uploading to IPFS

To upload models to IPFS, you'll need to install the Web3.Storage CLI:

```bash
npm install -g @web3-storage/w3cli
```

Then validate your email:

```bash
w3 login your-email@example.com
```

Create a space for storing your models:

```bash
w3 space create Models
```

Upload a model directory:

```bash
w3 up ./your-model-directory/
```

## Retrieving from IPFS via Kubo

To download from IPFS using the local IPFS daemon:

1. Install the [Kubo IPFS daemon](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions)

2. Start the daemon:

```bash
ipfs daemon
```

3. Download a model:

```bash
ipfs get QmYourModelCID -o ./your-model/
```

## License

This project is licensed under the MIT License.

## Troubleshooting

### CLI Command Not Found

If you encounter issues with the `from_ipfs` command not being found or not recognizing certain subcommands:

1. Try using the alternative entry point:

   ```bash
   from_ipfs_alt <command>
   ```

2. Or use the standalone configuration script for checking configuration:

   ```bash
   ./from_ipfs_config.py
   ```

3. Ensure the package is installed correctly:

   ```bash
   pip install -e .
   ```

4. Check if the entry points are properly registered:
   ```bash
   pip show from-ipfs
   ```

### IPFS Gateway Issues

If you have trouble downloading from IPFS:

1. Check your internet connection
2. Verify the IPFS CID is correct
3. Try specifying alternate gateways:
   ```bash
   FROM_IPFS_GATEWAYS="https://your-gateway.com/ipfs/,https://another-gateway.com/ipfs/" from_ipfs download ipfs://QmYourModelCID
   ```

### Cache Issues

If you encounter caching problems:

1. Clear the cache completely:

   ```bash
   from_ipfs clear
   ```

2. Specify a different cache directory:
   ```bash
   FROM_IPFS_CACHE="/path/to/cache" from_ipfs download ipfs://QmYourModelCID
   ```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on how to contribute to this project.
