# Excel Tech Radar

Generate interactive Technology/Strategy Radars from Excel files. Perfect for visualizing sales opportunities, technology adoption, or strategic initiatives across time horizons.

![Radar Preview](docs/radar-preview.png)

## Features

- 📊 **Excel-based input** - Update a simple Excel file, run one command
- 🎯 **Time-based rings** - Ready, <1 Year, 1-3 Years, 3+ Years
- 🎨 **Flexible configuration** - Customize quadrants, rings, and status colors via YAML
- 🔍 **Interactive visualization** - Search, filter, hover tooltips, detail panels
- 🚀 **Static site output** - No server required, works offline
- 🔒 **HTML sanitization** - Safe rendering of rich descriptions
- 📱 **Responsive design** - Works on desktop and mobile
- ♿ **Accessible** - Keyboard navigation and ARIA labels

## Quick Start

### Two Ways to Use

**Option 1: Auto-Discovery (Simplest)**
Just maintain your Excel file - rings and quadrants are automatically discovered:
```bash
excel-radar build --auto-config --input data/radar.xlsx
```

**Option 2: With Config File (More Control)**
Use a YAML config file for custom colors, descriptions, and layout:
```bash
excel-radar build --config config.yml --input data/radar.xlsx
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/excel-tech-radar.git
cd excel-tech-radar

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Create Sample Data

```bash
# Generate sample Excel file
python create_sample_data.py
```

This creates `data/radar.xlsx` with 20 sample sales/opportunity entries.

### Build the Radar

```bash
# Auto-discovery mode (simplest - no config file needed)
excel-radar build --auto-config --input data/radar.xlsx --out dist

# Or with config file for custom colors/layout
excel-radar build --config config.yml --input data/radar.xlsx --out dist

# Preview locally
excel-radar preview --out dist
```

Open your browser to `http://localhost:5173` to see the interactive radar!

## Usage

### Commands

#### `build` - Generate the radar

**Auto-Discovery Mode (Recommended for Quick Start):**
```bash
excel-radar build --auto-config --input data/radar.xlsx --out dist
```

Automatically discovers rings and quadrants from your Excel file. Just add new rings/quadrants to Excel and they'll appear in the radar!

**With Config File (For Custom Styling):**
```bash
excel-radar build \
  --config config.yml \
  --input data/radar.xlsx \
  --out dist
```

**Options:**
- `--input, -i`: Path to Excel file (default: `data/radar.xlsx`)
- `--sheet, -s`: Sheet name to read (default: `Radar`)
- `--config, -c`: Path to config file (optional)
- `--auto-config`: Auto-discover rings/quadrants from Excel (no config needed)
- `--title`: Radar title (used with --auto-config, default: "Technology Radar")
- `--subtitle`: Radar subtitle (used with --auto-config)
- `--out, -o`: Output directory (default: `dist`)
- `--allow-duplicates`: Allow duplicate entry names (appends suffix)
- `--embed-json/--no-embed-json`: Embed JSON in HTML for offline use (default: enabled)

**Note:** If neither `--config` nor `--auto-config` is specified, the tool will:
1. Look for `config.yml` in the current directory
2. If not found, automatically discover from Excel

#### `validate` - Check Excel file

```bash
excel-radar validate --input data/radar.xlsx
```

Validates rings, quadrants, booleans, duplicates, and required fields without building.

#### `preview` - Start local server

```bash
excel-radar preview --out dist --port 5173
```

**Options:**
- `--out, -o`: Directory to serve (default: `dist`)
- `--port, -p`: Port number (default: `5173`)
- `--no-browser`: Don't open browser automatically

#### `export` - Export to other formats

```bash
excel-radar export --format thoughtworks --output dist/radar-tw.json
```

Export to ThoughtWorks-compatible JSON format.

#### `version` - Show version

```bash
excel-radar version
```

## Excel File Format

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Entry name (unique) | "AWS Migration Phase 1" |
| `ring` | string | Time horizon | "Ready", "Less Than 1 Year", "1-3 Years", "3+ Years" |
| `quadrant` | string | Category | "Infrastructure", "Applications", "Services", "Emerging Tech" |

### Optional Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `isNew` | boolean | New entry indicator | TRUE, FALSE, 1, 0, yes, no |
| `status` | string | Current status | "on-track", "at-risk", "blocked", "new" |
| `description` | string | HTML description | `<p>Details about the opportunity...</p>` |
| `tags` | string | Comma-separated tags | "cloud,aws,migration" |
| `link` | string | External URL | "https://example.com/details" |
| `customer` | string | Customer name | "Acme Corp" |
| `value` | number | Deal value (for sizing) | 500000 |
| `owner` | string | Opportunity owner | "John Smith" |

### Example Row

```
name: AWS Migration Phase 1
ring: Ready
quadrant: Infrastructure
isNew: FALSE
status: on-track
description: <p><strong>AWS Migration Phase 1</strong> involves moving critical workloads...</p>
tags: cloud,aws,migration
link: https://example.com/aws-migration
customer: Acme Corp
value: 500000
owner: John Smith
```

## Configuration

### Auto-Discovery vs Config File

