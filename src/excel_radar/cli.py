"""Command-line interface for excel-radar using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from excel_radar.builder import (
    build_radar_json,
    build_thoughtworks_json,
    copy_web_assets,
)
from excel_radar.loader import load_config, load_excel, validate_entries
from excel_radar.server import serve_directory
from excel_radar.version import __version__

app = typer.Typer(
    name="excel-radar",
    help="Generate interactive Technology/Strategy Radars from Excel files",
    add_completion=False,
)
console = Console()


@app.command()
def build(
    input: Path = typer.Option(
        "data/radar.xlsx",
        "--input",
        "-i",
        help="Path to Excel file",
        exists=True,
        dir_okay=False,
    ),
    sheet: str = typer.Option(
        "Radar",
        "--sheet",
        "-s",
        help="Sheet name to read",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file (optional if using --auto-config)",
    ),
    auto_config: bool = typer.Option(
        False,
        "--auto-config",
        help="Auto-discover rings and quadrants from Excel (no config file needed)",
    ),
    title: str = typer.Option(
        "Technology Radar",
        "--title",
        help="Radar title (used with --auto-config)",
    ),
    subtitle: str = typer.Option(
        "",
        "--subtitle",
        help="Radar subtitle (used with --auto-config)",
    ),
    out: Path = typer.Option(
        "dist",
        "--out",
        "-o",
        help="Output directory",
    ),
    allow_duplicates: bool = typer.Option(
        False,
        "--allow-duplicates",
        help="Allow duplicate entry names (will append suffix)",
    ),
    embed_json: bool = typer.Option(
        True,
        "--embed-json/--no-embed-json",
        help="Embed radar.json in HTML for file:// protocol support",
    ),
) -> None:
    """
    Build the radar from Excel file.
    
    Reads Excel → validates → sanitizes → generates radar.json → copies web assets.
    
    Use --auto-config to automatically discover rings and quadrants from Excel,
    or provide --config to use a YAML configuration file.
    """
    try:
        console.print("🔧 Building radar...", style="bold blue")
        
        # Load or auto-discover config
        if auto_config:
            console.print(f"🔍 Auto-discovering config from {input}")
            from excel_radar.loader import auto_discover_config
            radar_config = auto_discover_config(input, sheet, title, subtitle)
            console.print(f"✓ Found {len(radar_config.rings)} rings and {len(radar_config.quadrants)} quadrants", style="green")
        elif config:
            console.print(f"📋 Loading config from {config}")
            radar_config = load_config(config)
        else:
            # Try default config.yml, fall back to auto-discovery
            default_config = Path("config.yml")
            if default_config.exists():
                console.print(f"📋 Loading config from {default_config}")
                radar_config = load_config(default_config)
            else:
                console.print(f"🔍 No config file found, auto-discovering from {input}")
                from excel_radar.loader import auto_discover_config
                radar_config = auto_discover_config(input, sheet, title, subtitle)
                console.print(f"✓ Found {len(radar_config.rings)} rings and {len(radar_config.quadrants)} quadrants", style="green")
        
        # Load Excel
        console.print(f"📊 Loading Excel from {input} (sheet: {sheet})")
        raw_entries = load_excel(input, sheet, radar_config, allow_duplicates)
        console.print(f"✓ Found {len(raw_entries)} entries", style="green")
        
        # Validate entries
        console.print("✓ Validating entries...")
        entries = validate_entries(raw_entries)
        
        # Build radar.json
        radar_json_path = out / "radar.json"
        console.print(f"📝 Building {radar_json_path}")
        build_radar_json(radar_config, entries, radar_json_path)
        
        # Copy web assets
        web_dir = Path(__file__).parent.parent.parent / "web"
        console.print(f"📦 Copying web assets to {out}")
        copy_web_assets(web_dir, out, embed_json=embed_json)
        
        console.print(f"\n✅ Build complete! Output: {out.absolute()}", style="bold green")
        console.print(f"\n💡 Run 'excel-radar preview --out {out}' to view locally")
        
    except Exception as e:
        console.print(f"\n❌ Build failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def validate(
    input: Path = typer.Option(
        "data/radar.xlsx",
        "--input",
        "-i",
        help="Path to Excel file",
        exists=True,
        dir_okay=False,
    ),
    sheet: str = typer.Option(
        "Radar",
        "--sheet",
        "-s",
        help="Sheet name to read",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file (optional if using --auto-config)",
    ),
    auto_config: bool = typer.Option(
        False,
        "--auto-config",
        help="Auto-discover rings and quadrants from Excel",
    ),
    allow_duplicates: bool = typer.Option(
        False,
        "--allow-duplicates",
        help="Allow duplicate entry names",
    ),
) -> None:
    """
    Validate Excel file without building.
    
    Checks rings, quadrants, booleans, duplicates, and required fields.
    """
    try:
        console.print("🔍 Validating Excel file...", style="bold blue")
        
        # Load or auto-discover config
        if auto_config:
            console.print(f"🔍 Auto-discovering config from {input}")
            from excel_radar.loader import auto_discover_config
            radar_config = auto_discover_config(input, sheet)
        elif config:
            console.print(f"📋 Loading config from {config}")
            radar_config = load_config(config)
        else:
            default_config = Path("config.yml")
            if default_config.exists():
                console.print(f"📋 Loading config from {default_config}")
                radar_config = load_config(default_config)
            else:
                console.print(f"🔍 No config file found, auto-discovering from {input}")
                from excel_radar.loader import auto_discover_config
                radar_config = auto_discover_config(input, sheet)
        
        # Display config summary
        table = Table(title="Configuration Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Values", style="green")
        
        table.add_row(
            "Rings",
            str(len(radar_config.rings)),
            ", ".join([r.name for r in radar_config.rings]),
        )
        table.add_row(
            "Quadrants",
            str(len(radar_config.quadrants)),
            ", ".join([q.name for q in radar_config.quadrants]),
        )
        table.add_row(
            "Statuses",
            str(len(radar_config.statuses)),
            ", ".join([s.name for s in radar_config.statuses]),
        )
        
        console.print(table)
        
        # Load and validate Excel
        console.print(f"\n📊 Loading Excel from {input} (sheet: {sheet})")
        raw_entries = load_excel(input, sheet, radar_config, allow_duplicates)
        console.print(f"✓ Found {len(raw_entries)} entries", style="green")
        
        # Validate entries
        console.print("✓ Validating entries...")
        entries = validate_entries(raw_entries)
        
        # Display validation summary
        summary_table = Table(title="Validation Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        
        summary_table.add_row("Total Entries", str(len(entries)))
        summary_table.add_row("New Entries", str(sum(1 for e in entries if e.isNew)))
        summary_table.add_row(
            "With Status", str(sum(1 for e in entries if e.status))
        )
        summary_table.add_row(
            "With Description", str(sum(1 for e in entries if e.descriptionHtml))
        )
        
        console.print(summary_table)
        
        console.print("\n✅ Validation passed!", style="bold green")
        
    except Exception as e:
        console.print(f"\n❌ Validation failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def preview(
    out: Path = typer.Option(
        "dist",
        "--out",
        "-o",
        help="Directory to serve",
    ),
    port: int = typer.Option(
        5173,
        "--port",
        "-p",
        help="Port to serve on",
    ),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Don't open browser automatically",
    ),
) -> None:
    """
    Start a local HTTP server to preview the radar.
    
    Serves the dist/ directory on localhost.
    """
    try:
        if not out.exists():
            console.print(
                f"❌ Directory not found: {out}\n"
                f"💡 Run 'excel-radar build' first",
                style="bold red",
            )
            raise typer.Exit(1)
        
        serve_directory(out, port=port, open_browser=not no_browser)
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"❌ Server error: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def export(
    input: Path = typer.Option(
        "data/radar.xlsx",
        "--input",
        "-i",
        help="Path to Excel file",
        exists=True,
        dir_okay=False,
    ),
    sheet: str = typer.Option(
        "Radar",
        "--sheet",
        "-s",
        help="Sheet name to read",
    ),
    config: Path = typer.Option(
        "config.yml",
        "--config",
        "-c",
        help="Path to config file",
        exists=True,
        dir_okay=False,
    ),
    format: str = typer.Option(
        "thoughtworks",
        "--format",
        "-f",
        help="Export format (thoughtworks)",
    ),
    output: Path = typer.Option(
        "dist/radar-thoughtworks.json",
        "--output",
        help="Output file path",
    ),
) -> None:
    """
    Export radar data in alternative formats.
    
    Currently supports ThoughtWorks-compatible JSON format.
    """
    try:
        console.print(f"📤 Exporting to {format} format...", style="bold blue")
        
        # Load config
        radar_config = load_config(config)
        
        # Load Excel
        raw_entries = load_excel(input, sheet, radar_config)
        entries = validate_entries(raw_entries)
        
        # Export based on format
        if format.lower() == "thoughtworks":
            console.print(f"📝 Building ThoughtWorks JSON: {output}")
            build_thoughtworks_json(radar_config, entries, output)
        else:
            console.print(f"❌ Unknown format: {format}", style="bold red")
            raise typer.Exit(1)
        
        console.print(f"✅ Export complete: {output.absolute()}", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"excel-radar version {__version__}", style="bold blue")


if __name__ == "__main__":
    app()

# Made with Bob


@app.command()
def serve(
    data_dir: Path = typer.Option(
        "data",
        "--data",
        "-d",
        help="Data directory containing Excel files",
    ),
    dist_dir: Path = typer.Option(
        "dist",
        "--dist",
        help="Dist directory for built radars",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind to",
    ),
    port: int = typer.Option(
        5173,
        "--port",
        "-p",
        help="Port to bind to",
    ),
    debug: bool = typer.Option(
        True,
        "--debug/--no-debug",
        help="Enable debug mode",
    ),
) -> None:
    """
    Start the unified interface server with REST API.
    
    Provides a web interface for managing multiple radar projects,
    editing Excel data, and viewing radars interactively.
    """
    try:
        from excel_radar.api import RadarAPI
        
        console.print("🚀 Starting unified interface server...", style="bold blue")
        console.print(f"📁 Data directory: {data_dir.absolute()}")
        console.print(f"📦 Dist directory: {dist_dir.absolute()}")
        console.print(f"🌐 Server: http://{host}:{port}")
        console.print("\n💡 Press Ctrl+C to stop the server\n")
        
        api = RadarAPI(data_dir=str(data_dir), dist_dir=str(dist_dir))
        api.run(host=host, port=port, debug=debug)
        
    except ImportError:
        console.print(
            "\n❌ Flask not installed. Install with: pip install flask flask-cors",
            style="bold red"
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n\n👋 Server stopped", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Server failed: {e}", style="bold red")
        raise typer.Exit(1)
