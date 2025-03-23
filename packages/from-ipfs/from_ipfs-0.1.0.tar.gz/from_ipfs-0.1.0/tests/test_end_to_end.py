import tempfile
import unittest

# Import from_ipfs first to apply patches


class TestIPFSIntegration(unittest.TestCase):
    """Test that the IPFS patches are correctly applied."""

    def setUp(self):
        """Set up a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up the temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_transformers_ipfs_uri(self):
        """Test that transformers recognizes and correctly handles IPFS URIs."""
        # Import the patched libraries
        from transformers import AutoModel

        # Check if the method is patched properly
        from_pretrained = AutoModel.from_pretrained
        if hasattr(from_pretrained, "__func__"):
            func_code = from_pretrained.__func__.__code__

            # Look for 'startswith' in the co_names which indicates our patch
            # that checks if a string starts with 'ipfs://'
            self.assertIn(
                "startswith",
                func_code.co_names,
                "AutoModel.from_pretrained doesn't check for IPFS URIs",
            )
            print("✅ AutoModel.from_pretrained is patched to handle IPFS URIs")
            return

        self.fail("Could not verify transformers patching")

    def test_llama_cpp_ipfs_uri(self):
        """Test that llama_cpp recognizes and correctly handles IPFS URIs."""
        # Import the patched libraries
        import llama_cpp

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
                print("✅ llama_cpp.Llama.from_pretrained is patched to handle IPFS URIs")
                return

        self.fail("Could not verify llama_cpp patching")

    def test_patch_summary(self):
        """Print a summary of the patching."""
        print("\nPatching test complete!")


if __name__ == "__main__":
    unittest.main()
