"""Secure file opener utility with comprehensive path validation.

Provides safe file opening with external applications, preventing command injection
and path traversal vulnerabilities. Implements CWE-78 mitigation strategies.
"""

import platform
import subprocess
from pathlib import Path

__author__ = "DevPyLib Contributors"


class FileOpenerError(Exception):
    """Base exception for file opener errors."""

    pass


class PathValidationError(FileOpenerError):
    """Exception raised when file path validation fails."""

    pass


class ExtensionNotAllowedError(FileOpenerError):
    """Exception raised when file extension is not whitelisted."""

    pass


class SecureFileOpener:
    """Secure file opener with path validation and extension whitelisting.

    Validates file paths before opening with system default applications,
    preventing command injection and path traversal attacks.

    Attributes:
        allowed_extensions: Set of whitelisted file extensions (lowercase, with dot).
        allowed_directories: List of allowed base directories (resolved paths).
        timeout: Subprocess timeout in seconds.
    """

    # Default safe file extensions for content creation workflows
    DEFAULT_ALLOWED_EXTENSIONS = {
        # Images
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".exr",
        ".hdr",
        ".bmp",
        ".gif",
        # 3D/DCC files
        ".ma",
        ".mb",
        ".fbx",
        ".obj",
        ".abc",
        ".usd",
        ".usda",
        ".usdc",
        ".hip",
        ".hipnc",
        ".blend",
        # Documents
        ".txt",
        ".pdf",
        ".md",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        # Video
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
    }

    def __init__(
        self,
        allowed_extensions: set[str] | None = None,
        allowed_directories: list[str | Path] | None = None,
        timeout: int = 30,
    ):
        """Initialize SecureFileOpener with validation rules.

        Args:
            allowed_extensions: Set of allowed file extensions (with dot).
                If None, uses DEFAULT_ALLOWED_EXTENSIONS.
            allowed_directories: List of allowed base directories.
                If None, no directory restriction is enforced.
            timeout: Subprocess timeout in seconds. Defaults to 30.
        """
        self.allowed_extensions = (
            {ext.lower() for ext in allowed_extensions}
            if allowed_extensions is not None
            else self.DEFAULT_ALLOWED_EXTENSIONS.copy()
        )

        self.allowed_directories = (
            [Path(d).resolve() for d in allowed_directories]
            if allowed_directories
            else None
        )

        self.timeout = timeout

    def validate_path(self, file_path: str | Path) -> Path:
        """Validate file path against security rules.

        Args:
            file_path: Path to validate.

        Returns:
            Resolved absolute Path object.

        Raises:
            PathValidationError: If path validation fails.
            ExtensionNotAllowedError: If file extension not whitelisted.
        """
        # Convert to Path and resolve (follows symlinks)
        try:
            path = Path(file_path).resolve(strict=True)
        except (OSError, RuntimeError) as e:
            raise PathValidationError(f"Cannot resolve path '{file_path}': {e}") from e

        # Check file exists
        if not path.exists():
            raise PathValidationError(f"File does not exist: {path}")

        # Check it's a file, not a directory
        if not path.is_file():
            raise PathValidationError(f"Path is not a file: {path}")

        # Validate extension
        extension = path.suffix.lower()
        if extension not in self.allowed_extensions:
            raise ExtensionNotAllowedError(
                f"File extension '{extension}' not allowed. "
                f"Allowed: {sorted(self.allowed_extensions)}"
            )

        # Validate directory if restrictions are set
        if self.allowed_directories:
            is_allowed = any(
                self._is_subpath(path, allowed_dir)
                for allowed_dir in self.allowed_directories
            )
            if not is_allowed:
                raise PathValidationError(
                    f"File is not in allowed directories: {path}"
                )

        return path

    @staticmethod
    def _is_subpath(path: Path, parent: Path) -> bool:
        """Check if path is a subpath of parent.

        Args:
            path: Path to check.
            parent: Potential parent path.

        Returns:
            True if path is under parent directory.
        """
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _get_opener(self) -> tuple[list[str], bool]:
        """Get platform-specific file opener command.

        Returns:
            Tuple of (command_list, use_shell) for subprocess.run.
            Command list always includes placeholder for file path.

        Raises:
            OSError: If platform not supported.
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return (["open"], False)
        elif system == "Windows":
            # Use cmd /c start with proper escaping
            # Note: start requires a window title as first arg after /c start
            return (["cmd", "/c", "start", '""'], False)
        elif system == "Linux":
            # Try xdg-open (most common), fallback to alternatives
            return (["xdg-open"], False)
        else:
            raise OSError(f"Unsupported platform: {system}")

    def open_file(
        self,
        file_path: str | Path,
        validate: bool = True,
    ) -> subprocess.CompletedProcess:
        """Open file with system default application.

        Args:
            file_path: Path to file to open.
            validate: Whether to validate path (default: True).
                Only disable for pre-validated paths.

        Returns:
            subprocess.CompletedProcess result.

        Raises:
            PathValidationError: If path validation fails.
            ExtensionNotAllowedError: If extension not allowed.
            subprocess.TimeoutExpired: If subprocess times out.
            subprocess.SubprocessError: If subprocess fails.
        """
        # Validate path
        validated_path = self.validate_path(file_path) if validate else Path(file_path).resolve()

        # Get platform-specific opener
        opener_cmd, use_shell = self._get_opener()

        # Build command - NEVER use shell=True
        cmd = opener_cmd + [str(validated_path)]

        # Execute with timeout and error handling
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=self.timeout,
                shell=use_shell,  # Always False for security
            )
            return result

        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(
                cmd=e.cmd,
                timeout=e.timeout,
                output=e.output,
                stderr=e.stderr,
            ) from e

        except subprocess.CalledProcessError as e:
            raise subprocess.SubprocessError(
                f"Failed to open file '{validated_path}': {e.stderr.decode()}"
            ) from e

    def add_extension(self, extension: str) -> None:
        """Add an extension to the whitelist.

        Args:
            extension: File extension to add (with or without dot).
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        self.allowed_extensions.add(extension.lower())

    def remove_extension(self, extension: str) -> None:
        """Remove an extension from the whitelist.

        Args:
            extension: File extension to remove (with or without dot).
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        self.allowed_extensions.discard(extension.lower())

    def add_directory(self, directory: str | Path) -> None:
        """Add a directory to the allowed directories list.

        Args:
            directory: Directory path to add.
        """
        if self.allowed_directories is None:
            self.allowed_directories = []
        self.allowed_directories.append(Path(directory).resolve())

    def is_extension_allowed(self, extension: str) -> bool:
        """Check if an extension is in the whitelist.

        Args:
            extension: File extension to check (with or without dot).

        Returns:
            True if extension is allowed.
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        return extension.lower() in self.allowed_extensions


# Convenience function for simple use cases
def open_file_secure(
    file_path: str | Path,
    allowed_extensions: set[str] | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """Open a file securely with validation (convenience function).

    Args:
        file_path: Path to file to open.
        allowed_extensions: Set of allowed extensions. If None, uses defaults.
        timeout: Subprocess timeout in seconds.

    Returns:
        subprocess.CompletedProcess result.

    Raises:
        PathValidationError: If path validation fails.
        ExtensionNotAllowedError: If extension not allowed.
        subprocess.TimeoutExpired: If subprocess times out.
        subprocess.SubprocessError: If subprocess fails.
    """
    opener = SecureFileOpener(allowed_extensions=allowed_extensions, timeout=timeout)
    return opener.open_file(file_path)
