# MalloryAI Python SDK

## 🚀 Overview
The official Python SDK for the MalloryAI platform, providing seamless API integration. This SDK simplifies interaction with MalloryAI's services while maintaining high code quality standards and consistent development practices.

## 🛠️ Installation

### From PyPI
```sh
pip install malloryai-sdk
```

### For Development
1. **Clone the Repository**
   ```sh
   git clone git@github.com:malloryai/api-sdk.git
   cd api-sdk
   ```

2. **Install Dependencies**
   Make sure you have `pdm` installed, then:
   ```sh
   pdm install
   ```

3. **Install Development Tools**
   ```sh
   pdm install -dG lint test dev
   ./install-commit-hook.sh
   ```

## 📚 Quick Start

```python
from malloryai.sdk.api.v1.api import MalloryIntelligenceClient

# Initialize the client
malloryClient = MalloryIntelligenceClient(api_key="your-api-key")


# Use the SDK
async def main():
   bulletin = await malloryClient.bulletins.list_bulletins(limit=1)
```

## 🧪 Development

### Running Tests
```sh
# Run all tests with coverage
pdm run pytest

# Run specific test files
pdm run pytest tests/v1/bulletins/test_bulletins.py
```

### Code Quality
We use several tools to maintain code quality:
- Black for code formatting
- Flake8 for code linting
- Pre-commit hooks for automated checks

Run quality checks manually:
```sh
pdm run pre-commit run --all-files
```

## 📦 Deployment
The SDK uses GitHub Actions for automated deployment to PyPI. The deployment process is triggered automatically when you push a new version tag.

### Creating a New Release
1. **Update Version**
   Update the version in `pyproject.toml`:
   ```toml
   [project]
   version = "x.y.z"  # Update this
   ```

2. **Create a GitHub Release**
   - Go to the repository's Releases page
   - Click "Draft a new release"
   - Create a new tag (e.g., `vx.y.z`)
   - Fill in the release title and description
   - Click "Publish release"

The GitHub Actions workflow will automatically:
1. Run linting checks
2. Build the package
3. Publish to PyPI using trusted publishing

### Manual Deployment
If needed, you can build and publish manually:
```sh
# Build the package
pdm build

# Publish to PyPI (requires PyPI credentials)
pdm publish
```

## 📝 Commit Convention
We follow the Conventional Commits specification for commit messages:

```
<type>(<optional-scope>): <description>
```

### Types
| Type      | Usage |
|-----------|-------|
| `feat`    | New features |
| `fix`     | Bug fixes |
| `docs`    | Documentation changes |
| `style`   | Code style changes (formatting, etc.) |
| `refactor`| Code refactoring |
| `test`    | Adding or modifying tests |
| `chore`   | Maintenance tasks |

### Examples
✅ Good:
```sh
git commit -m "feat(auth): implement async token refresh"
git commit -m "fix: handle connection timeouts properly"
git commit -m "docs: update authentication examples"
```

❌ Avoid:
```sh
git commit -m "updated code"
git commit -m "fixed stuff"
git commit -m "wip"
```

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch:
   ```sh
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Run tests and quality checks:
   ```sh
   pdm run pytest
   pdm run pre-commit run --all-files
   ```
5. Commit your changes following our commit convention
6. Push and create a Pull Request
