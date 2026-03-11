#!/usr/bin/env python3
"""Test isStrategic field loading."""

from pathlib import Path
from src.excel_radar.loader import load_config, auto_discover_config, load_excel, validate_entries
from src.excel_radar.builder import build_radar_json

# Test with test-2.xlsx
excel_file = Path("data/test-2.xlsx")
if not excel_file.exists():
    print(f"File not found: {excel_file}")
    exit(1)

print(f"Testing with {excel_file}")

# Auto-discover config
config = auto_discover_config(excel_file, sheet_name="Sheet1", title="Test")
print(f"\nConfig loaded: {config.title}")

# Load entries
raw_entries = load_excel(excel_file, "Sheet1", config, allow_duplicates=False)
print(f"\nLoaded {len(raw_entries)} raw entries")

# Check first entry
if raw_entries:
    first = raw_entries[0]
    print(f"\nFirst entry:")
    print(f"  Name: {first.get('name')}")
    print(f"  isStrategic: {first.get('isStrategic')} (type: {type(first.get('isStrategic'))})")

# Validate entries
entries = validate_entries(raw_entries)
print(f"\nValidated {len(entries)} entries")

# Check first validated entry
if entries:
    first_validated = entries[0]
    print(f"\nFirst validated entry:")
    print(f"  Name: {first_validated.name}")
    print(f"  isStrategic: {first_validated.isStrategic} (type: {type(first_validated.isStrategic)})")
    
    # Check model_dump
    dumped = first_validated.model_dump()
    print(f"\nmodel_dump includes isStrategic: {'isStrategic' in dumped}")
    if 'isStrategic' in dumped:
        print(f"  Value: {dumped['isStrategic']}")

print("\nDone!")

