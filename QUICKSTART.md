# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### 2. Create Sample Data

```bash
# Generate sample Excel file with 20 sales opportunities
python3 create_sample_data.py
```

This creates `data/radar.xlsx` with sample entries across:
- **Rings**: Ready, <1 Year, 1-3 Years, 3+ Years
- **Quadrants**: Infrastructure, Applications, Services, Emerging Tech
- **Statuses**: On Track, At Risk, Blocked, New

### 3. Validate Your Data

```bash
# Check if Excel file is valid
excel-radar validate --input data/radar.xlsx
```

You should see:
```
✅ Validation passed!
   - 20 entries found
   - All rings and quadrants mapped correctly
   - No duplicates
```

### 4. Build the Radar

```bash
# Generate the interactive radar
excel-radar build --input data/radar.xlsx --out dist
```

This creates:
- `dist/radar.json` - Validated and sanitized data
- `dist/index.html` - Interactive visualization
- `dist/app.js` - D3.js rendering logic
- `dist/style.css` - Styling

### 5. Preview Locally

```bash
# Start local server
excel-radar preview --out dist
```

Opens your browser to `http://localhost:5173` with the interactive radar!

## 📝 Customize Your Radar

### Edit the Excel File

Open `data/radar.xlsx` and modify:
- **name**: Opportunity/initiative name
- **ring**: Time horizon (Ready, <1 Year, 1-3 Years, 3+ Years)
- **quadrant**: Category (Infrastructure, Applications, Services, Emerging Tech)
- **status**: Current status (on-track, at-risk, blocked, new)
- **description**: HTML description with details
- **tags**: Comma-separated tags for filtering
- **customer**: Customer name
- **value**: Deal value (affects dot size)
- **owner**: Opportunity owner

### Customize Configuration

Edit `config.yml` to change:
- **Rings**: Time horizons, colors, descriptions
- **Quadrants**: Categories and descriptions
- **Statuses**: Status types and colors
- **Layout**: Sizing, spacing, jitter

Example:
```yaml
rings:
  - id: ready
    name: "Ready"
    order: 0
    color: "#4CAF50"
    description: "Immediate opportunities"
```

### Rebuild After Changes

```bash
# Validate changes
excel-radar validate --input data/radar.xlsx

# Rebuild
excel-radar build --input data/radar.xlsx --out dist

# Preview
excel-radar preview --out dist
```

## 🎯 Interactive Features

Once the radar is running:

1. **Hover** over dots to see quick info
2. **Click** dots to open detailed panel with full description
3. **Search** by name or tags using the search box
4. **Filter** by status using checkboxes
5. **Press Escape** to close detail panel

## 📊 Understanding the Visualization

### Rings (Concentric Circles)
- **Inner ring (Green)**: Ready - Immediate opportunities
- **Second ring (Blue)**: <1 Year - Short-term
- **Third ring (Orange)**: 1-3 Years - Medium-term
- **Outer ring (Gray)**: 3+ Years - Long-term

### Quadrants (Pie Slices)
- **Top-right**: Infrastructure
- **Bottom-right**: Applications
- **Bottom-left**: Services
- **Top-left**: Emerging Tech

### Status Colors
- **Green**: On Track
- **Yellow**: At Risk
- **Red**: Blocked
- **Magenta**: New
- **Purple halo**: Recently added (isNew=true)

### Dot Sizes
Larger dots = Higher value opportunities (based on `value` column)

## 🔧 Advanced Usage

### Export to ThoughtWorks Format

```bash
excel-radar export --format thoughtworks --output dist/radar-tw.json
```

### Custom Port

```bash
excel-radar preview --port 8080
```

### Allow Duplicate Names

```bash
excel-radar build --allow-duplicates
```

### Disable JSON Embedding

```bash
excel-radar build --no-embed-json
```

## 📦 Deployment

### Deploy to GitHub Pages

1. Push to GitHub
2. Enable GitHub Pages in repository settings
3. GitHub Actions will automatically build and deploy

### Deploy to Other Platforms

The `dist/` folder is a complete static site. Upload to:
- Netlify: Drag & drop `dist/` folder
- Vercel: Connect repository
- AWS S3: `aws s3 sync dist/ s3://your-bucket/`
- Azure Static Web Apps: Connect repository

## 🆘 Troubleshooting

### "Command not found: excel-radar"

Make sure you've installed the package:
```bash
pip install -e .
```

### "Excel file not found"

Check the path:
```bash
ls -la data/radar.xlsx
```

### "Validation failed: Unknown ring"

Ring names in Excel must match config.yml (case-insensitive):
- "Ready" or "ready" ✅
- "Adopt" ❌ (not in config)

### "Port already in use"

Use a different port:
```bash
excel-radar preview --port 8080
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize `config.yml` for your use case
- Add more entries to `data/radar.xlsx`
- Deploy to production
- Share with your team!

## 💡 Tips

1. **Start small**: Begin with 10-20 entries to test
2. **Use HTML**: Rich descriptions with `<p>`, `<strong>`, `<a>` tags
3. **Tag everything**: Makes searching easier
4. **Update regularly**: Keep the Excel file current
5. **Automate**: Set up CI/CD to rebuild on changes

---

Need help? Check the [README.md](README.md) or open an issue on GitHub!