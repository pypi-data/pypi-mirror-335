import tempfile
import unittest

import llama_cpp

# Then import the libraries we want to test
import transformers

# First import from_ipfs to ensure patches are applied


class TestIPFSIntegration(unittest.TestCase):
    """Test that patching transformers and llama_cpp to handle IPFS URIs works."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempdir_path = self.tempdir.name

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tempdir.cleanup()

    def test_transformers_is_patched(self):
        """Check if transformers is patched to handle IPFS URIs."""
        # Check if the AutoModel.from_pretrained method is patched
        if hasattr(transformers, "AutoModel"):
            from_pretrained = transformers.AutoModel.from_pretrained
            if hasattr(from_pretrained, "__func__"):
                func_code = from_pretrained.__func__.__code__

                # Look for 'startswith' in the co_names which indicates our patch
                # that checks if a string starts with 'ipfs://'
                self.assertIn(
                    "startswith",
                    func_code.co_names,
                    "AutoModel.from_pretrained doesn't check for IPFS URIs",
                )
                print("Patched transformers with IPFS support")
                return

        self.fail("Could not verify transformers patching")

    def test_llama_cpp_is_patched(self):
        """Check if llama_cpp is patched to handle IPFS URIs."""
        # Check if Llama has been patched
        if hasattr(llama_cpp, "Llama") and hasattr(llama_cpp.Llama, "from_pretrained"):
            from_pretrained = llama_cpp.Llama.from_pretrained
            original_func = getattr(from_pretrained, "__func__", None)

            # Look for 'startswith' in the co_names which indicates our patch
            if original_func:
                self.assertIn(
                    "startswith",
                    original_func.__code__.co_names,
                    "llama_cpp.Llama.from_pretrained doesn't check for IPFS URIs",
                )
                print("Patched llama-cpp-python with IPFS support")
                return

        self.fail("Could not verify llama_cpp patching")

    def test_patch_summary(self):
        """Print a summary of the patching test."""
        print("Patching test complete!")


if __name__ == "__main__":
    unittest.main()
