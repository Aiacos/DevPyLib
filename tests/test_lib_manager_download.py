"""Integration tests for lib_manager download with verification.

Tests the complete download flow including hash verification, extraction,
and cleanup behavior to ensure security measures work correctly.
"""

import hashlib
import pathlib
import tempfile
import urllib.error
import zipfile
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from mayaLib.pipelineLib.utility.lib_manager import InstallLibrary


@pytest.fixture
def installer():
    """Create an InstallLibrary instance for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        maya_scripts = temp_path / "maya" / "scripts"
        maya_scripts.mkdir(parents=True)

        inst = InstallLibrary()
        inst.maya_script_path = maya_scripts
        yield inst


@pytest.fixture
def mock_zip_file():
    """Create a mock zip file with known content and hash."""
    content = b"Mock DevPyLib zip content"
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    expected_hash = sha256_hash.hexdigest()

    return {
        "content": content,
        "hash": expected_hash,
    }


@pytest.mark.unit
class TestDownloadWithVerification:
    """Test suite for download method with hash verification."""

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_with_valid_hash(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test successful download with correct hash verification."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = mock_zip_file["hash"]

        # Create actual file for hash verification
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock zipfile extraction
        mock_zip_context = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_context

        # Execute
        installer.download()

        # Verify
        mock_urlretrieve.assert_called_once()
        mock_zipfile.assert_called_once_with(str(zip_path), "r")
        mock_zip_context.extractall.assert_called_once()

        captured = capsys.readouterr()
        assert "Hash verification successful" in captured.out
        assert "Extracted to:" in captured.out

        # Verify zip file was cleaned up
        assert not zip_path.exists()

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_with_invalid_hash(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test download fails and cleans up with incorrect hash."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = "invalid_hash_" + "0" * 50  # Wrong hash

        # Create actual file for hash verification
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Execute
        installer.download()

        # Verify download occurred but extraction did NOT
        mock_urlretrieve.assert_called_once()
        mock_zipfile.assert_not_called()  # Should not extract unverified file

        captured = capsys.readouterr()
        assert "SECURITY WARNING" in captured.out
        assert "Hash verification failed" in captured.out
        assert "man-in-the-middle" in captured.out
        assert "Removed unverified file" in captured.out

        # Verify zip file was cleaned up
        assert not zip_path.exists()

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_without_hash_backward_compatibility(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test download works without hash for backward compatibility."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = ""  # No hash provided

        # Create actual file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock zipfile extraction
        mock_zip_context = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_context

        # Execute
        installer.download()

        # Verify download and extraction occurred
        mock_urlretrieve.assert_called_once()
        mock_zipfile.assert_called_once()
        mock_zip_context.extractall.assert_called_once()

        captured = capsys.readouterr()
        assert "Hash verification" not in captured.out  # No verification done
        assert "Extracted to:" in captured.out

    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_network_error(self, mock_urlretrieve, installer, capsys):
        """Test download handles network errors gracefully."""
        # Setup
        mock_urlretrieve.side_effect = urllib.error.URLError("Network error")

        # Execute
        installer.download()

        # Verify
        captured = capsys.readouterr()
        assert "Error downloading file" in captured.out

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_extraction_error(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test download handles extraction errors gracefully."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = ""  # Skip hash verification

        # Create actual file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock zipfile to raise error
        mock_zipfile.side_effect = zipfile.BadZipFile("Corrupted zip")

        # Execute
        installer.download()

        # Verify
        captured = capsys.readouterr()
        assert "Error extracting zip file" in captured.out

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_removes_existing_directory(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test download removes existing extracted directory before proceeding."""
        # Setup
        existing_dir = installer.maya_script_path / "DevPyLib-master"
        existing_dir.mkdir()
        existing_file = existing_dir / "test.txt"
        existing_file.write_text("old content")

        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = ""

        # Create actual file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock zipfile extraction
        mock_zip_context = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_context

        # Execute
        installer.download()

        # Verify
        captured = capsys.readouterr()
        assert "Removed existing directory" in captured.out
        mock_urlretrieve.assert_called_once()
        mock_zipfile.assert_called_once()

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_hash_verification_file_not_found_error(
        self, mock_urlretrieve, mock_zipfile, installer, capsys
    ):
        """Test download handles file disappearing during verification."""
        # Setup
        installer.lib_hash = "a" * 64  # Set hash to trigger verification

        # Mock urlretrieve but don't create file (simulates file disappearing)
        mock_urlretrieve.return_value = None

        # Execute
        installer.download()

        # Verify
        captured = capsys.readouterr()
        assert "Hash verification error: File not found" in captured.out
        mock_zipfile.assert_not_called()

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_hash_verification_io_error(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test download handles I/O errors during hash verification."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = mock_zip_file["hash"]

        # Create file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock _verify_file_hash to raise OSError
        with patch.object(
            installer, "_verify_file_hash", side_effect=OSError("Permission denied")
        ):
            # Execute
            installer.download()

        # Verify
        captured = capsys.readouterr()
        assert "Hash verification error: Unable to read file" in captured.out
        assert "Permission denied" in captured.out
        mock_zipfile.assert_not_called()

        # Verify cleanup occurred
        assert not zip_path.exists()

    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_cleanup_on_verification_failure(
        self, mock_urlretrieve, mock_zipfile, installer, mock_zip_file, capsys
    ):
        """Test that unverified files are always cleaned up on failure."""
        # Setup
        zip_path = installer.maya_script_path / "master.zip"
        installer.lib_hash = "wrong_hash_" + "0" * 50

        # Create actual file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Execute
        installer.download()

        # Verify file was created then deleted
        assert not zip_path.exists(), "Unverified file should be deleted"

        captured = capsys.readouterr()
        assert "Removed unverified file" in captured.out
        mock_zipfile.assert_not_called()

    @patch("mayaLib.pipelineLib.utility.lib_manager.shutil.rmtree")
    @patch("mayaLib.pipelineLib.utility.lib_manager.zipfile.ZipFile")
    @patch("mayaLib.pipelineLib.utility.lib_manager.urllib.request.urlretrieve")
    def test_download_with_custom_filename(
        self, mock_urlretrieve, mock_zipfile, mock_rmtree, installer, mock_zip_file
    ):
        """Test download with custom zip filename."""
        # Setup
        custom_filename = "custom_download.zip"
        zip_path = installer.maya_script_path / custom_filename
        installer.lib_hash = ""

        # Create actual file
        def create_zip_file(*args, **kwargs):
            zip_path.write_bytes(mock_zip_file["content"])

        mock_urlretrieve.side_effect = create_zip_file

        # Mock zipfile extraction
        mock_zip_context = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_context

        # Execute
        installer.download(zip_filename=custom_filename)

        # Verify
        mock_urlretrieve.assert_called_once()
        call_args = mock_urlretrieve.call_args
        assert str(zip_path) in call_args[0]  # Check path includes custom filename
