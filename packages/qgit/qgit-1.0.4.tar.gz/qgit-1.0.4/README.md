# QGit - Quick Git Operations

QGit is a powerful Git operations automation tool that provides enhanced Git workflow management, repository visualization, and security scanning capabilities.

## Requirements

### System Requirements

- Python 3.13.2
- Git 2.20 or higher
- OpenGL support (for visualization features)
- SQLite 3.x (included with Python)

### Platform Support

- Linux (Primary support)
- macOS (Full support with platform-specific optimizations)
- Windows (Basic support)

### Hardware Requirements

- Minimum 4GB RAM
- OpenGL-capable graphics card for visualization features
- 100MB free disk space

## Installation

### Option 1: Using setup.py (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/griffincancode/qgit.git
cd qgit
```

2. Install using setup.py:
```bash
python setup.py install
```

This will:
- Install all required dependencies
- Set up the QGit environment
- Create system-wide executable links
- Configure Git integration
- Set up logging and cache directories

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/griffincancode/qgit.git
cd qgit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Optional Dependencies

For enhanced features, install optional dependencies:
```bash
pip install "pillow>=10.1.0,<11.0.0" "rich>=13.7.0,<14.0.0" "tqdm>=4.66.1,<5.0.0"
```

## Development Setup

For development work, install additional tools:
```bash
pip install -r requirements.txt
pip install "black>=23.11.0,<24.0.0" "flake8>=6.1.0,<7.0.0" "mypy>=1.7.0,<2.0.0" "isort>=5.12.0,<6.0.0" "pytest>=7.4.3,<8.0.0" "pytest-asyncio>=0.23.0,<1.0.0" "pytest-cov>=4.1.0,<5.0.0"
```

## Platform-Specific Notes

### macOS

On macOS, you might need to:
1. Install XQuartz for OpenGL support: https://www.xquartz.org
2. Use `--user` flag during installation:
```bash
python setup.py install --user
```

### Linux

Ensure OpenGL development libraries are installed:
```bash
# Ubuntu/Debian
sudo apt-get install python3-opengl
# Fedora
sudo dnf install python3-opengl
```

### Windows

On Windows:
1. Ensure you have the latest graphics drivers installed
2. Install Visual C++ Build Tools if required
3. Consider using Windows Subsystem for Linux (WSL) for best experience

## Troubleshooting

If you encounter OpenGL-related issues:
1. Update your graphics drivers
2. Ensure OpenGL support is properly installed
3. Try running in a different terminal
4. On macOS, restart your machine after installing XQuartz

For other issues, check the logs in:
- Linux/macOS: `~/.qgit/logs/`
- Windows: `%USERPROFILE%\.qgit\logs\`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 