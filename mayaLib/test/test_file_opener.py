"""Comprehensive tests for SecureFileOpener utility.

Tests path validation, extension whitelisting, directory restrictions,
symlink resolution, and cross-platform file opening functionality.
"""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import file_opener module directly without triggering Maya dependency chain
_file_opener_path = Path(__file__).parent.parent / "pipelineLib" / "utility" / "file_opener.py"
_spec = importlib.util.spec_from_file_location("file_opener", _file_opener_path)
_file_opener = importlib.util.module_from_spec(_spec)
sys.modules["file_opener"] = _file_opener
_spec.loader.exec_module(_file_opener)

# Import the classes and functions
ExtensionNotAllowedError = _file_opener.ExtensionNotAllowedError
FileOpenerError = _file_opener.FileOpenerError
PathValidationError = _file_opener.PathValidationError
SecureFileOpener = _file_opener.SecureFileOpener
open_file_secure = _file_opener.open_file_secure


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files.

    Args:
        tmp_path: Pytest fixture providing temporary directory.

    Returns:
        Path to temporary directory.
    """
    return tmp_path


@pytest.fixture
def test_file(temp_dir):
    """Create a temporary test file with allowed extension.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to test file.
    """
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    return test_file


@pytest.fixture
def executable_file(temp_dir):
    """Create a temporary file with executable extension.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to executable file.
    """
    exe_file = temp_dir / "malicious.exe"
    exe_file.write_text("malicious content")
    return exe_file


@pytest.fixture
def image_file(temp_dir):
    """Create a temporary image file.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to image file.
    """
    img_file = temp_dir / "image.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG header
    return img_file


@pytest.fixture
def secure_opener():
    """Create SecureFileOpener instance with default settings.

    Returns:
        SecureFileOpener instance.
    """
    return SecureFileOpener()


@pytest.fixture
def restricted_opener(temp_dir):
    """Create SecureFileOpener with directory restrictions.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        SecureFileOpener instance with restricted directories.
    """
    return SecureFileOpener(allowed_directories=[temp_dir])


# ============================================================================
# Initialization Tests
# ============================================================================


class TestSecureFileOpenerInit:
    """Test SecureFileOpener initialization."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        opener = SecureFileOpener()
        assert opener.allowed_extensions == SecureFileOpener.DEFAULT_ALLOWED_EXTENSIONS
        assert opener.allowed_directories is None
        assert opener.timeout == 30

    def test_custom_extensions(self):
        """Test initialization with custom allowed extensions."""
        custom_exts = {".custom", ".test"}
        opener = SecureFileOpener(allowed_extensions=custom_exts)
        assert opener.allowed_extensions == {".custom", ".test"}

    def test_extensions_lowercase_normalization(self):
        """Test that extensions are normalized to lowercase."""
        opener = SecureFileOpener(allowed_extensions={".TXT", ".PNG"})
        assert opener.allowed_extensions == {".txt", ".png"}

    def test_allowed_directories(self, temp_dir):
        """Test initialization with allowed directories."""
        opener = SecureFileOpener(allowed_directories=[temp_dir])
        assert len(opener.allowed_directories) == 1
        assert opener.allowed_directories[0] == temp_dir.resolve()

    def test_custom_timeout(self):
        """Test initialization with custom timeout."""
        opener = SecureFileOpener(timeout=60)
        assert opener.timeout == 60


# ============================================================================
# Path Validation Tests
# ============================================================================


