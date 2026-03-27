# Requirements Files Specification

## requirements.txt

This file will contain all dependencies needed for production use:

### Base Dependencies (from pyproject.toml dependencies)
```
pandas>=2.0.0
openpyxl>=3.1.0
pydantic>=2.0.0
pyyaml>=6.0
bleach>=6.0.0
typer>=0.9.0
rich>=13.0.0
flask>=3.0.0
flask-cors>=4.0.0
```

### Production Dependencies (from pyproject.toml [project.optional-dependencies].prod)
```
python-dotenv>=1.0.0
gunicorn>=21.0.0
psutil>=5.9.0
```

**Total: 12 dependencies**

## requirements-dev.txt

This file will contain all dependencies needed for development:

### Include Production Requirements
```
-r requirements.txt
```

### Development Dependencies (from pyproject.toml [project.optional-dependencies].dev)
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
```

**Total: 12 (from requirements.txt) + 5 (dev-specific) = 17 dependencies**

## Updated Installation Instructions

### For Production Use
```bash
# Clone repository
cd excel-tech-radar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

# Create directories
mkdir -p data dist logs

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
excel-radar serve
```

### For Development
```bash
# Clone repository
cd excel-tech-radar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies (including dev tools)
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .

# Run tests
pytest
```

## Benefits

1. **Reliability**: Works on all platforms without shell escaping issues
2. **Simplicity**: Standard Python practice that developers recognize
3. **Clarity**: Clear separation between production and development dependencies
4. **Compatibility**: Works with pip freeze for version locking
5. **CI/CD Friendly**: Easy to use in automated pipelines

## Migration Notes

Users currently using `pip install -e .[prod]` can migrate to:
```bash
pip install -r requirements.txt
pip install -e .
```

The functionality is identical, but the new method is more reliable.