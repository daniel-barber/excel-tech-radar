# Excel Tech Radar - API Documentation

Complete REST API reference for Excel Tech Radar.

## Base URL

```
http://localhost:8080/api
```

## Table of Contents
- [Health & Status](#health--status)
- [Projects](#projects)
- [Excel Data](#excel-data)
- [Backups](#backups)
- [Maintenance](#maintenance)
- [Scheduler](#scheduler)
- [Storage](#storage)
- [Error Responses](#error-responses)

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing authentication via reverse proxy or custom middleware.

## Health & Status

### GET /api/health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-11T10:00:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "projects_count": 5,
  "disk": {
    "total_gb": 100.0,
    "used_gb": 25.5,
    "free_gb": 74.5,
    "percent_used": 25.5
  },
  "memory": {
    "total_gb": 16.0,
    "available_gb": 8.5,
    "percent_used": 46.9
  },
  "config": {
    "data_dir": "/app/data",
    "max_backups": 5,
    "debug": false
  }
}
```

## Projects

### GET /api/projects

List all radar projects.

**Response:**
```json
{
  "projects": [
    {
      "id": "my_project",
      "name": "My Project",
      "filename": "my_project.xlsx",
      "size": 45678,
      "modified": "2026-03-11T10:00:00"
    }
  ]
}
```

### GET /api/projects/{project_id}

Get project details and radar data.

**Parameters:**
- `project_id` (path): Project identifier

**Response:**
```json
{
  "title": "My Tech Radar",
  "date": "2026-03-11",
  "entries": [
    {
      "label": "React",
      "quadrant": "Languages & Frameworks",
      "ring": "Adopt",
      "moved": 0,
      "link": "https://react.dev",
      "dealSize": "Large",
      "propensityToWin": "High",
      "isStrategic": true
    }
  ]
}
```

### POST /api/projects

Create a new radar project.

**Request Body:**
```json
{
  "name": "New Radar",
  "template": "default"
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "new_radar",
    "name": "New Radar",
    "filename": "new_radar.xlsx"
  }
}
```

### POST /api/projects/{project_id}/rename

Rename a project.

**Request Body:**
```json
{
  "new_name": "Updated Name"
}
```

**Response:**
```json
{
  "success": true,
  "old_name": "old_project.xlsx",
  "new_name": "updated_name.xlsx"
}
```

### DELETE /api/projects/{project_id}

Delete a project (moves to .deleted).

**Response:**
```json
{
  "success": true,
  "message": "Project deleted"
}
```

### GET /api/projects/{project_id}/download

Download project Excel file.

**Response:** Excel file download

### POST /api/projects/{project_id}/build

Build radar JSON for a project.

**Response:**
```json
{
  "success": true,
  "message": "Radar built successfully",
  "radar": { /* radar data */ }
}
```

### POST /api/projects/upload

Upload an Excel file to create a new project.

**Request:** Multipart form data with `file` field

**Response:**
```json
{
  "success": true,
  "message": "Project uploaded successfully",
  "project_id": "uploaded_project"
}
```

## Excel Data

### GET /api/projects/{project_id}/excel

Get raw Excel data as JSON for editing.

**Response:**
```json
{
  "columns": ["name", "ring", "quadrant", "description"],
  "rows": [
    {
      "name": "React",
      "ring": "Adopt",
      "quadrant": "Languages & Frameworks",
      "description": "JavaScript library"
    }
  ],
  "rowCount": 1
}
```

### PUT /api/projects/{project_id}/excel

Update Excel data from JSON.

**Request Body:**
```json
{
  "rows": [
    {
      "name": "React",
      "ring": "Adopt",
      "quadrant": "Languages & Frameworks"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated 1 rows",
  "radar": { /* updated radar data */ }
}
```

### POST /api/projects/{project_id}/rows

Add a new row to Excel.

**Request Body:**
```json
{
  "name": "Vue.js",
  "ring": "Trial",
  "quadrant": "Languages & Frameworks",
  "description": "Progressive framework"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Row added",
  "radar": { /* updated radar data */ }
}
```

### PUT /api/projects/{project_id}/rows/{row_index}

Update a single row in Excel.

**Parameters:**
- `row_index` (path): Zero-based row index

**Request Body:**
```json
{
  "name": "Vue.js",
  "ring": "Adopt",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Row updated",
  "radar": { /* updated radar data */ }
}
```

### DELETE /api/projects/{project_id}/rows/{row_index}

Delete a row from Excel.

**Response:**
```json
{
  "success": true,
  "message": "Row deleted",
  "radar": { /* updated radar data */ }
}
```

## Backups

### GET /api/backups

List all backups across all projects.

**Query Parameters:**
- `project_id` (optional): Filter by project

**Response:**
```json
{
  "backups": [
    {
      "project_id": "my_project",
      "backup_path": "/app/data/my_project.xlsx.bak.20260311_100000",
      "timestamp": "2026-03-11T10:00:00",
      "size_bytes": 45678,
      "size_mb": 0.04,
      "backup_type": "manual",
      "age_hours": 2.5
    }
  ],
  "count": 1
}
```

### GET /api/projects/{project_id}/backups

List backups for a specific project.

**Response:**
```json
{
  "project_id": "my_project",
  "backups": [ /* array of backup objects */ ],
  "count": 3
}
```

### POST /api/projects/{project_id}/backups

Create a manual backup of a project.

**Response:**
```json
{
  "success": true,
  "message": "Backup created successfully",
  "backup_file": "my_project.xlsx.bak.20260311_100000",
  "size_mb": 0.04
}
```

### DELETE /api/projects/{project_id}/backups/{backup_timestamp}

Delete a specific backup.

**Parameters:**
- `backup_timestamp`: Timestamp in format YYYYMMDD_HHMMSS

**Response:**
```json
{
  "success": true,
  "message": "Backup deleted successfully"
}
```

### POST /api/projects/{project_id}/restore

Restore a project from a backup.

**Request Body:**
```json
{
  "backup_timestamp": "20260311_100000"
}
```

Leave empty to restore from latest backup.

**Response:**
```json
{
  "success": true,
  "message": "Project restored successfully",
  "radar": { /* restored radar data */ }
}
```

### POST /api/projects/{project_id}/export

Export a project with all backups as a ZIP file.

**Response:** ZIP file download containing:
- Project Excel file
- All backup files
- metadata.json with export information

### POST /api/projects/import

Import a project from a ZIP export file.

**Request:** Multipart form data
- `file`: ZIP file
- `overwrite` (optional): "true" or "false"

**Response:**
```json
{
  "success": true,
  "message": "Project imported successfully",
  "project_id": "imported_project"
}
```

## Maintenance

### POST /api/maintenance/cleanup

Manual cleanup of old backups and deleted files.

**Request Body (optional):**
```json
{
  "retention_days": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cleanup completed",
  "stats": {
    "projects_processed": 5,
    "backups_removed": 12,
    "deleted_files_removed": 3
  }
}
```

## Scheduler

### GET /api/scheduler/status

Get scheduler status and task information.

**Response:**
```json
{
  "running": true,
  "tasks": [
    {
      "name": "daily_cleanup",
      "enabled": true,
      "interval_seconds": 86400,
      "interval_hours": 24.0,
      "last_run": "2026-03-11T00:00:00",
      "next_run": "2026-03-12T00:00:00",
      "run_count": 5,
      "error_count": 0
    }
  ]
}
```

### POST /api/scheduler/start

Start the task scheduler.

**Response:**
```json
{
  "success": true,
  "message": "Scheduler started"
}
```

### POST /api/scheduler/stop

Stop the task scheduler.

**Response:**
```json
{
  "success": true,
  "message": "Scheduler stopped"
}
```

### POST /api/scheduler/tasks/{task_name}/enable

Enable a specific scheduled task.

**Parameters:**
- `task_name`: Task name (e.g., "daily_cleanup", "weekly_auto_backup")

**Response:**
```json
{
  "success": true,
  "message": "Task \"daily_cleanup\" enabled"
}
```

### POST /api/scheduler/tasks/{task_name}/disable

Disable a specific scheduled task.

**Response:**
```json
{
  "success": true,
  "message": "Task \"daily_cleanup\" disabled"
}
```

## Storage

### GET /api/storage/stats

Get storage statistics for the data directory.

**Response:**
```json
{
  "projects": {
    "count": 5,
    "size_bytes": 1234567,
    "size_mb": 1.18
  },
  "backups": {
    "count": 15,
    "size_bytes": 2345678,
    "size_mb": 2.24
  },
  "deleted": {
    "count": 2,
    "size_bytes": 345678,
    "size_mb": 0.33
  },
  "total": {
    "size_bytes": 3925923,
    "size_mb": 3.74,
    "size_gb": 0.00
  },
  "data_dir": "/app/data"
}
```

## Templates

### GET /api/template/download

Download Excel template for importing projects.

**Response:** Excel template file download

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "status": 400,
  "message": "Detailed error description"
}
```

### Common Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Server error

### Example Error Responses

**404 Not Found:**
```json
{
  "error": "Project not found",
  "status": 404
}
```

**400 Bad Request:**
```json
{
  "error": "Bad request",
  "status": 400,
  "message": "new_name is required"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "status": 500,
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, implement rate limiting via reverse proxy (e.g., Nginx).

## CORS

CORS is configured via the `RADAR_ALLOWED_ORIGINS` environment variable. Default is `*` (all origins).

For production:
```bash
RADAR_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Examples

### cURL Examples

```bash
# Health check
curl http://localhost:8080/api/health

# List projects
curl http://localhost:8080/api/projects

# Get project
curl http://localhost:8080/api/projects/my_project

# Create backup
curl -X POST http://localhost:8080/api/projects/my_project/backups

# List backups
curl http://localhost:8080/api/projects/my_project/backups

# Restore from backup
curl -X POST http://localhost:8080/api/projects/my_project/restore \
  -H "Content-Type: application/json" \
  -d '{"backup_timestamp": "20260311_100000"}'

# Upload project
curl -X POST http://localhost:8080/api/projects/upload \
  -F "file=@my_radar.xlsx"

# Get storage stats
curl http://localhost:8080/api/storage/stats

# Scheduler status
curl http://localhost:8080/api/scheduler/status
```

### Python Examples

```python
import requests

# Base URL
BASE_URL = "http://localhost:8080/api"

# List projects
response = requests.get(f"{BASE_URL}/projects")
projects = response.json()["projects"]

# Create backup
response = requests.post(f"{BASE_URL}/projects/my_project/backups")
backup = response.json()

# Upload project
with open("my_radar.xlsx", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/projects/upload", files=files)
    result = response.json()

# Get health
response = requests.get(f"{BASE_URL}/health")
health = response.json()
print(f"Status: {health['status']}")
```

### JavaScript Examples

```javascript
// Fetch projects
fetch('http://localhost:8080/api/projects')
  .then(response => response.json())
  .then(data => console.log(data.projects));

// Create backup
fetch('http://localhost:8080/api/projects/my_project/backups', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));

// Upload project
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8080/api/projects/upload', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Webhooks

Webhooks are not currently implemented. For event notifications, consider:
- Polling the `/api/scheduler/status` endpoint
- Monitoring log files
- Implementing custom webhook middleware

## Versioning

API versioning is not currently implemented. Breaking changes will be documented in release notes.

## Support

For API issues or questions:
- Check this documentation
- Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Open an issue on GitHub