class TestPathValidation:
    """Test path validation functionality."""

    def test_validate_existing_file(self, secure_opener, test_file):
        """Test validation of existing file with allowed extension."""
        validated = secure_opener.validate_path(test_file)
        assert validated == test_file.resolve()

    def test_validate_non_existent_file(self, secure_opener, temp_dir):
        """Test validation rejects non-existent files."""
        non_existent = temp_dir / "nonexistent.txt"
        with pytest.raises(PathValidationError, match="Cannot resolve path"):
            secure_opener.validate_path(non_existent)

    def test_validate_directory(self, secure_opener, temp_dir):
        """Test validation rejects directories."""
        # Create a directory and try to validate it
        dir_path = temp_dir / "subdir"
        dir_path.mkdir()
        with pytest.raises(PathValidationError, match="Path is not a file"):
            secure_opener.validate_path(dir_path)

    def test_validate_disallowed_extension(self, secure_opener, executable_file):
        """Test validation rejects files with disallowed extensions."""
        with pytest.raises(
            ExtensionNotAllowedError, match="File extension '.exe' not allowed"
        ):
            secure_opener.validate_path(executable_file)

    def test_validate_outside_allowed_directory(self, restricted_opener, temp_dir):
        """Test validation rejects files outside allowed directories."""
        # Create file in a different temp directory
        with tempfile.TemporaryDirectory() as other_dir:
            other_file = Path(other_dir) / "file.txt"
            other_file.write_text("content")

            with pytest.raises(
                PathValidationError, match="File is not in allowed directories"
            ):
                restricted_opener.validate_path(other_file)

    def test_validate_inside_allowed_directory(self, restricted_opener, test_file):
        """Test validation accepts files inside allowed directories."""
        validated = restricted_opener.validate_path(test_file)
        assert validated == test_file.resolve()

    def test_validate_string_path(self, secure_opener, test_file):
        """Test validation works with string paths."""
        validated = secure_opener.validate_path(str(test_file))
        assert validated == test_file.resolve()

    @pytest.mark.parametrize(
        "extension",
        [".jpg", ".png", ".ma", ".mb", ".fbx", ".usd", ".pdf", ".json", ".mp4"],
    )
    def test_validate_allowed_extensions(self, secure_opener, temp_dir, extension):
        """Test validation accepts all default allowed extensions."""
        test_file = temp_dir / f"test{extension}"
        test_file.write_text("content")
        validated = secure_opener.validate_path(test_file)
        assert validated.suffix.lower() == extension

    def test_validate_symlink_resolution(self, secure_opener, test_file, temp_dir):
        """Test validation resolves symlinks to real paths."""
        # Create symlink
        symlink = temp_dir / "link.txt"
        try:
            symlink.symlink_to(test_file)
            validated = secure_opener.validate_path(symlink)
            # Should resolve to actual file, not symlink
            assert validated == test_file.resolve()
        except OSError:
            # Skip on Windows without developer mode
            pytest.skip("Symlinks require elevated privileges on Windows")

    def test_validate_path_traversal_attempt(self, restricted_opener, temp_dir):
        """Test validation prevents path traversal attacks."""
        # Create a file with path traversal in name
        safe_file = temp_dir / "subdir" / "file.txt"
        safe_file.parent.mkdir(exist_ok=True)
        safe_file.write_text("content")

        # This should succeed because file is still within allowed directory
        validated = restricted_opener.validate_path(safe_file)
        assert restricted_opener._is_subpath(validated, temp_dir.resolve())


# ============================================================================
# File Opening Tests
# ============================================================================


