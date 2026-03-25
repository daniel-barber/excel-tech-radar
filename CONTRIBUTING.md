# Contributing to Excel Tech Radar

Thank you for your interest in contributing to Excel Tech Radar! We welcome contributions from the community and appreciate your help in making this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Contributing Code](#contributing-code)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Questions?](#questions)

## Code of Conduct

This project and everyone participating in it is expected to uphold a professional and respectful environment. Please be kind and courteous to others.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [existing issues](https://github.com/daniel-barber/excel-tech-radar/issues) to avoid duplicates.

**To report a bug:**

1. Use the [Bug Report template](https://github.com/daniel-barber/excel-tech-radar/issues/new?template=bug_report.md)
2. Provide a clear and descriptive title
3. Include detailed steps to reproduce the issue
4. Describe the expected vs actual behavior
5. Include your environment details (OS, Python version, etc.)
6. Add screenshots or error logs if applicable

**Before submitting:**
- [ ] Check if the issue exists in the latest version
- [ ] Review the [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [ ] Search existing issues to avoid duplicates

### Suggesting Enhancements

We love hearing ideas for new features and improvements!

**To suggest an enhancement:**

1. Use the [Feature Request template](https://github.com/daniel-barber/excel-tech-radar/issues/new?template=feature_request.md)
2. Clearly describe the feature and its benefits
3. Explain the use case and who would benefit
4. Provide examples or mockups if possible
5. Consider backward compatibility and existing features

**Before submitting:**
- [ ] Check if a similar feature request already exists
- [ ] Consider if this aligns with the project's goals
- [ ] Think about how it would work with existing features

### Contributing Code

We welcome code contributions! Here's how to get started:

#### First Time Contributors

Look for issues labeled `good first issue` - these are great starting points for new contributors.

#### Development Workflow

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/excel-tech-radar.git
   cd excel-tech-radar
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set up development environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e .[dev]
   
   # Create necessary directories
   mkdir -p data dist logs
   ```

4. **Make your changes**
   - Write clear, readable code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Test the application
   excel-radar serve
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```
   
   **Commit message guidelines:**
   - Use present tense ("Add feature" not "Added feature")
   - Use imperative mood ("Move cursor to..." not "Moves cursor to...")
   - First line should be 50 characters or less
   - Reference issues and pull requests when relevant

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with details about your changes

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Modern web browser

### Local Development

```bash
# Clone the repository
git clone https://github.com/daniel-barber/excel-tech-radar.git
cd excel-tech-radar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Start development server
excel-radar serve --debug
```

### Project Structure

```
excel-tech-radar/
├── src/excel_radar/     # Python backend
│   ├── api.py          # REST API endpoints
│   ├── server.py       # Flask server
│   ├── loader.py       # Excel data loading
│   └── ...
├── web/                # Web interface
│   ├── index.html      # Main HTML
│   ├── app.js          # JavaScript
│   └── style.css       # Styles
├── tests/              # Unit tests
├── docs/               # Documentation
└── templates/          # Excel templates
```

## Pull Request Process

1. **Update documentation** - If you've added features, update the README.md and relevant docs
2. **Add tests** - Ensure your code is covered by tests
3. **Update CHANGELOG** - Add a note about your changes (if applicable)
4. **Ensure CI passes** - All automated tests must pass
5. **Request review** - Tag maintainers for review
6. **Address feedback** - Make requested changes promptly
7. **Squash commits** - Clean up your commit history if needed

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows the project's style guidelines
- [ ] Tests pass locally (`pytest`)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included
- [ ] PR description clearly explains the changes

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

```python
def load_excel_data(file_path: str) -> dict:
    """
    Load and parse Excel data from the specified file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary containing parsed radar data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    # Implementation here
    pass
```

### JavaScript Code Style

- Use ES6+ features
- Use `const` and `let`, avoid `var`
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting

## Questions?

If you have questions about contributing:

1. Check the [Documentation](./README.md)
2. Review [existing issues](https://github.com/daniel-barber/excel-tech-radar/issues)
3. Ask in [GitHub Discussions](https://github.com/daniel-barber/excel-tech-radar/discussions)
4. Contact the maintainers: [Daniel Barber](https://github.com/daniel-barber)

## Recognition

Contributors will be recognized in the project's README and release notes. Thank you for helping make Excel Tech Radar better!

---

**Happy Contributing! 🎉**