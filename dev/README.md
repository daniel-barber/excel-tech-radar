# Development Scripts

This directory contains development and testing utilities for the Excel Tech Radar project.

## Scripts

### Template Management

- **`update_template.py`** - Updates the Excel template with new columns or structure
- **`update_propensity_template.py`** - Adds propensity to win column to templates
- **`update_strategic_template.py`** - Adds strategic indicator column to templates

### Testing & Data Generation

- **`create_test_data.py`** - Generates test data for development
- **`test_strategic.py`** - Tests strategic item functionality

## Usage

These scripts are for development purposes only and should not be used in production.

### Example: Create Test Data

```bash
python dev/create_test_data.py
```

### Example: Update Template

```bash
python dev/update_template.py
```

## Notes

- These scripts modify files in the `data/` and `templates/` directories
- Always backup your data before running development scripts
- Scripts are not included in the production build
- For production template creation, use the main `create_template.py` in the root directory
