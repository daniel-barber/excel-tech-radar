# Production Readiness Plan

This document outlines the steps to make the Excel Tech Radar project production-ready.

## Current Issues Identified

### 1. Data Directory Pollution
- **Problem**: `.deleted` and `.bak` files accumulate in the data directory
- **Impact**: Disk space waste, cluttered directory, potential confusion
- **Files affected**: 29+ backup/deleted files currently in data/

### 2. Development Files in Root
- **Problem**: Test scripts and development utilities in root directory
- **Files**: `create_test_data.py`, `test_strategic.py`, `update_*.py` scripts
- **Impact**: Unclear project structure, potential security risk

### 3. Missing Production Features
- No logging system
- No environment-based configuration
- Limited error handling
- No automated cleanup
- No backup/restore functionality

### 4. Documentation Gaps
- No deployment guide
- No production configuration examples
- No troubleshooting guide

---

## Phase 1: Data Directory Cleanup ✓

### 1.1 Update .gitignore
Add rules to ignore backup and deleted files:
```
# Backup and deleted files
*.bak
*.deleted
data/*.bak
data/*.deleted
```

### 1.2 Clean Existing Files
Remove all `.bak` and `.deleted` files from data directory:
- Keep only active `.xlsx` files
- Document cleanup in git commit

### 1.3 Implement Auto-Cleanup
Add cleanup functionality to API:
- Keep only last N backups per project (configurable)
- Auto-delete backups older than X days
- Add cleanup endpoint for manual triggering

---

## Phase 2: Project Structure Organization

### 2.1 Create Development Directory
Move development scripts to `dev/` or `scripts/`:
- `create_test_data.py` → `dev/create_test_data.py`
- `test_strategic.py` → `dev/test_strategic.py`
- `update_*.py` → `dev/update_*.py`
- `create_sample_data.py` → `dev/create_sample_data.py`
- `create_template.py` → Keep in root (user-facing)

### 2.2 Update .gitignore
Add development directory patterns:
```
# Development files
dev/
scripts/test_*
*.test.py
```

### 2.3 Create Proper Directory Structure
```
excel-tech-radar/
├── data/              # User data (gitignored except templates)
├── src/excel_radar/   # Core application
├── web/               # Frontend assets
├── templates/         # Excel templates
├── tests/             # Unit tests
├── dev/               # Development scripts
├── docs/              # Documentation
├── config/            # Configuration examples
└── .github/           # CI/CD workflows
```

---

## Phase 3: Production Configuration

### 3.1 Environment Variables
Create `.env.example`:
```env
# Server Configuration
RADAR_HOST=0.0.0.0
RADAR_PORT=8080
RADAR_DEBUG=false

# Data Configuration
RADAR_DATA_DIR=./data
RADAR_BACKUP_ENABLED=true
RADAR_BACKUP_RETENTION_DAYS=30
RADAR_MAX_BACKUPS_PER_PROJECT=5

# Logging
RADAR_LOG_LEVEL=INFO
RADAR_LOG_FILE=./logs/radar.log

# Security (for production)
RADAR_SECRET_KEY=change-me-in-production
RADAR_ALLOWED_ORIGINS=*
```

### 3.2 Configuration Loader
Update `loader.py` to support environment variables:
- Use `python-dotenv` for .env file support
- Fallback to config.yml for defaults
- Environment variables override config.yml

### 3.3 Production Config Example
Create `config/production.yml`:
```yaml
server:
  host: 0.0.0.0
  port: 8080
  debug: false

backup:
  enabled: true
  retention_days: 30
  max_per_project: 5
  auto_cleanup: true

logging:
  level: INFO
  file: /var/log/radar/app.log
  format: json
```

---

## Phase 4: Logging and Error Handling

### 4.1 Implement Logging System
Add structured logging to all modules:
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure in server.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/radar.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 4.2 Add Request Logging
Log all API requests:
- Request method, path, params
- Response status, time
- Errors with stack traces

### 4.3 Improve Error Handling
- Catch and log all exceptions
- Return user-friendly error messages
- Add error codes for debugging
- Implement retry logic for file operations

### 4.4 Add Health Check Endpoint
Create `/api/health` endpoint:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "projects_count": 5,
  "disk_space": "10GB free"
}
```

---

## Phase 5: Backup and Maintenance

### 5.1 Automated Backup Cleanup
Implement in `api.py`:
```python
def cleanup_old_backups(project_id: str, max_backups: int = 5):
    """Keep only the N most recent backups per project."""
    backup_files = sorted(
        data_dir.glob(f"{project_id}.xlsx.bak*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    for old_backup in backup_files[max_backups:]:
        old_backup.unlink()
```

### 5.2 Scheduled Cleanup Task
Add cleanup scheduler:
- Run daily cleanup of old backups
- Remove deleted files older than retention period
- Log cleanup actions

### 5.3 Backup/Restore API
Add endpoints:
- `POST /api/backup` - Create manual backup
- `GET /api/backups/{project_id}` - List backups
- `POST /api/restore/{project_id}/{backup_id}` - Restore from backup
- `DELETE /api/backups/{backup_id}` - Delete specific backup

### 5.4 Data Export/Import
Add bulk operations:
- Export all projects as ZIP
- Import projects from ZIP
- Validate before import

---

## Phase 6: Documentation and Deployment

### 6.1 Production Deployment Guide
Create `docs/DEPLOYMENT.md`:
- System requirements
- Installation steps
- Configuration guide
- Security best practices
- Monitoring setup
- Backup strategy

### 6.2 Docker Setup
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8080
CMD ["excel-radar", "serve"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  radar:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - RADAR_HOST=0.0.0.0
      - RADAR_PORT=8080
```

### 6.3 Troubleshooting Guide
Create `docs/TROUBLESHOOTING.md`:
- Common issues and solutions
- Log file locations
- Debug mode instructions
- Performance tuning

### 6.4 API Documentation
Create `docs/API.md`:
- All endpoints documented
- Request/response examples
- Error codes
- Rate limiting (if implemented)

### 6.5 Update README
Enhance README.md:
- Add production deployment section
- Link to detailed documentation
- Add troubleshooting quick links
- Include system requirements

---

## Implementation Priority

### High Priority (Do First)
1. ✅ Clean up data directory
2. ✅ Update .gitignore
3. ✅ Implement backup cleanup
4. ✅ Add basic logging

### Medium Priority (Do Next)
5. Reorganize project structure
6. Add environment configuration
7. Improve error handling
8. Create deployment documentation

### Low Priority (Nice to Have)
9. Docker setup
10. Advanced backup/restore
11. Health check endpoint
12. Monitoring integration

---

## Success Criteria

### Must Have
- [ ] No .bak or .deleted files in git
- [ ] Automatic cleanup of old backups
- [ ] Basic logging system
- [ ] Production deployment guide
- [ ] Environment-based configuration

### Should Have
- [ ] Organized project structure
- [ ] Comprehensive error handling
- [ ] Health check endpoint
- [ ] Docker support
- [ ] API documentation

### Nice to Have
- [ ] Monitoring integration
- [ ] Advanced backup/restore UI
- [ ] Performance metrics
- [ ] Rate limiting

---

## Timeline Estimate

- **Phase 1**: 2-3 hours
- **Phase 2**: 1-2 hours
- **Phase 3**: 2-3 hours
- **Phase 4**: 3-4 hours
- **Phase 5**: 2-3 hours
- **Phase 6**: 2-3 hours

**Total**: 12-18 hours for complete production readiness

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Data Directory Cleanup)
3. Proceed through phases sequentially
4. Test after each phase
5. Deploy to production environment
6. Monitor and iterate
