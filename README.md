# Excel Tech Radar

A production-ready web application for creating and managing interactive technology radar visualizations from Excel data. Perfect for tracking projects, initiatives, technology adoption, and strategic planning.

## ✨ Features

### Core Capabilities
- 📊 **Interactive Radar Visualization** - D3.js-powered circular radar with zoom/pan
- 📝 **Excel-Based Storage** - All data in simple .xlsx files (no database required)
- 🎨 **Fully Customizable** - Configure rings, categories, and visual appearance
- 🔍 **Advanced Search & Filter** - Find entries by name, ring, category, deal size, or propensity
- 📸 **PNG Export** - Generate high-quality images for presentations
- ✏️ **Live Editing** - Edit entries directly in the web interface
- 🔗 **Rich Content** - HTML descriptions, external links, and tags
- 🏢 **Multi-Project Management** - Manage multiple radars in one interface

### Business Intelligence
- 💰 **Deal Size Visualization** - Circle sizes represent deal values
- 📈 **Propensity to Win** - Color-coded confidence levels (High/Medium/Low)
- ⭐ **Strategic Items** - Highlight strategic initiatives with special markers
- 🏷️ **Classification Badges** - Visual indicators for deal size and propensity

### Production Features
- 🔐 **Security** - Configurable CORS, secret key management, environment-based config
- 📝 **Structured Logging** - JSON and text formats with rotation and retention
- 🔄 **Automated Backups** - Timestamped backups with configurable retention
- 📦 **Export/Import** - ZIP-based project export with all backups
- 🔧 **Health Monitoring** - System metrics, disk usage, memory tracking
- ⏰ **Task Scheduler** - Automated cleanup, backups, and monitoring
- 🐳 **Docker Support** - Production-ready containerization
- 📊 **Storage Management** - Automatic cleanup of old backups and deleted files

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd excel-tech-radar

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Create .env file
cp .env.example .env
# Edit .env and set RADAR_SECRET_KEY

# Start with Docker Compose
docker-compose up -d

# Access application
open http://localhost:8080
```

### Option 2: Local Installation

```bash
# Clone repository
cd excel-tech-radar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[prod]

# Create directories
mkdir -p data dist logs

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
excel-radar serve
```

### First Steps

1. **Access Web UI**: Open http://localhost:8080
2. **Create Project**: Click "New Project" and enter a name
3. **Add Entries**: Click "New Entry" or "Edit Data" to add items
4. **Visualize**: View your interactive radar with filtering
5. **Export**: Generate PNG images for presentations

## 📋 Excel File Format

Your Excel file should have these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| name | Yes | Entry name (unique) | "React", "Kubernetes" |
| ring | Yes | Ring/horizon | "Q1", "Q2", "Adopt", "Trial" |
| quadrant | No | Category/sector | "Languages & Frameworks" |
| dealSize | No | Deal size category | "< $100k", "$100k - $500k", "> $500k" |
| propensityToWin | No | Win probability | "High", "Medium", "Low" |
| isStrategic | No | Strategic flag | TRUE, FALSE |
| description | No | HTML description | "React is a JavaScript library..." |
| tags | No | Comma-separated tags | "frontend, javascript, ui" |
| link | No | External URL | "https://react.dev" |
| linkName | No | Display text for link | "Official Website" |

**Note**: The `status` field has been removed. Use `propensityToWin` and `isStrategic` for better business intelligence.

## ⚙️ Configuration

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

## 📚 Documentation

- **[API Documentation](./API.md)** - Complete REST API reference
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment instructions
- **[Troubleshooting](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[Configuration Guide](./config/README.md)** - Detailed configuration options
- **[Development Guide](./dev/README.md)** - Development scripts and tools

## 🔄 Backup & Maintenance

### Automated Backups
- **Timestamped backups**: Created automatically on every save
- **Configurable retention**: Keep N most recent backups per project
- **Scheduled cleanup**: Daily cleanup of old backups and deleted files
- **Weekly auto-backup**: Optional automated backup of all projects

### Manual Operations
```bash
# Create manual backup
curl -X POST http://localhost:8080/api/projects/my_project/backups

# List backups
curl http://localhost:8080/api/projects/my_project/backups

# Restore from backup
curl -X POST http://localhost:8080/api/projects/my_project/restore

# Export project (with all backups)
curl -X POST http://localhost:8080/api/projects/my_project/export -o export.zip

# Storage statistics
curl http://localhost:8080/api/storage/stats
```

## 🔧 API Endpoints

The application provides a comprehensive REST API:

- **Projects**: CRUD operations, upload, download, export/import
- **Data**: Excel data manipulation, row operations
- **Backups**: Create, list, restore, delete backups
- **Scheduler**: Task management and status
- **Health**: System monitoring and metrics
- **Storage**: Usage statistics

See [API.md](./API.md) for complete documentation.

## 🐳 Docker Deployment

### Quick Start
```bash
docker-compose up -d
```

### Custom Configuration
```yaml
# docker-compose.yml
services:
  radar:
    environment:
      - RADAR_SECRET_KEY=your-secret-key
      - RADAR_MAX_BACKUPS=10
      - RADAR_LOG_FORMAT=json
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Production Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- AWS, Azure, Google Cloud deployment
- Nginx reverse proxy configuration
- SSL/TLS setup
- Monitoring and scaling

## 🔐 Security

### Production Checklist
- [ ] Generate unique `RADAR_SECRET_KEY`
- [ ] Set `RADAR_DEBUG=false`
- [ ] Configure `RADAR_ALLOWED_ORIGINS` (don't use `*`)
- [ ] Use HTTPS with valid SSL certificate
- [ ] Enable firewall and restrict ports
- [ ] Regular security updates
- [ ] Implement authentication (via reverse proxy)
- [ ] Regular backup verification

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8080/api/health
```

Returns system metrics:
- Service status
- Uptime
- Project count
- Disk usage
- Memory usage

### Scheduler Status
```bash
curl http://localhost:8080/api/scheduler/status
```

Shows scheduled task information:
- Task status (enabled/disabled)
- Last run time
- Next run time
- Run count and error count


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