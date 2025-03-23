<div align="center">

![image](https://tomato-suzy-27.tiiny.site/1.png)
# FRIDAY AI CLI

**Forget Refactoring, I Do All Your Coding Now!**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Status](https://img.shields.io/pypi/status/friday-ai-cli.svg)](https://pypi.org/project/friday-ai-cli/)
[![PyPI version](https://badge.fury.io/py/friday-ai-cli.svg)](https://badge.fury.io/py/friday-ai-cli)
[![PyPI Downloads](https://static.pepy.tech/badge/friday-ai-cli/week)](https://pepy.tech/projects/friday-ai-cli)

*A powerful AI-powered CLI tool for developers, built on Anthropic's Claude 3*

[Installation](#installation) •
[Usage](#usage) •
[Features](#features) •
[Documentation](#documentation) •
[Contributing](#contributing)

</div>

---

## Overview

FRIDAY AI CLI is a sophisticated development assistant that leverages Anthropic's Claude 3 to provide intelligent, context-aware software development support. It's designed to streamline development workflows while maintaining high standards of code quality and security.

## Features

### Core Capabilities

- **Intelligent Code Assistance**
  - Project structure optimization
  - Code review and refactoring suggestions
  - Best practices implementation
  - Architecture planning

- **Development Workflow Support**
  - Environment setup automation
  - Dependency management
  - Project scaffolding
  - Documentation generation

- **Interactive Development**
  - Real-time coding assistance
  - Context-aware suggestions
  - Intelligent error resolution
  - Pattern recognition

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Anthropic API key ([Get one here](https://www.anthropic.com/))

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/yashChouriya/friday-ai-cli.git

# Navigate to project directory
cd friday-ai-cli

# Install the package
pip install -e .
```

### API Key Configuration

```bash
# Option 1: Environment variable (recommended)
export ANTHROPIC_API_KEY='your-api-key'

# Option 2: Runtime configuration
friday chat --api-key 'your-api-key'
```

## Usage

### Quick Start

```bash
# Start FRIDAY
friday chat

# Check version
friday version

# License Management
friday add-license YOUR_LICENSE_KEY
friday reset-license
```

### License Management

FRIDAY AI CLI requires a valid license key to operate. When you first run the tool, it will prompt you to provide a license key.

```bash
# Add or update license
friday add-license YOUR_LICENSE_KEY

# Remove current license
friday reset-license

# Check license status
friday version
```

### Common Operations

```bash
# Project initialization
You › Initialize a new Flask REST API project

# Code review
You › Review this Django model implementation

# Environment setup
You › Set up a React development environment
```

## Technical Details

### Architecture

FRIDAY AI CLI is built with a modular architecture focusing on:
- Clean separation of concerns
- Extensible tool integration
- Robust error handling
- Secure operation execution

### Core Components

- **Terminal UI**: Rich-based interactive interface
- **Tool System**: Modular tool integration framework
- **Security Layer**: Permission-based operation execution
- **Claude 3 Integration**: Advanced AI capabilities leveraging Claude 3 Sonnet (claude-3-7-sonnet-20250219)
- **License Management**: Server-based license validation with local caching
- **Encryption System**: Memory-only decryption of protected core modules

### Project Structure

```
friday/
├── cli/                # Command-line interface components
│   ├── commands.py     # CLI command definitions
│   └── __init__.py
├── core/               # Core functionality (encrypted)
│   ├── chat.py         # Chat interaction handling
│   ├── engine.py       # AI integration and core logic
│   └── tools/          # Tool implementations
│       ├── base.py     # Base tool classes
│       ├── bash.py     # Bash command execution
│       ├── collection.py # Tool collection management
│       ├── edit.py     # File editing capabilities
│       └── run.py      # Command execution
├── license/            # License management
│   ├── api_client.py   # Server API communication
│   ├── cli.py          # License CLI commands
│   ├── crypto.py       # Encryption/decryption logic
│   ├── __init__.py
│   ├── manager.py      # License management
│   └── tools.py        # License-related tools
├── ui/                 # User interface components
│   ├── __init__.py
│   ├── loader.py       # Loading animations
│   ├── terminal.py     # Terminal UI components
│   └── welcome.py      # Welcome screen
├── utils/              # Utility functions
│   ├── helpers.py      # Helper utilities
│   └── ocr.py          # OCR capabilities
├── __init__.py
└── main.py             # Application entry point
```

### Development Mode

For contributors and developers:

```python
# Enable development features in engine.py
DEV_MODE = True  # Enables additional logging and debug info
```

### Encryption System

The FRIDAY CLI uses a sophisticated encryption system for IP protection:

1. **Module Protection**:
   - Core modules in `friday/core/` are encrypted during build
   - Encrypted files use Fernet symmetric encryption
   - Files remain encrypted on disk at all times

2. **Decryption Process**:
   - Memory-only decryption at runtime
   - License key verification required for decryption
   - Two-phase module loading to handle dependencies

3. **Development Tools**:
   - `build_encrypted.py` - Manages the encryption build process
   - `encrypt_core.py` - Handles core module encryption
   - `debug_decrypt.py` - Testing tool for decryption verification

## Security

FRIDAY implements several security measures:

- **Operation Safety**
  - Explicit permission requirements
  - Sandbox environments for operations
  - Protected system boundaries

- **Data Protection**
  - Secure credential handling with proper permissions (0o600)
  - API key masking (showing only first/last 4 characters)
  - Local-only file operations
  
- **Source Code Protection**
  - Encrypted core modules with Fernet symmetric encryption
  - License-based decryption with server validation
  - Memory-only decryption of protected code
  - Secure two-phase module loading system
  - Server-based license validation with JWT authentication
  
## License Management

FRIDAY uses a comprehensive license management system:

- **License Validation**
  - Server-based validation with API authentication
  - Fallback to local validation when offline
  - Time-limited licenses with automatic expiration

- **Remote Key Distribution**
  - Secure decryption key distribution from server
  - JWT-authenticated key retrieval
  - Local caching for offline use

- **Flexible Deployment**
  - License server can be self-hosted
  - Docker container available for easy deployment
  - Configurable offline mode for restricted environments

## Interface

### Message Types

| Type | Color | Purpose |
|------|--------|---------|
| User Input | Cyan | Command and query input |
| FRIDAY Response | Green | AI responses and suggestions |
| Tool Execution | Yellow | System operations |
| Operation Output | Blue | Command results |

## Dependencies

Core dependencies are managed through pip:

```plaintext
anthropic>=0.7.0     # Claude 3 API integration
typer>=0.9.0        # CLI framework
rich>=13.3.5        # Terminal formatting
python-dotenv       # Environment management
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support, please:
1. Check the [documentation](#documentation)
2. Create an issue in the repository
3. Contact the maintainer

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Anthropic's Claude 3](https://www.anthropic.com/)
- Maintained by [Yash Chouriya](https://github.com/yashChouriya)

---

<div align="center">

**[⬆ back to top](#friday-ai-cli)**

Made with dedication by Yash Chouriya

</div>
