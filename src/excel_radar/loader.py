"""Excel file loading and validation using pandas and pydantic."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml
from pydantic import BaseModel, Field, field_validator


class RingConfig(BaseModel):
    """Configuration for a radar ring."""

    id: str
    name: str
    order: int
    color: str
    description: Optional[str] = None


class QuadrantConfig(BaseModel):
    """Configuration for a radar quadrant."""

    id: str
    name: str
    description: Optional[str] = None


class StatusConfig(BaseModel):
    """Configuration for entry status."""

    id: str
    name: str
    color: str
    description: Optional[str] = None


class LayoutConfig(BaseModel):
    """Layout configuration for the radar."""

    startAngleDeg: int = 0
    padding: int = 20
    jitter: float = 0.85
    minRadius: int = 80
    maxRadius: int = 400
    dotMinSize: int = 8
    dotMaxSize: int = 40


class ColumnMappings(BaseModel):
    """Column name mappings for Excel file."""

    name: str = "name"
    ring: str = "ring"
    quadrant: str = "quadrant"
    isNew: str = "isNew"
    status: str = "status"
    description: str = "description"
    tags: str = "tags"
    link: str = "link"
    customer: str = "customer"
    value: str = "value"
    owner: str = "owner"


class RadarConfig(BaseModel):
    """Complete radar configuration."""

    title: str
    subtitle: str
    rings: List[RingConfig]
    quadrants: List[QuadrantConfig]
    statuses: List[StatusConfig] = Field(default_factory=list)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    columnMappings: ColumnMappings = Field(default_factory=ColumnMappings)


class RadarEntry(BaseModel):
    """A single radar entry with validation."""

    id: str
    name: str
    ring: str
    quadrant: str
    isNew: bool = False
    status: Optional[str] = None
    descriptionHtml: str = ""
    tags: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    customer: Optional[str] = None
    value: Optional[float] = None
    owner: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any) -> List[str]:
        """Parse tags from comma-separated string or list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        elif isinstance(v, list):
            return [str(tag).strip() for tag in v if str(tag).strip()]
        return []


def slugify(text: str) -> str:
    """
    Convert text to a slug (lowercase, no spaces).
    
    Args:
        text: Text to slugify
        
    Returns:
        Slugified text
    """
    return text.lower().strip().replace(" ", "-").replace("_", "-")


def parse_boolean(value: Any) -> bool:
    """
    Parse various boolean representations.
    
    Accepts: TRUE/FALSE, true/false, 1/0, yes/no, y/n
    
    Args:
        value: Value to parse
        
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    
    if pd.isna(value):
        return False
    
    str_value = str(value).lower().strip()
    
    truthy = {"true", "1", "yes", "y", "t"}
    falsy = {"false", "0", "no", "n", "f", ""}
    
    if str_value in truthy:
        return True
    elif str_value in falsy:
        return False
    else:
        raise ValueError(f"Cannot parse boolean from: {value}")


def load_config(config_path: Path) -> RadarConfig:
    """
    Load radar configuration from YAML file.
    
    Args:
        config_path: Path to config.yml
        
    Returns:
        Validated RadarConfig
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    return RadarConfig(**config_data)


