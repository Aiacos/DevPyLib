# Security Policy

## Supported Versions

The following versions of DevPyLib are currently supported with security updates:

| Version | Python | Supported          |
| ------- | ------ | ------------------ |
| 1.x     | 3.11   | :white_check_mark: |
| 1.x     | 3.10   | :white_check_mark: |
| 1.x     | 3.9    | :white_check_mark: |
| < 1.0   | < 3.9  | :x:                |

## Reporting a Vulnerability

We take the security of DevPyLib seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Instead, please report security issues through one of these channels:
   - **GitHub Private Vulnerability Reporting**: Use [GitHub's security advisory feature](https://github.com/Aiacos/DevPyLib/security/advisories/new) to privately report the vulnerability
   - **Email**: Contact the repository maintainers directly through their GitHub profile

### What to Include

When reporting a vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: The potential impact and severity of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
- **Affected Versions**: Which versions of DevPyLib are affected
- **Proof of Concept**: If possible, include code or screenshots demonstrating the issue
- **Suggested Fix**: If you have ideas on how to fix the issue (optional)

### What to Expect

- **Initial Response**: We aim to acknowledge receipt of your report within 48 hours
- **Status Updates**: We will provide updates on the progress of addressing the vulnerability
- **Resolution Timeline**: We strive to resolve critical vulnerabilities within 30 days
- **Disclosure**: We follow responsible disclosure practices and will coordinate with you on public disclosure timing

### After Reporting

Once a vulnerability is reported:

1. We will confirm receipt and begin investigation
2. We will work to validate and reproduce the issue
3. We will develop and test a fix
4. We will release a patched version
5. We will publicly acknowledge the reporter (unless anonymity is requested)

## Security Features

DevPyLib includes built-in security measures to protect against supply chain attacks:

### Library Update Integrity Verification

- **Hash Verification**: All library updates downloaded via `lib_manager.py` are verified using SHA-256 cryptographic hashes before extraction
- **MITM Protection**: The download process validates the integrity of downloaded files against known-good hashes, preventing man-in-the-middle attacks
- **Automatic Cleanup**: If hash verification fails, the downloaded file is automatically deleted to prevent accidental installation of unverified or potentially malicious code
- **Clear Error Reporting**: Security failures generate detailed error messages to help diagnose download issues or potential security threats

This feature ensures that DevPyLib updates are authentic and have not been tampered with during download.

## Security Best Practices for Users

When using DevPyLib in your DCC pipeline:

- **Keep Updated**: Always use the latest version of DevPyLib
- **Review Dependencies**: Regularly update and audit dependencies
- **Secure Configurations**: Follow secure configuration practices in your Maya/Houdini/Blender environment
- **Access Control**: Limit access to pipeline scripts and configurations
- **Input Validation**: Validate any user inputs before passing to DevPyLib functions

### Secure File Opening

DevPyLib provides secure file opening utilities to prevent command injection vulnerabilities when opening files with external applications.

#### CWE-78: OS Command Injection Prevention

Opening files with system default applications can lead to arbitrary code execution if file paths are not properly validated. This is particularly risky in shared studio environments where malicious files could be placed in project directories.

**Vulnerable Pattern (DO NOT USE):**

```python
import os
import subprocess

# UNSAFE: No validation
os.startfile(user_provided_path)  # Windows only, no validation

# UNSAFE: Shell injection risk
subprocess.call(f"open {path}", shell=True)  # Never use shell=True

# UNSAFE: No extension validation
subprocess.run(["xdg-open", untrusted_path])  # Could open .exe, .sh, etc.
```

**Secure Pattern (USE THIS):**

```python
from mayaLib.pipelineLib.utility.file_opener import SecureFileOpener

# Create opener with validation
opener = SecureFileOpener()

# Safe file opening with automatic validation
try:
    opener.open_file("/path/to/texture.exr")
except PathValidationError as e:
    print(f"Invalid path: {e}")
except ExtensionNotAllowedError as e:
    print(f"File type not allowed: {e}")
```

#### Path Validation Requirements

The `SecureFileOpener` class implements multiple layers of validation:

1. **File Existence**: Verifies the file exists before opening
2. **Path Resolution**: Resolves symlinks to prevent path traversal attacks
3. **Extension Whitelist**: Only allows explicitly permitted file types
4. **Directory Restrictions**: Optionally restricts files to specific directories
5. **Type Checking**: Ensures the path points to a file, not a directory

**Example with Custom Restrictions:**

```python
from mayaLib.pipelineLib.utility.file_opener import SecureFileOpener
from pathlib import Path

# Create opener with custom restrictions
opener = SecureFileOpener(
    allowed_extensions={".ma", ".mb", ".fbx"},  # Maya files only
    allowed_directories=["/projects/current_show"],  # Restrict to project dir
    timeout=30  # 30-second timeout
)

# This will succeed
opener.open_file("/projects/current_show/assets/character.ma")

# This will raise ExtensionNotAllowedError
opener.open_file("/projects/current_show/malicious.exe")

# This will raise PathValidationError
opener.open_file("/other/directory/file.ma")
```

#### Subprocess Safety: subprocess.run vs os.system vs os.startfile

DevPyLib uses `subprocess.run()` with `shell=False` for cross-platform safety:

| Method | Security Risk | Cross-Platform | Recommendation |
|--------|--------------|----------------|----------------|
| `os.system()` | ❌ **High** - Shell injection | ❌ No | **Never use** |
| `os.startfile()` | ⚠️ **Medium** - No validation | ❌ Windows only | **Avoid** |
| `subprocess.call(..., shell=True)` | ❌ **High** - Shell injection | ⚠️ Partial | **Never use** |
| `subprocess.run([...], shell=False)` | ✅ **Low** - Safe with validation | ✅ Yes | **Use this** |

**Why `shell=False` is Critical:**

```python
# UNSAFE: Shell injection vulnerability
user_file = "image.jpg; rm -rf /"  # Malicious input
subprocess.run(f"open {user_file}", shell=True)  # Executes rm -rf /!

# SAFE: No shell interpretation
subprocess.run(["open", user_file], shell=False)  # Opens literal filename
```

#### Allowed File Extensions Rationale

The default whitelist includes common content creation file types:

- **Images**: `.jpg`, `.png`, `.exr`, `.tif`, `.hdr` - Textures and renders
- **3D Files**: `.ma`, `.mb`, `.fbx`, `.usd`, `.abc` - Scene files
- **Documents**: `.txt`, `.pdf`, `.json`, `.yaml` - Configuration and docs
- **Video**: `.mp4`, `.mov`, `.avi` - Animation playback

**Excluded by Default (Security Risk):**

- ❌ `.exe`, `.bat`, `.cmd`, `.com` - Windows executables
- ❌ `.sh`, `.bash`, `.zsh` - Unix shell scripts
- ❌ `.py`, `.pyc`, `.pyw` - Python executables
- ❌ `.app`, `.dmg` - macOS applications
- ❌ `.dll`, `.so`, `.dylib` - Binary libraries

**Adding Custom Extensions:**

```python
from mayaLib.pipelineLib.utility.file_opener import SecureFileOpener

opener = SecureFileOpener()

# Add a custom extension if needed
opener.add_extension(".nk")  # Nuke scripts

# Check if extension is allowed
if opener.is_extension_allowed(".ma"):
    print("Maya files allowed")

# Remove an extension
opener.remove_extension(".pdf")
```

#### Common Vulnerabilities to Avoid

1. **Path Traversal**
   ```python
   # UNSAFE: Doesn't resolve symlinks
   path = user_input  # Could be symlink to /etc/passwd

   # SAFE: SecureFileOpener resolves symlinks automatically
   opener.open_file(path)  # Validates resolved path
   ```

2. **Extension Spoofing**
   ```python
   # UNSAFE: Only checks filename, not actual extension
   if ".jpg" in filename:  # Matches "malware.exe.jpg"
       open_file(filename)

   # SAFE: Validates actual file extension
   opener = SecureFileOpener(allowed_extensions={".jpg"})
   opener.open_file(filename)  # Only opens actual .jpg files
   ```

3. **Directory Traversal**
   ```python
   # UNSAFE: No directory restrictions
   open_file("../../../../etc/passwd")

   # SAFE: Restrict to project directories
   opener = SecureFileOpener(allowed_directories=["/projects"])
   opener.open_file("file.ma")  # Must be under /projects
   ```

4. **Timeout Handling**
   ```python
   # UNSAFE: No timeout, could hang forever
   subprocess.run(["open", file], timeout=None)

   # SAFE: 30-second timeout by default
   opener = SecureFileOpener(timeout=30)
   opener.open_file(file)  # Raises TimeoutExpired after 30s
   ```

#### Quick Reference

**For simple use cases:**

```python
from mayaLib.pipelineLib.utility.file_opener import open_file_secure

# One-liner for common file types
open_file_secure("/path/to/texture.exr")
```

**For custom validation:**

```python
from mayaLib.pipelineLib.utility.file_opener import SecureFileOpener

opener = SecureFileOpener(
    allowed_extensions={".ma", ".mb"},
    allowed_directories=["/projects/current_show"],
    timeout=60
)
opener.open_file(file_path)
```

**For production pipelines:**

```python
# Configure once, reuse across pipeline
PROJECT_OPENER = SecureFileOpener(
    allowed_extensions={".ma", ".mb", ".fbx", ".abc", ".usd"},
    allowed_directories=[
        "/mnt/projects",
        "/mnt/assets",
        "/mnt/shots"
    ],
    timeout=30
)

# Use in tools
def open_scene_file(path):
    """Open a scene file safely."""
    try:
        PROJECT_OPENER.open_file(path)
    except FileOpenerError as e:
        logger.error(f"Cannot open file: {e}")
        raise
```

## Scope

This security policy covers:

- The DevPyLib Python library (`mayaLib/`, `houdiniLib/`, `blenderLib/`, `prismLib/`)
- Pipeline integration code (`pipelineLib/`)
- Maya plugins (`mayaLib/plugin/`)
- Documentation and configuration files

### Out of Scope

The following are NOT covered by this security policy:

- Third-party DCC applications (Maya, Houdini, Blender)
- External dependencies (PyMEL, numpy, etc.)
- User-created scripts that use DevPyLib

## Security Updates

Security updates will be released as patch versions and announced through:

- GitHub Releases with security labels
- GitHub Security Advisories

Thank you for helping keep DevPyLib and its users safe!