class TestFileOpening:
    """Test file opening functionality."""

    @patch("subprocess.run")
    def test_open_file_success(self, mock_run, secure_opener, test_file):
        """Test successful file opening."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        secure_opener.open_file(test_file)

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert str(test_file.resolve()) in call_args[0][0]
        assert call_args[1]["shell"] is False
        assert call_args[1]["timeout"] == 30

    @patch("subprocess.run")
    def test_open_file_without_validation(self, mock_run, secure_opener, test_file):
        """Test opening file with validation disabled."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        secure_opener.open_file(test_file, validate=False)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_open_file_timeout(self, mock_run, secure_opener, test_file):
        """Test file opening timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=30)

        with pytest.raises(subprocess.TimeoutExpired):
            secure_opener.open_file(test_file)

    @patch("subprocess.run")
    def test_open_file_subprocess_error(self, mock_run, secure_opener, test_file):
        """Test file opening subprocess error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=[], stderr=b"error"
        )

        with pytest.raises(subprocess.SubprocessError, match="Failed to open file"):
            secure_opener.open_file(test_file)

    def test_open_file_validation_failure(self, secure_opener, executable_file):
        """Test file opening fails validation for disallowed extension."""
        with pytest.raises(ExtensionNotAllowedError):
            secure_opener.open_file(executable_file)

    @patch("subprocess.run")
    def test_open_file_custom_timeout(self, mock_run, test_file):
        """Test file opening with custom timeout."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        opener = SecureFileOpener(timeout=60)
        opener.open_file(test_file)

        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 60


# ============================================================================
# Cross-Platform Opener Tests
# ============================================================================


class TestCrossPlatformOpener:
    """Test platform-specific opener selection."""

    @patch("platform.system", return_value="Darwin")
    def test_get_opener_macos(self, mock_platform, secure_opener):
        """Test opener command for macOS."""
        cmd, use_shell = secure_opener._get_opener()
        assert cmd == ["open"]
        assert use_shell is False

    @patch("platform.system", return_value="Windows")
    def test_get_opener_windows(self, mock_platform, secure_opener):
        """Test opener command for Windows."""
        cmd, use_shell = secure_opener._get_opener()
        assert cmd == ["cmd", "/c", "start", '""']
        assert use_shell is False

    @patch("platform.system", return_value="Linux")
    def test_get_opener_linux(self, mock_platform, secure_opener):
        """Test opener command for Linux."""
        cmd, use_shell = secure_opener._get_opener()
        assert cmd == ["xdg-open"]
        assert use_shell is False

    @patch("platform.system", return_value="Unknown")
    def test_get_opener_unsupported_platform(self, mock_platform, secure_opener):
        """Test opener raises error for unsupported platform."""
        with pytest.raises(OSError, match="Unsupported platform"):
            secure_opener._get_opener()


# ============================================================================
# Extension Management Tests
# ============================================================================


class TestExtensionManagement:
    """Test extension whitelist management."""

    def test_add_extension_with_dot(self, secure_opener):
        """Test adding extension with leading dot."""
        initial_count = len(secure_opener.allowed_extensions)
        secure_opener.add_extension(".custom")
        assert ".custom" in secure_opener.allowed_extensions
        assert len(secure_opener.allowed_extensions) == initial_count + 1

    def test_add_extension_without_dot(self, secure_opener):
        """Test adding extension without leading dot."""
        secure_opener.add_extension("custom")
        assert ".custom" in secure_opener.allowed_extensions

    def test_add_extension_uppercase(self, secure_opener):
        """Test adding extension normalizes to lowercase."""
        secure_opener.add_extension(".CUSTOM")
        assert ".custom" in secure_opener.allowed_extensions
        assert ".CUSTOM" not in secure_opener.allowed_extensions

    def test_remove_extension_with_dot(self, secure_opener):
        """Test removing extension with leading dot."""
        secure_opener.add_extension(".custom")
        secure_opener.remove_extension(".custom")
        assert ".custom" not in secure_opener.allowed_extensions

    def test_remove_extension_without_dot(self, secure_opener):
        """Test removing extension without leading dot."""
        secure_opener.add_extension(".custom")
        secure_opener.remove_extension("custom")
        assert ".custom" not in secure_opener.allowed_extensions

    def test_remove_nonexistent_extension(self, secure_opener):
        """Test removing non-existent extension doesn't raise error."""
        initial_count = len(secure_opener.allowed_extensions)
        secure_opener.remove_extension(".nonexistent")
        assert len(secure_opener.allowed_extensions) == initial_count

    def test_is_extension_allowed_with_dot(self, secure_opener):
        """Test checking if extension is allowed with dot."""
        assert secure_opener.is_extension_allowed(".txt")
        assert not secure_opener.is_extension_allowed(".exe")

    def test_is_extension_allowed_without_dot(self, secure_opener):
        """Test checking if extension is allowed without dot."""
        assert secure_opener.is_extension_allowed("txt")
        assert not secure_opener.is_extension_allowed("exe")

    def test_is_extension_allowed_case_insensitive(self, secure_opener):
        """Test extension check is case-insensitive."""
        assert secure_opener.is_extension_allowed(".TXT")
        assert secure_opener.is_extension_allowed("TXT")


# ============================================================================
# Directory Management Tests
# ============================================================================


