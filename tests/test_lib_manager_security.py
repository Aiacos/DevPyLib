"""Unit tests for lib_manager security features.

Tests the hash verification functionality added to prevent MITM attacks
and ensure integrity of downloaded library updates.
"""

import hashlib
import pathlib
import tempfile

import pytest

from mayaLib.pipelineLib.utility.lib_manager import InstallLibrary


@pytest.mark.unit
class TestHashVerification:
    """Test suite for _verify_file_hash method."""

    @pytest.fixture
    def installer(self):
        """Create an InstallLibrary instance for testing."""
        return InstallLibrary()

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file with known content and hash."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            content = b"Test content for hash verification"
            f.write(content)
            temp_path = pathlib.Path(f.name)

        # Compute the expected hash
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content)
        expected_hash = sha256_hash.hexdigest()

        yield temp_path, expected_hash

        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    def test_verify_file_hash_correct(self, installer, temp_file, capsys):
        """Test hash verification with correct hash."""
        temp_path, expected_hash = temp_file

        result = installer._verify_file_hash(temp_path, expected_hash)

        assert result is True
        captured = capsys.readouterr()
        assert "Hash verification successful" in captured.out

    def test_verify_file_hash_incorrect(self, installer, temp_file, capsys):
        """Test hash verification with incorrect hash."""
        temp_path, _ = temp_file
        wrong_hash = "0" * 64  # Invalid hash

        result = installer._verify_file_hash(temp_path, wrong_hash)

        assert result is False
        captured = capsys.readouterr()
        assert "Hash mismatch" in captured.out
        assert "Expected:" in captured.out
        assert "Computed:" in captured.out

    def test_verify_file_hash_nonexistent(self, installer):
        """Test hash verification with non-existent file."""
        nonexistent_path = pathlib.Path("/nonexistent/file.zip")
        expected_hash = "a" * 64

        with pytest.raises(FileNotFoundError):
            installer._verify_file_hash(nonexistent_path, expected_hash)

    def test_verify_file_hash_large_file(self, installer):
        """Test hash verification with larger file to ensure chunk reading works."""
        # Create a file larger than the 8KB chunk size
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            content = b"x" * (10 * 1024)  # 10KB file
            f.write(content)
            temp_path = pathlib.Path(f.name)

        try:
            # Compute expected hash
            sha256_hash = hashlib.sha256()
            sha256_hash.update(content)
            expected_hash = sha256_hash.hexdigest()

            result = installer._verify_file_hash(temp_path, expected_hash)

            assert result is True
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_verify_file_hash_empty_file(self, installer):
        """Test hash verification with empty file."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            temp_path = pathlib.Path(f.name)

        try:
            # Hash of empty file
            expected_hash = hashlib.sha256(b"").hexdigest()

            result = installer._verify_file_hash(temp_path, expected_hash)

            assert result is True
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_lib_hash_attribute_exists(self, installer):
        """Test that lib_hash attribute is initialized."""
        assert hasattr(installer, "lib_hash")
        assert isinstance(installer.lib_hash, str)
