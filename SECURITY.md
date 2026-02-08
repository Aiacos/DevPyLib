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