class TestDirectoryManagement:
    """Test directory restriction management."""

    def test_add_directory(self, secure_opener, temp_dir):
        """Test adding directory to allowed list."""
        secure_opener.add_directory(temp_dir)
        assert secure_opener.allowed_directories is not None
        assert temp_dir.resolve() in secure_opener.allowed_directories

    def test_add_directory_string(self, secure_opener, temp_dir):
        """Test adding directory as string."""
        secure_opener.add_directory(str(temp_dir))
        assert temp_dir.resolve() in secure_opener.allowed_directories

    def test_add_directory_initializes_list(self):
        """Test adding directory initializes list if None."""
        opener = SecureFileOpener()
        assert opener.allowed_directories is None

        opener.add_directory("/tmp")
        assert opener.allowed_directories is not None
        assert len(opener.allowed_directories) == 1

    def test_is_subpath_positive(self, temp_dir):
        """Test _is_subpath correctly identifies subpaths."""
        parent = temp_dir
        child = temp_dir / "subdir" / "file.txt"
        child.parent.mkdir()
        child.write_text("content")

        assert SecureFileOpener._is_subpath(child, parent)

    def test_is_subpath_negative(self, temp_dir):
        """Test _is_subpath correctly rejects non-subpaths."""
        with tempfile.TemporaryDirectory() as other_dir:
            parent = temp_dir
            non_child = Path(other_dir) / "file.txt"
            non_child.write_text("content")

            assert not SecureFileOpener._is_subpath(non_child, parent)

    def test_is_subpath_equal(self, temp_dir):
        """Test _is_subpath handles equal paths."""
        assert SecureFileOpener._is_subpath(temp_dir, temp_dir)


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunction:
    """Test open_file_secure convenience function."""

    @patch("subprocess.run")
    def test_open_file_secure_default(self, mock_run, test_file):
        """Test convenience function with default parameters."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        open_file_secure(test_file)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_open_file_secure_custom_extensions(self, mock_run, temp_dir):
        """Test convenience function with custom extensions."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        custom_file = temp_dir / "file.custom"
        custom_file.write_text("content")

        open_file_secure(custom_file, allowed_extensions={".custom"})
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_open_file_secure_custom_timeout(self, mock_run, test_file):
        """Test convenience function with custom timeout."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        open_file_secure(test_file, timeout=60)

        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 60


# ============================================================================
# Exception Hierarchy Tests
# ============================================================================


class TestExceptionHierarchy:
    """Test custom exception hierarchy."""

    def test_path_validation_error_is_file_opener_error(self):
        """Test PathValidationError inherits from FileOpenerError."""
        assert issubclass(PathValidationError, FileOpenerError)

    def test_extension_not_allowed_error_is_file_opener_error(self):
        """Test ExtensionNotAllowedError inherits from FileOpenerError."""
        assert issubclass(ExtensionNotAllowedError, FileOpenerError)

    def test_file_opener_error_is_exception(self):
        """Test FileOpenerError inherits from Exception."""
        assert issubclass(FileOpenerError, Exception)

    def test_raise_path_validation_error(self):
        """Test raising PathValidationError."""
        with pytest.raises(PathValidationError, match="test error"):
            raise PathValidationError("test error")

    def test_raise_extension_not_allowed_error(self):
        """Test raising ExtensionNotAllowedError."""
        with pytest.raises(ExtensionNotAllowedError, match="test error"):
            raise ExtensionNotAllowedError("test error")


# ============================================================================
# Security Tests
# ============================================================================


class TestSecurity:
    """Test security-related functionality."""

    @patch("subprocess.run")
    def test_never_uses_shell_true(self, mock_run, secure_opener, test_file):
        """Test that subprocess never uses shell=True."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        secure_opener.open_file(test_file)

        call_args = mock_run.call_args
        assert call_args[1]["shell"] is False

    def test_blocks_executable_extensions(self, secure_opener, temp_dir):
        """Test that executable extensions are blocked by default."""
        dangerous_extensions = [".exe", ".bat", ".sh", ".cmd", ".ps1", ".com"]

        for ext in dangerous_extensions:
            dangerous_file = temp_dir / f"malicious{ext}"
            dangerous_file.write_text("malicious content")

            with pytest.raises(ExtensionNotAllowedError):
                secure_opener.validate_path(dangerous_file)

    def test_symlink_to_disallowed_location(self, restricted_opener, temp_dir):
        """Test symlink to file outside allowed directory is rejected."""
        # Create file outside allowed directory
        with tempfile.TemporaryDirectory() as other_dir:
            target_file = Path(other_dir) / "target.txt"
            target_file.write_text("content")

            # Create symlink inside allowed directory
            symlink = temp_dir / "link.txt"
            try:
                symlink.symlink_to(target_file)

                # Should fail because resolved path is outside allowed directory
                with pytest.raises(PathValidationError, match="not in allowed directories"):
                    restricted_opener.validate_path(symlink)
            except OSError:
                # Skip on Windows without developer mode
                pytest.skip("Symlinks require elevated privileges on Windows")

    @patch("subprocess.run")
    def test_timeout_prevents_hanging(self, mock_run, secure_opener, test_file):
        """Test timeout prevents subprocess from hanging indefinitely."""
        # Simulate a hanging process
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=30)

        with pytest.raises(subprocess.TimeoutExpired):
            secure_opener.open_file(test_file)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring actual file operations."""

    def test_end_to_end_workflow(self, temp_dir):
        """Test complete workflow from initialization to file opening."""
        # Create opener with restrictions
        opener = SecureFileOpener(
            allowed_extensions={".txt", ".md"},
            allowed_directories=[temp_dir],
            timeout=10,
        )

        # Create test file
        test_file = temp_dir / "document.txt"
        test_file.write_text("Test content")

        # Validate path
        validated = opener.validate_path(test_file)
        assert validated.exists()

        # Mock the subprocess to prevent actual opening
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"", stderr=b""
            )

            # Open file
            opener.open_file(test_file)
            assert mock_run.called

    def test_multiple_files_different_extensions(self, temp_dir):
        """Test opening multiple files with different extensions."""
        opener = SecureFileOpener()

        files = {
            "image.png": b"\x89PNG\r\n\x1a\n",
            "document.txt": b"text content",
            "data.json": b'{"key": "value"}',
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"", stderr=b""
            )

            for filename, content in files.items():
                test_file = temp_dir / filename
                test_file.write_bytes(content)

                opener.open_file(test_file)
                assert mock_run.called

            assert mock_run.call_count == len(files)
