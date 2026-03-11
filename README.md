# Radar Studio

A web-based visualization tool for creating interactive radar charts from Excel data. Perfect for tracking projects, initiatives, roadmaps, and strategic planning.

## Quick Start

### 1. Install

```bash
# Clone or download this repository
cd excel-tech-radar

# Install dependencies
pip install -e .
```

### 2. Run

```bash
# Start the web interface (opens on http://localhost:8080)
excel-radar serve
```

### 3. Use

- **Create Project**: Click "New Project" and enter a name
- **Add Entries**: Click "New Entry" or "Edit Data" to add items
- **Visualize**: View your radar with interactive filtering and search
- **Export**: Click "Export PNG" to save a snapshot

## Features

- 📊 **Interactive Radar Visualization** - D3.js-powered circular radar with zoom/pan
- 📝 **Excel-Based** - All data stored in simple .xlsx files (no database required)
- 🎨 **Fully Customizable** - Configure rings, categories, and statuses via `config.yml`
- 🔍 **Search & Filter** - Find entries by name, ring, category, or status
- 📸 **PNG Export** - Generate high-quality images for presentations
- ✏️ **Live Editing** - Edit entries directly in the web interface
- 🔗 **Rich Content** - Support for HTML descriptions and external links
- 🏢 **Multi-Project** - Manage multiple radars in one interface

## Excel File Format

Your Excel file should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| name | Yes | Entry name (unique) |
| ring | Yes | Ring/horizon (e.g., "Q1", "Q2", "Q3", "Q4", "Beyond This Year") |
| quadrant | No | Category/sector (e.g., "Data", "Platform") |
| status | No | Status (e.g., "On Track", "At Risk", "New") |
| dealSize | No | Deal size category (e.g., "< $100k", "$100k - $500k", "> $500k") |
| description | No | HTML description with formatting |
| tags | No | Comma-separated tags for filtering |
| link | No | External URL |
| linkName | No | Display text for link |

## Configuration

Edit `config.yml` to customize your radar:

- **Rings**: Define your time horizons, maturity levels, or priority tiers
- **Statuses**: Configure status options with custom colors
- **Deal Sizes**: Define deal size categories that control circle sizes
- **Layout**: Adjust visual appearance (padding, sizing, angles)

Example:
```yaml
rings:
  - id: q1
    name: "Q1"
    order: 0
    color: "#4CAF50"
  - id: q2
    name: "Q2"
    order: 1
    color: "#2196F3"

dealSizes:
  - id: small
    name: "< $100k"
    value: 1
    description: "Small deals under $100k"
  - id: medium
    name: "$100k - $500k"
    value: 2
    description: "Medium deals $100k to $500k"
  - id: large
    name: "> $500k"
    value: 3
    description: "Large deals over $500k"
```

## Environment Configuration

For production deployments, use environment variables to configure the application:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

Key environment variables:
- `RADAR_HOST` - Server host (default: 127.0.0.1)
- `RADAR_PORT` - Server port (default: 8080)
- `RADAR_DEBUG` - Debug mode (default: false)
- `RADAR_DATA_DIR` - Data directory path
- `RADAR_MAX_BACKUPS` - Number of backups to keep (default: 5)
- `RADAR_LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

See `.env.example` for all available options and `config/README.md` for detailed configuration guide.


## Advanced Usage

Most users only need `excel-radar serve`. Additional commands for special cases:

```bash
# Validate Excel file format (troubleshooting)
excel-radar validate --input data/myproject.xlsx

# Build static files for hosting (advanced)
excel-radar build --input data/myproject.xlsx --out dist/
```

## Project Structure

```
excel-tech-radar/
├── data/              # Excel files (one per project)
├── config.yml         # Global configuration
├── src/excel_radar/   # Python backend
├── web/               # Web interface files
├── templates/         # Excel templates
├── tests/             # Unit tests
└── dev/               # Development scripts
```

## Use Cases

- **Project Portfolio Management** - Track project timelines and status
- **Strategic Planning** - Visualize roadmaps and priorities
- **Technology Adoption** - Monitor tech stack evolution
- **Initiative Tracking** - Manage organizational initiatives
- **Team Alignment** - Communicate decisions and plans across teams
- **Vendor Management** - Track vendor relationships and contracts

## Requirements

- Python 3.11+
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Tips

- **Keep it Simple**: Start with just rings and names, add complexity as needed
- **Use Categories Flexibly**: Quadrants are optional - use them only if they add value
- **Deal Sizes**: Use the dealSize column to visually emphasize larger opportunities with bigger circles
- **Rich Descriptions**: Use HTML formatting for better readability
- **Export Often**: Generate PNGs for presentations and documentation
- **Multiple Projects**: Create separate Excel files for different teams or initiatives

## Support

For issues or questions, contact the development team or refer to the inline documentation in the code.

---

**Version**: 1.0.0  
**License**: MIT  
**Author**: [Daniel Barber]https://github.com/daniel-barber)  