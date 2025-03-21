# 🤖 Claudine Development Guide

This guide provides information for developers who want to contribute to Claudine, a Python wrapper for the Anthropic Claude API.

## 📦 Source Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claudine.git
cd claudine

# Install in editable mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## 🧪 Running Tests

```bash
# Run tests with pytest
pytest

# Run tests with coverage
pytest --cov=claudine
```

## 🏗️ Building Documentation

```bash
# Build documentation
cd docs
make html
```

## 🚀 Development Workflow

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Add tests for your changes
4. Run the test suite to ensure everything passes
5. Submit a pull request

## 📜 Code Style

This project follows PEP 8 style guidelines. You can use tools like `flake8` and `black` to ensure your code conforms to the style guidelines.

```bash
# Check code style
flake8 claudine

# Format code
black claudine
```

## 📄 License

MIT