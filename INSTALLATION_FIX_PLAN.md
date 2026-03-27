# Installation Fix Plan

## Problem Analysis

The current README Option 3 installation instructions use `pip install -e .[prod]` which has several issues:

1. **Shell Escaping Issues**: Square brackets `[]` are special characters in bash/zsh and need to be escaped or quoted
2. **Cross-Platform Compatibility**: The syntax doesn't work consistently across different shells and operating systems
3. **User Confusion**: Non-Python developers find the syntax confusing and non-intuitive
4. **Missing Standard Files**: Python projects typically include `requirements.txt` for dependency management

## Solution

### 1. Create requirements.txt
Create a `requirements.txt` file that includes:
- All base dependencies from `pyproject.toml` dependencies section
- All production dependencies from `[project.optional-dependencies].prod`

This provides a standard, reliable way to install dependencies that works across all platforms.

### 2. Create requirements-dev.txt (Optional)
Create a `requirements-dev.txt` file for development dependencies:
- Includes all base and prod dependencies via `-r requirements.txt`
- Adds all dev dependencies from `[project.optional-dependencies].dev`

### 3. Update README.md
Replace the problematic installation command with:
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

This approach:
- Works on all platforms and shells
- Is familiar to Python developers
- Is easier for non-Python developers to understand
- Follows Python community best practices

## Implementation Steps

1. ✅ Analyze current pyproject.toml dependencies
2. 🔄 Create requirements.txt with base + prod dependencies
3. 📝 Create requirements-dev.txt with dev dependencies
4. 📝 Update README.md Option 3 installation instructions
5. ✅ Verify solution addresses the reported issue

## Files to Modify

- `requirements.txt` (CREATE)
- `requirements-dev.txt` (CREATE)
- `README.md` (UPDATE lines 102-124)

## Expected Outcome

Users will be able to install the project reliably using standard Python tools:
```bash
pip install -r requirements.txt
pip install -e .
```

This eliminates shell escaping issues and provides a consistent experience across all platforms.