# Excel Tech Radar - Troubleshooting Guide

Common issues and solutions for Excel Tech Radar.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Server Issues](#server-issues)
- [Docker Issues](#docker-issues)
- [Data Issues](#data-issues)
- [Performance Issues](#performance-issues)
- [Backup Issues](#backup-issues)
- [Scheduler Issues](#scheduler-issues)
- [Logging Issues](#logging-issues)
- [Security Issues](#security-issues)

## Installation Issues

### Python Version Error

**Problem:** `ERROR: Python 3.9 or higher is required`

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.11 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Use specific Python version
python3.11 -m venv venv
```

### Dependency Installation Fails

**Problem:** `pip install` fails with compilation errors

**Solution:**
```bash
# Install build dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev build-essential

# Install build dependencies (macOS)
xcode-select --install

# Try installing with --no-cache-dir
pip install --no-cache-dir -e .[prod]
```

### Module Not Found Error

**Problem:** `ModuleNotFoundError: No module named 'excel_radar'`

**Solution:**
```bash
# Ensure you're in the project directory
cd excel-tech-radar

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .
```

## Server Issues

### Port Already in Use

**Problem:** `Address already in use: 8080`

**Solution:**
```bash
# Find process using port 8080
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
RADAR_PORT=8081 python -m excel_radar.cli serve
```

### Server Won't Start

**Problem:** Server starts but immediately exits

**Solution:**
```bash
# Check logs for errors
tail -f logs/radar.log

# Run in debug mode
RADAR_DEBUG=true RADAR_LOG_LEVEL=DEBUG python -m excel_radar.cli serve

# Check configuration
python -c "from excel_radar.config import load_config; print(load_config().to_dict())"
```

### Cannot Connect to Server

**Problem:** `Connection refused` when accessing http://localhost:8080

**Solution:**
```bash
# Check if server is running
curl http://localhost:8080/api/health

# Check firewall
sudo ufw status  # Linux
sudo firewall-cmd --list-all  # RHEL/CentOS

# Check if bound to correct interface
# Change RADAR_HOST=0.0.0.0 to listen on all interfaces
```

### 500 Internal Server Error

**Problem:** API returns 500 errors

**Solution:**
```bash
# Check logs
tail -f logs/radar.log

# Enable debug mode temporarily
RADAR_DEBUG=true python -m excel_radar.cli serve

# Check disk space
df -h

# Check permissions
ls -la data/
```

## Docker Issues

### Docker Build Fails

**Problem:** `docker build` fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Build with no cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build --progress=plain .
```

### Container Exits Immediately

**Problem:** Container starts then exits

**Solution:**
```bash
# Check container logs
docker-compose logs radar

# Run container interactively
docker-compose run --rm radar bash

# Check health status
docker-compose ps
docker inspect excel-tech-radar
```

### Volume Permission Issues

**Problem:** Permission denied errors in container

**Solution:**
```bash
# Fix ownership (Linux)
sudo chown -R 1000:1000 data/ logs/

# Or run container as root (not recommended)
docker-compose run --user root radar bash
```

### Cannot Access Container

**Problem:** Cannot access http://localhost:8080 with Docker

**Solution:**
```bash
# Check port mapping
docker-compose ps
docker port excel-tech-radar

# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs -f radar

# Verify RADAR_HOST is set to 0.0.0.0
docker-compose exec radar env | grep RADAR_HOST
```

## Data Issues

### Excel File Corrupted

**Problem:** "Cannot read Excel file" error

**Solution:**
```bash
# Restore from backup
curl -X POST http://localhost:8080/api/projects/my_project/restore

# Or manually restore
cp data/my_project.xlsx.bak.20260311_100000 data/my_project.xlsx

# Verify file integrity
python -c "import pandas as pd; pd.read_excel('data/my_project.xlsx')"
```

### Missing Data Directory

**Problem:** `FileNotFoundError: data directory not found`

**Solution:**
```bash
# Create data directory
mkdir -p data dist logs

# Set correct permissions
chmod 755 data dist logs

# Check configuration
echo $RADAR_DATA_DIR
```

### Duplicate Entries

**Problem:** Radar shows duplicate entries

**Solution:**
```bash
# Check Excel file for duplicates
# The system should prevent duplicates, but check manually

# Rebuild radar
curl -X POST http://localhost:8080/api/projects/my_project/build

# Or use CLI
python -m excel_radar.cli build data/my_project.xlsx
```

### Invalid Excel Format

**Problem:** "Invalid Excel format" error

**Solution:**
```bash
# Ensure file is .xlsx (not .xls)
# Check required columns exist: name, ring, quadrant

# Download template
curl -O http://localhost:8080/api/template/download

# Validate Excel file
python -c "
from excel_radar.loader import load_excel, auto_discover_config
config = auto_discover_config('data/my_project.xlsx', 'Sheet1')
entries = load_excel('data/my_project.xlsx', 'Sheet1', config)
print(f'Loaded {len(entries)} entries')
"
```

## Performance Issues

### Slow Response Times

**Problem:** API responses are slow

**Solution:**
```bash
# Increase Gunicorn workers
gunicorn --workers 8 src.excel_radar.server:app

# Check system resources
top
htop
docker stats  # For Docker

# Check disk I/O
iostat -x 1

# Optimize backups
# Reduce RADAR_MAX_BACKUPS
# Increase RADAR_RETENTION_DAYS cleanup interval
```

### High Memory Usage

**Problem:** Server uses too much memory

**Solution:**
```bash
# Check memory usage
free -h
docker stats excel-tech-radar

# Reduce Gunicorn workers
gunicorn --workers 2 src.excel_radar.server:app

# Set memory limits (Docker)
# Add to docker-compose.yml:
# mem_limit: 1g
# mem_reservation: 512m
```

### Large File Upload Fails

**Problem:** Cannot upload large Excel files

**Solution:**
```bash
# Increase upload size limit
export RADAR_MAX_UPLOAD_SIZE=100  # MB

# For Nginx reverse proxy, add:
# client_max_body_size 100M;

# Increase timeout
export RADAR_REQUEST_TIMEOUT=300  # seconds
```

## Backup Issues

### Backup Creation Fails

**Problem:** "Failed to create backup" error

**Solution:**
```bash
# Check disk space
df -h data/

# Check permissions
ls -la data/

# Manually create backup
cp data/my_project.xlsx data/my_project.xlsx.bak.$(date +%Y%m%d_%H%M%S)

# Check backup manager logs
grep "backup" logs/radar.log
```

### Too Many Backups

**Problem:** Disk filling up with backups

**Solution:**
```bash
# Reduce max backups
export RADAR_MAX_BACKUPS=3

# Run cleanup manually
curl -X POST http://localhost:8080/api/maintenance/cleanup

# Or via CLI
python -c "
from excel_radar.backup_manager import BackupManager
from pathlib import Path
bm = BackupManager(Path('data'), max_backups=3)
stats = bm.cleanup_all_backups()
print(stats)
"
```

### Restore Fails

**Problem:** Cannot restore from backup

**Solution:**
```bash
# List available backups
curl http://localhost:8080/api/projects/my_project/backups

# Try specific backup
curl -X POST http://localhost:8080/api/projects/my_project/restore \
  -H "Content-Type: application/json" \
  -d '{"backup_timestamp": "20260311_100000"}'

# Manual restore
cp data/my_project.xlsx.bak.20260311_100000 data/my_project.xlsx
```

## Scheduler Issues

### Scheduler Not Running

**Problem:** Scheduled tasks not executing

**Solution:**
```bash
# Check scheduler status
curl http://localhost:8080/api/scheduler/status

# Start scheduler
curl -X POST http://localhost:8080/api/scheduler/start

# Check configuration
echo $RADAR_ENABLE_SCHEDULER

# Check logs
grep "scheduler" logs/radar.log
```

### Task Execution Fails

**Problem:** Scheduled task shows errors

**Solution:**
```bash
# Check task status
curl http://localhost:8080/api/scheduler/status | jq '.tasks'

# Check error count
# If error_count > 0, check logs

# Disable problematic task
curl -X POST http://localhost:8080/api/scheduler/tasks/daily_cleanup/disable

# Fix issue and re-enable
curl -X POST http://localhost:8080/api/scheduler/tasks/daily_cleanup/enable
```

### Tasks Running Too Frequently

**Problem:** Tasks executing more often than expected

**Solution:**
```bash
# Check task intervals
curl http://localhost:8080/api/scheduler/status | jq '.tasks[].interval_hours'

# Intervals are set in scheduler.py:
# - daily_cleanup: 24 hours
# - weekly_auto_backup: 168 hours (7 days)
# - storage_monitor: 1 hour

# Restart scheduler to reset timers
curl -X POST http://localhost:8080/api/scheduler/stop
curl -X POST http://localhost:8080/api/scheduler/start
```

## Logging Issues

### No Logs Generated

**Problem:** Log file is empty or not created

**Solution:**
```bash
# Check log configuration
echo $RADAR_LOG_FILE
echo $RADAR_LOG_LEVEL

# Create logs directory
mkdir -p logs
chmod 755 logs

# Set log file
export RADAR_LOG_FILE=./logs/radar.log

# Check permissions
ls -la logs/
```

### Logs Too Large

**Problem:** Log files consuming too much disk space

**Solution:**
```bash
# Log rotation is automatic (10MB max, 5 backups)
# Check current size
ls -lh logs/

# Manually rotate
mv logs/radar.log logs/radar.log.old
# Server will create new log file

# Reduce log level
export RADAR_LOG_LEVEL=WARNING

# Use JSON format for better parsing
export RADAR_LOG_FORMAT=json
```

### Cannot Parse JSON Logs

**Problem:** JSON logs are malformed

**Solution:**
```bash
# Validate JSON logs
cat logs/radar.log | jq .

# If errors, check for mixed formats
# Ensure RADAR_LOG_FORMAT=json

# Parse specific fields
cat logs/radar.log | jq -r '.message'
cat logs/radar.log | jq 'select(.level=="ERROR")'
```

## Security Issues

### Using Default Secret Key

**Problem:** Warning about default secret key

**Solution:**
```bash
# Generate secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in .env
echo "RADAR_SECRET_KEY=<generated-key>" >> .env

# Or export
export RADAR_SECRET_KEY=<generated-key>

# Restart server
```

### CORS Errors

**Problem:** Browser shows CORS errors

**Solution:**
```bash
# Allow specific origins
export RADAR_ALLOWED_ORIGINS=https://yourdomain.com

# For development only (not production)
export RADAR_ALLOWED_ORIGINS=*

# Check current setting
curl http://localhost:8080/api/health -v | grep -i cors
```

### Unauthorized Access

**Problem:** Need to restrict access

**Solution:**
```bash
# Use reverse proxy with authentication (Nginx)
# See DEPLOYMENT.md for Nginx configuration

# Or implement custom middleware
# Add authentication to src/excel_radar/api.py

# Use firewall to restrict access
sudo ufw allow from 192.168.1.0/24 to any port 8080
```

## Common Error Messages

### "ENOENT: no such file or directory"

**Cause:** Missing file or directory

**Solution:**
```bash
# Create missing directories
mkdir -p data dist logs templates

# Check file paths
ls -la data/
```

### "Permission denied"

**Cause:** Insufficient permissions

**Solution:**
```bash
# Fix permissions
chmod 755 data dist logs
chmod 644 data/*.xlsx

# For Docker
sudo chown -R 1000:1000 data/ logs/
```

### "Connection refused"

**Cause:** Server not running or wrong port

**Solution:**
```bash
# Check if server is running
ps aux | grep gunicorn
docker-compose ps

# Check port
netstat -tuln | grep 8080

# Start server
docker-compose up -d
```

### "Module not found"

**Cause:** Dependencies not installed

**Solution:**
```bash
# Install dependencies
pip install -e .[prod]

# Verify installation
pip list | grep excel-radar
```

## Getting Help

If you're still experiencing issues:

1. **Check logs**: `tail -f logs/radar.log`
2. **Enable debug mode**: `RADAR_DEBUG=true RADAR_LOG_LEVEL=DEBUG`
3. **Check health**: `curl http://localhost:8080/api/health`
4. **Review documentation**: [README.md](./README.md), [DEPLOYMENT.md](./DEPLOYMENT.md), [API.md](./API.md)
5. **Search issues**: Check GitHub issues for similar problems
6. **Create issue**: Open a new GitHub issue with:
   - Error message
   - Log output
   - System information
   - Steps to reproduce

## Diagnostic Commands

Run these commands to gather diagnostic information:

```bash
#!/bin/bash
# diagnostic.sh - Gather system information

echo "=== System Information ==="
uname -a
python3 --version
docker --version
docker-compose --version

echo -e "\n=== Service Status ==="
docker-compose ps
curl -s http://localhost:8080/api/health | jq .

echo -e "\n=== Disk Usage ==="
df -h data/ logs/

echo -e "\n=== Recent Logs ==="
tail -20 logs/radar.log

echo -e "\n=== Configuration ==="
env | grep RADAR_

echo -e "\n=== Storage Stats ==="
curl -s http://localhost:8080/api/storage/stats | jq .

echo -e "\n=== Scheduler Status ==="
curl -s http://localhost:8080/api/scheduler/status | jq .
```

Save as `diagnostic.sh`, make executable (`chmod +x diagnostic.sh`), and run (`./diagnostic.sh`) to collect diagnostic information.