**Auto-Discovery Mode** (Recommended for most users):
- ✅ **Zero configuration** - just edit Excel
- ✅ **Maximum flexibility** - add/remove rings and quadrants anytime
- ✅ **No sync issues** - Excel is the single source of truth
- ✅ **Quick iteration** - change structure without editing YAML
- ⚠️ Uses default colors (green, blue, amber, grey cycle)

**Config File Mode** (For advanced customization):
- ✅ **Custom colors** for each ring
- ✅ **Custom descriptions** for rings, quadrants, statuses
- ✅ **Layout control** (padding, jitter, dot sizes)
- ✅ **Column name mapping** (if your Excel uses different column names)
- ⚠️ Must keep config.yml in sync with Excel

### Config File Format

Edit `config.yml` to customize your radar:

### Rings (Time Horizons)

```yaml
rings:
  - id: ready
    name: "Ready"
    order: 0
    color: "#4CAF50"
    description: "Immediate/Current opportunities"
  
  - id: year1
    name: "Less Than 1 Year"
    order: 1
    color: "#2196F3"
```

### Quadrants (Categories)

```yaml
quadrants:
  - id: infrastructure
    name: "Infrastructure"
    description: "Infrastructure and platform solutions"
  
  - id: applications
    name: "Applications"
    description: "Application and software solutions"
```

### Statuses

```yaml
statuses:
  - id: on-track
    name: "On Track"
    color: "#4CAF50"
    description: "Progressing as planned"
  
  - id: at-risk
    name: "At Risk"
    color: "#FFC107"
    description: "Needs attention"
```

### Layout

```yaml
layout:
  startAngleDeg: 0        # 0° at right; clockwise
  padding: 20             # px between rings
  jitter: 0.85            # 0..1 random jitter factor
  minRadius: 80           # minimum radius for innermost ring
  maxRadius: 400          # maximum radius for outermost ring
  dotMinSize: 8           # minimum dot size
  dotMaxSize: 40          # maximum dot size (based on value)
```

## Visualization Features

### Interactive Elements

- **Hover**: Shows tooltip with name, ring, quadrant, and status
- **Click**: Opens detail panel with full description and metadata
- **Search**: Filter entries by name or tags
- **Keyboard**: Press `Escape` to close detail panel

### Status Indicators

- **Green** (On Track): Progressing as planned
- **Yellow** (At Risk): Needs attention
- **Red** (Blocked): Critical issues
- **Magenta** (New): Recently added
- **Purple halo**: `isNew=true` entries

### Dot Sizing

Dots are sized based on the `value` column (if provided), making high-value opportunities more prominent.

## Development

### Project Structure

```
excel-tech-radar/
├── README.md
├── config.yml              # Radar configuration
├── pyproject.toml          # Python dependencies
├── create_sample_data.py   # Sample data generator
├── data/
│   └── radar.xlsx          # Input Excel file
├── src/
│   └── excel_radar/
│       ├── __init__.py
│       ├── version.py
│       ├── cli.py          # CLI commands
│       ├── loader.py       # Excel loading & validation
│       ├── sanitizer.py    # HTML sanitization
│       ├── builder.py      # JSON generation
│       └── server.py       # Preview server
├── web/
│   ├── index.html          # Radar HTML template
│   ├── app.js              # D3.js visualization
│   └── style.css           # Styling
├── dist/                   # Build output (generated)
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── radar.json
└── tests/
    ├── test_validation.py
    ├── test_sanitize.py
    └── test_build_json.py
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=excel_radar --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Deployment

### GitHub Pages

The repository includes a GitHub Actions workflow that automatically builds and deploys to GitHub Pages on push to `main`.

1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Push to `main` branch
4. Radar will be available at `https://yourusername.github.io/excel-tech-radar/`

### Manual Deployment

The `dist/` folder is a complete static site. Deploy to any static hosting:

```bash
# Build
excel-radar build

# Deploy dist/ folder to:
# - GitHub Pages
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - Azure Static Web Apps
# - Any web server
```

## Use Cases

### Sales & Opportunity Tracking

Track sales opportunities across time horizons (Ready, <1 Year, 1-3 Years, 3+ Years) and categories (Infrastructure, Applications, Services, Emerging Tech).

### Technology Adoption

Visualize technology adoption stages (Adopt, Trial, Assess, Hold) across domains (Techniques, Tools, Platforms, Languages).

### Strategic Planning

Map strategic initiatives across time horizons and business units.

### Product Roadmap

Display product features and their expected delivery timeframes.

## Troubleshooting

### "Module not found" errors

Make sure you've installed the package:
```bash
pip install -e .
```

### Excel file not found

Check the path and ensure the file exists:
```bash
ls -la data/radar.xlsx
```

### Validation errors

Run validate command to see detailed error messages:
```bash
excel-radar validate --input data/radar.xlsx
```

### Port already in use

Use a different port:
```bash
excel-radar preview --port 8080
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- Inspired by [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar)
- Built with [D3.js](https://d3js.org/)
- Uses [pandas](https://pandas.pydata.org/), [pydantic](https://pydantic.dev/), and [typer](https://typer.tiangolo.com/)

## Support

- 📖 [Documentation](https://github.com/yourusername/excel-tech-radar)
- 🐛 [Issue Tracker](https://github.com/yourusername/excel-tech-radar/issues)
- 💬 [Discussions](https://github.com/yourusername/excel-tech-radar/discussions)

---

Made with ❤️ for visualizing strategic initiatives