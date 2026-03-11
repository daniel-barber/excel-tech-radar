# Configuration Examples

This directory contains example configuration files for different environments.

## Files

### `development.yml`
Configuration for local development:
- Debug mode enabled
- Verbose logging
- Relaxed security settings
- Shorter backup retention

### `production.yml`
Configuration for production deployment:
- Debug mode disabled
- JSON logging for aggregation
- Strict security settings
- Longer backup retention
- Performance optimizations

## Usage

### Option 1: Environment Variables (Recommended)

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your settings
```

Then start the server:

```bash
excel-radar serve
```

### Option 2: Configuration File

Use a specific configuration file:

```bash
# Development
export RADAR_CONFIG=config/development.yml
excel-radar serve

# Production
export RADAR_CONFIG=config/production.yml
excel-radar serve
```

### Option 3: Mix Both

Environment variables override configuration file settings:

```bash
export RADAR_CONFIG=config/production.yml
export RADAR_PORT=9000  # Override port from config file
excel-radar serve
```

## Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. Default values (in code)
2. Configuration file (if specified)
3. Environment variables
4. Command-line arguments

## Environment Variables

All configuration options can be set via environment variables with the `RADAR_` prefix:

```bash
RADAR_HOST=0.0.0.0
RADAR_PORT=8080
RADAR_DEBUG=false
RADAR_DATA_DIR=/var/lib/radar/data
RADAR_LOG_LEVEL=INFO
RADAR_MAX_BACKUPS=10
```

See `.env.example` for a complete list of available variables.

## Security Notes

### Production Checklist

- [ ] Set `RADAR_DEBUG=false`
- [ ] Generate a secure `RADAR_SECRET_KEY`
- [ ] Configure `RADAR_ALLOWED_ORIGINS` (don't use `*`)
- [ ] Set appropriate file permissions on data directory
- [ ] Enable HTTPS/TLS at reverse proxy level
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backup strategy

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Docker

When using Docker, mount configuration as a volume:

```bash
docker run -v $(pwd)/config/production.yml:/app/config.yml \
           -e RADAR_CONFIG=/app/config.yml \
           excel-radar
```

Or use environment variables:

```bash
docker run --env-file .env excel-radar
```
