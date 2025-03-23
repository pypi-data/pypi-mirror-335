"""
Module for patching llama-cpp-python with IPFS support.
"""

import functools
import os

from .utils import download_from_ipfs


def apply_patch():
    """Apply the IPFS patches to llama_cpp classes."""
    try:
        import llama_cpp

        # Save the original init method
        original_init = llama_cpp.Llama.__init__

        @functools.wraps(original_init)
        def patched_init(self, model_path: str, *args, **kwargs):
            """Patched init method that supports IPFS URIs."""
            if isinstance(model_path, str) and model_path.startswith("ipfs://"):
                print(f"Downloading model from IPFS: {model_path}")
                local_path = download_from_ipfs(model_path)
                model_path = os.path.join(local_path, os.path.basename(model_path))

            # Call the original init method with the local path
            return original_init(self, model_path, *args, **kwargs)

        # Replace the original init method with the patched one
        llama_cpp.Llama.__init__ = patched_init

        # Add from_pretrained method to Llama class
        @classmethod
        def from_pretrained(cls, pretrained_model_name_or_path: str, **kwargs):
            """
            Load a model from a pretrained model name or path.

            Args:
                pretrained_model_name_or_path: The model name/path or IPFS URI
                **kwargs: Additional arguments to pass to the Llama constructor

            Returns:
                Llama: A Llama instance with the model loaded
            """
            if isinstance(
                pretrained_model_name_or_path, str
            ) and pretrained_model_name_or_path.startswith("ipfs://"):
                print(f"Downloading model from IPFS: {pretrained_model_name_or_path}")
                local_path = download_from_ipfs(pretrained_model_name_or_path)
                model_path = os.path.join(
                    local_path, os.path.basename(pretrained_model_name_or_path)
                )
                return cls(model_path=model_path, **kwargs)

            # If not an IPFS URI, try to load from HuggingFace Hub
            try:
                from huggingface_hub import HfFileSystem, hf_hub_download

                fs = HfFileSystem()
                files = fs.ls(pretrained_model_name_or_path, detail=False)
                gguf_files = [f for f in files if str(f).endswith(".gguf")]

                if not gguf_files:
                    raise ValueError(f"No .gguf files found in {pretrained_model_name_or_path}")

                model_path = gguf_files[0]
                local_path = hf_hub_download(
                    repo_id=pretrained_model_name_or_path, filename=os.path.basename(model_path)
                )

                return cls(model_path=local_path, **kwargs)
            except ImportError as e:
                raise ValueError(
                    "Could not load model. For HuggingFace Hub support, install huggingface_hub."
                ) from e

        # Add the method to the Llama class
        llama_cpp.Llama.from_pretrained = from_pretrained
        print("Patched Llama class with from_pretrained method")

    except ImportError:
        print("llama-cpp-python not installed, skipping patching")
        return
