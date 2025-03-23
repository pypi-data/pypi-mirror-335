"""
Tests for from_ipfs.utils module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from from_ipfs.utils import (
    clear_cache,
    extract_cid_from_uri,
    get_cache_path,
    is_cached,
    is_ipfs_uri,
)


class TestUtils(unittest.TestCase):
    """Tests for the utils module."""

    def test_is_ipfs_uri(self):
        """Test is_ipfs_uri function."""
        self.assertTrue(is_ipfs_uri("ipfs://QmYourModelCID"))
        self.assertFalse(is_ipfs_uri("https://huggingface.co/bert-base-uncased"))
        self.assertFalse(is_ipfs_uri("bert-base-uncased"))

    def test_extract_cid_from_uri(self):
        """Test extract_cid_from_uri function."""
        self.assertEqual(extract_cid_from_uri("ipfs://QmYourModelCID"), "QmYourModelCID")
        self.assertEqual(
            extract_cid_from_uri("ipfs://QmYourModelCID/config.json"), "QmYourModelCID"
        )

        with self.assertRaises(ValueError):
            extract_cid_from_uri("https://huggingface.co/bert-base-uncased")

    def test_get_cache_path(self):
        """Test get_cache_path function."""
        with patch("from_ipfs.utils.CACHE_DIR", "/tmp/from_ipfs"):
            self.assertEqual(get_cache_path("QmYourModelCID"), "/tmp/from_ipfs/QmYourModelCID")

    def test_is_cached(self):
        """Test is_cached function."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("from_ipfs.utils.CACHE_DIR", tmp_dir):
                # Create a fake cached model
                os.makedirs(os.path.join(tmp_dir, "QmYourModelCID"))

                self.assertTrue(is_cached("QmYourModelCID"))
                self.assertFalse(is_cached("QmNonExistentCID"))

    def test_clear_cache(self):
        """Test clear_cache function."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("from_ipfs.utils.CACHE_DIR", tmp_dir):
                # Create some fake cached models
                os.makedirs(os.path.join(tmp_dir, "QmYourModelCID1"))
                os.makedirs(os.path.join(tmp_dir, "QmYourModelCID2"))

                # Test clearing specific CID
                clear_cache("QmYourModelCID1")
                self.assertFalse(os.path.exists(os.path.join(tmp_dir, "QmYourModelCID1")))
                self.assertTrue(os.path.exists(os.path.join(tmp_dir, "QmYourModelCID2")))

                # Test clearing all
                clear_cache()
                self.assertFalse(os.path.exists(os.path.join(tmp_dir, "QmYourModelCID2")))


if __name__ == "__main__":
    unittest.main()