def load_excel(
    excel_path: Path,
    sheet_name: str,
    config: RadarConfig,
    allow_duplicates: bool = False,
) -> List[Dict[str, Any]]:
    """
    Load and validate Excel file.
    
    Args:
        excel_path: Path to Excel file
        sheet_name: Name of sheet to read
        config: Radar configuration
        allow_duplicates: Allow duplicate names (will append suffix)
        
    Returns:
        List of raw entry dictionaries
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        ValueError: If validation fails
    """
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")
    
    # Get column mappings
    col_map = config.columnMappings
    
    # Check required columns exist
    required_cols = [col_map.name, col_map.ring, col_map.quadrant]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Create ID lookup maps
    ring_ids = {slugify(r.name): r.id for r in config.rings}
    ring_ids.update({r.id: r.id for r in config.rings})  # Also accept IDs directly
    
    quadrant_ids = {slugify(q.name): q.id for q in config.quadrants}
    quadrant_ids.update({q.id: q.id for q in config.quadrants})
    
    status_ids = {slugify(s.name): s.id for s in config.statuses}
    status_ids.update({s.id: s.id for s in config.statuses})
    
    entries = []
    seen_names = set()
    
    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row[col_map.name]):
            continue
        
        name = str(row[col_map.name]).strip()
        
        # Check for duplicates
        if name in seen_names:
            if not allow_duplicates:
                raise ValueError(f"Duplicate name found: {name}")
            # Append numeric suffix
            counter = 2
            original_name = name
            while name in seen_names:
                name = f"{original_name} ({counter})"
                counter += 1
        
        seen_names.add(name)
        
        # Map ring
        ring_value = str(row[col_map.ring]).strip() if not pd.isna(row[col_map.ring]) else ""
        ring_slug = slugify(ring_value)
        if ring_slug not in ring_ids:
            raise ValueError(
                f"Row {idx + 2}: Unknown ring '{ring_value}'. "
                f"Valid rings: {[r.name for r in config.rings]}"
            )
        ring_id = ring_ids[ring_slug]
        
        # Map quadrant
        quad_value = str(row[col_map.quadrant]).strip() if not pd.isna(row[col_map.quadrant]) else ""
        quad_slug = slugify(quad_value)
        if quad_slug not in quadrant_ids:
            raise ValueError(
                f"Row {idx + 2}: Unknown quadrant '{quad_value}'. "
                f"Valid quadrants: {[q.name for q in config.quadrants]}"
            )
        quadrant_id = quadrant_ids[quad_slug]
        
        # Parse isNew
        is_new = False
        if col_map.isNew in df.columns and not pd.isna(row[col_map.isNew]):
            try:
                is_new = parse_boolean(row[col_map.isNew])
            except ValueError as e:
                raise ValueError(f"Row {idx + 2}: Invalid isNew value: {e}")
        
        # Map status (optional)
        status_id = None
        if col_map.status in df.columns and not pd.isna(row[col_map.status]):
            status_value = str(row[col_map.status]).strip()
            status_slug = slugify(status_value)
            if status_slug in status_ids:
                status_id = status_ids[status_slug]
        
        # Get description
        description = ""
        if col_map.description in df.columns and not pd.isna(row[col_map.description]):
            description = str(row[col_map.description])
        
        # Get optional fields
        tags = []
        if col_map.tags in df.columns and not pd.isna(row[col_map.tags]):
            tags = str(row[col_map.tags])
        
        link = None
        if col_map.link in df.columns and not pd.isna(row[col_map.link]):
            link = str(row[col_map.link]).strip()
        
        customer = None
        if col_map.customer in df.columns and not pd.isna(row[col_map.customer]):
            customer = str(row[col_map.customer]).strip()
        
        value = None
        if col_map.value in df.columns and not pd.isna(row[col_map.value]):
            try:
                value = float(row[col_map.value])
            except (ValueError, TypeError):
                pass
        
        owner = None
        if col_map.owner in df.columns and not pd.isna(row[col_map.owner]):
            owner = str(row[col_map.owner]).strip()
        
        # Create entry dict
        entry = {
            "id": slugify(name),
            "name": name,
            "ring": ring_id,
            "quadrant": quadrant_id,
            "isNew": is_new,
            "status": status_id,
            "descriptionHtml": description,  # Will be sanitized later
            "tags": tags,
            "link": link,
            "customer": customer,
            "value": value,
            "owner": owner,
        }
        
        entries.append(entry)
    
    if not entries:
        raise ValueError("No valid entries found in Excel file")
    
    return entries


def validate_entries(entries: List[Dict[str, Any]]) -> List[RadarEntry]:
    """
    Validate entries using Pydantic models.
    
    Args:
        entries: List of raw entry dictionaries
        
    Returns:
        List of validated RadarEntry objects
        
    Raises:
        ValueError: If validation fails
    """
    validated = []
    
    for entry in entries:
        try:
            validated.append(RadarEntry(**entry))
        except Exception as e:
            raise ValueError(f"Validation failed for entry '{entry.get('name')}': {e}")
    
    return validated

# Made with Bob
