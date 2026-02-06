"""Build radar.json and copy web assets to dist directory."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from excel_radar.loader import RadarConfig, RadarEntry
from excel_radar.sanitizer import sanitize_description


def build_radar_json(
    config: RadarConfig,
    entries: List[RadarEntry],
    output_path: Path,
) -> Dict[str, Any]:
    """
    Build radar.json from config and entries.
    
    Args:
        config: Radar configuration
        entries: List of validated entries
        output_path: Path to write radar.json
        
    Returns:
        The radar data dictionary
    """
    # Sanitize descriptions
    for entry in entries:
        entry.descriptionHtml = sanitize_description(entry.descriptionHtml)
    
    # Build radar data
    radar_data = {
        "meta": {
            "title": config.title,
            "subtitle": config.subtitle,
            "generatedAt": datetime.utcnow().isoformat() + "Z",
        },
        "rings": [
            {
                "id": ring.id,
                "name": ring.name,
                "order": ring.order,
                "color": ring.color,
                "description": ring.description,
            }
            for ring in sorted(config.rings, key=lambda r: r.order)
        ],
        "quadrants": [
            {
                "id": quad.id,
                "name": quad.name,
                "description": quad.description,
            }
            for quad in config.quadrants
        ],
        "statuses": [
            {
                "id": status.id,
                "name": status.name,
                "color": status.color,
                "description": status.description,
            }
            for status in config.statuses
        ],
        "layout": {
            "startAngleDeg": config.layout.startAngleDeg,
            "padding": config.layout.padding,
            "jitter": config.layout.jitter,
            "minRadius": config.layout.minRadius,
            "maxRadius": config.layout.maxRadius,
            "dotMinSize": config.layout.dotMinSize,
            "dotMaxSize": config.layout.dotMaxSize,
        },
        "entries": [entry.model_dump() for entry in entries],
    }
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(radar_data, f, indent=2, ensure_ascii=False)
    
    return radar_data


def copy_web_assets(web_dir: Path, dist_dir: Path, embed_json: bool = False) -> None:
    """
    Copy web assets (HTML, CSS, JS) to dist directory.
    
    Args:
        web_dir: Source web directory
        dist_dir: Destination dist directory
        embed_json: If True, embed radar.json in HTML for file:// protocol
    """
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    for file_name in ["index.html", "app.js", "style.css"]:
        src = web_dir / file_name
        dst = dist_dir / file_name
        
        if src.exists():
            shutil.copy2(src, dst)
    
    # If embed_json is True, modify index.html to include radar.json
    if embed_json:
        radar_json_path = dist_dir / "radar.json"
        index_html_path = dist_dir / "index.html"
        
        if radar_json_path.exists() and index_html_path.exists():
            with open(radar_json_path, "r", encoding="utf-8") as f:
                radar_data = f.read()
            
            with open(index_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Add embedded JSON before </body>
            embedded_script = f'\n<script type="application/json" id="radar-data">\n{radar_data}\n</script>\n'
            html_content = html_content.replace("</body>", f"{embedded_script}</body>")
            
            with open(index_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)


def build_thoughtworks_json(
    config: RadarConfig,
    entries: List[RadarEntry],
    output_path: Path,
) -> Dict[str, Any]:
    """
    Build ThoughtWorks-compatible radar JSON.
    
    ThoughtWorks format uses:
    - rings as numeric indices (0 = innermost)
    - moved as -1 (out), 0 (unchanged), +1 (in)
    
    Args:
        config: Radar configuration
        entries: List of validated entries
        output_path: Path to write JSON
        
    Returns:
        The ThoughtWorks-compatible data dictionary
    """
    # Create ring index map
    ring_index = {ring.id: ring.order for ring in config.rings}
    
    # Create quadrant index map
    quadrant_index = {quad.id: idx for idx, quad in enumerate(config.quadrants)}
    
    # Convert entries
    tw_entries = []
    for entry in entries:
        # Determine moved value
        moved = 0
        if entry.status == "moved-in":
            moved = 1
        elif entry.status == "moved-out":
            moved = -1
        
        tw_entry = {
            "name": entry.name,
            "ring": ring_index.get(entry.ring, 0),
            "quadrant": quadrant_index.get(entry.quadrant, 0),
            "isNew": entry.isNew or entry.status == "new",
            "moved": moved,
            "description": entry.descriptionHtml,
        }
        
        tw_entries.append(tw_entry)
    
    tw_data = {
        "entries": tw_entries,
    }
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tw_data, f, indent=2, ensure_ascii=False)
    
    return tw_data

# Made with Bob
