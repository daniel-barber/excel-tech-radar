# Excel Tech Radar - Deployment Guide

This guide covers deploying Excel Tech Radar in production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 10GB+ for data and backups
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+) or macOS

### Software Requirements
- **Python**: 3.9 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 1.29+ (optional)

## Deployment Options

### 1. Docker Deployment (Recommended)

Docker provides the easiest and most consistent deployment experience.

#### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd excel-tech-radar

# 2. Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Create .env file
cp .env.example .env
# Edit .env and set RADAR_SECRET_KEY

# 4. Build and start
docker-compose up -d

# 5. Check status
docker-compose ps
docker-compose logs -f radar
```

#### Access the Application
- Web UI: http://localhost:8080
- API: http://localhost:8080/api
- Health Check: http://localhost:8080/api/health

#### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f radar

# Restart service
docker-compose restart radar

# Update to latest version
git pull
docker-compose build --no-cache
docker-compose up -d

# Access container shell
docker-compose exec radar bash
```

### 2. Manual Deployment

For environments without Docker or when you need more control.

#### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd excel-tech-radar

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .[prod]

# 4. Create directories
mkdir -p data dist logs

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings

# 6. Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Add to .env as RADAR_SECRET_KEY
```

#### Running with Gunicorn (Production)

```bash
# Start with gunicorn
gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  src.excel_radar.server:app
```

#### Running with Systemd

Create `/etc/systemd/system/excel-radar.service`:

```ini
[Unit]
Description=Excel Tech Radar
After=network.target

[Service]
Type=simple
User=radar
WorkingDirectory=/opt/excel-tech-radar
Environment="PATH=/opt/excel-tech-radar/venv/bin"
ExecStart=/opt/excel-tech-radar/venv/bin/gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --timeout 120 \
  src.excel_radar.server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable excel-radar
sudo systemctl start excel-radar
sudo systemctl status excel-radar
```

### 3. Cloud Deployment

#### AWS (EC2 + Docker)

```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Deploy application
git clone <repository-url>
cd excel-tech-radar
docker-compose up -d

# 5. Configure security group to allow port 8080
```

#### Azure (Container Instances)

```bash
# 1. Build and push image
docker build -t excel-radar:latest .
docker tag excel-radar:latest <registry>.azurecr.io/excel-radar:latest
docker push <registry>.azurecr.io/excel-radar:latest

# 2. Deploy container
az container create \
  --resource-group <resource-group> \
  --name excel-radar \
  --image <registry>.azurecr.io/excel-radar:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8080 \
  --environment-variables \
    RADAR_SECRET_KEY=<secret-key> \
    RADAR_LOG_FORMAT=json
```

#### Google Cloud (Cloud Run)

```bash
# 1. Build and push image
gcloud builds submit --tag gcr.io/<project-id>/excel-radar

# 2. Deploy to Cloud Run
gcloud run deploy excel-radar \
  --image gcr.io/<project-id>/excel-radar \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars RADAR_SECRET_KEY=<secret-key>
```

## Configuration

### Environment Variables

See `.env.example` for all available options. Key settings:

```bash
# Production essentials
RADAR_DEBUG=false
RADAR_SECRET_KEY=<generate-secure-key>
RADAR_LOG_FORMAT=json
RADAR_LOG_LEVEL=INFO

# Security
RADAR_ALLOWED_ORIGINS=https://yourdomain.com

# Performance
RADAR_MAX_BACKUPS=10
RADAR_RETENTION_DAYS=90

# Scheduler
RADAR_ENABLE_SCHEDULER=true
RADAR_ENABLE_AUTO_BACKUP=true
```

### Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name radar.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name radar.yourdomain.com;

    ssl_certificate /etc/ssl/certs/radar.crt;
    ssl_certificate_key /etc/ssl/private/radar.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Increase upload size
    client_max_body_size 50M;
}
```

## Security

### Security Checklist

- [ ] Generate and set unique `RADAR_SECRET_KEY`
- [ ] Set `RADAR_DEBUG=false` in production
- [ ] Configure `RADAR_ALLOWED_ORIGINS` (don't use `*`)
- [ ] Use HTTPS with valid SSL certificate
- [ ] Enable firewall and restrict ports
- [ ] Keep dependencies updated
- [ ] Regular security audits
- [ ] Implement rate limiting (via reverse proxy)
- [ ] Set up authentication (if needed)
- [ ] Regular backup verification

### SSL/TLS Setup

Using Let's Encrypt with Certbot:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d radar.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8080/api/health

# Detailed response includes:
# - Status (healthy/unhealthy)
# - Uptime
# - Project count
# - Disk usage
# - Memory usage
```

### Log Monitoring

```bash
# Docker logs
docker-compose logs -f radar

# File logs (if configured)
tail -f logs/radar.log

# JSON logs can be parsed with jq
tail -f logs/radar.log | jq .
```

### Metrics Collection

Integration with monitoring tools:

```bash
# Prometheus metrics endpoint (if implemented)
curl http://localhost:8080/metrics

# Custom monitoring script
#!/bin/bash
HEALTH=$(curl -s http://localhost:8080/api/health)
STATUS=$(echo $HEALTH | jq -r '.status')
if [ "$STATUS" != "healthy" ]; then
    # Send alert
    echo "Radar unhealthy: $HEALTH"
fi
```

## Backup and Recovery

### Automated Backups

The scheduler automatically creates backups:
- **Daily cleanup**: Removes old backups
- **Weekly auto-backup**: Backs up all projects
- **Storage monitoring**: Alerts on high usage

### Manual Backup

```bash
# Backup data directory
tar -czf radar-backup-$(date +%Y%m%d).tar.gz data/

# Backup with Docker
docker-compose exec radar tar -czf /tmp/backup.tar.gz /app/data
docker cp excel-tech-radar:/tmp/backup.tar.gz ./backup.tar.gz
```

### Restore from Backup

```bash
# Stop service
docker-compose down

# Restore data
tar -xzf radar-backup-20260311.tar.gz

# Start service
docker-compose up -d
```

### Disaster Recovery

1. **Regular backups**: Automated daily backups
2. **Off-site storage**: Copy backups to S3/Azure/GCS
3. **Test restores**: Verify backups monthly
4. **Documentation**: Keep deployment docs updated
5. **Monitoring**: Set up alerts for failures

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  radar:
    deploy:
      replicas: 3
    # Add load balancer
```

### Performance Tuning

```bash
# Increase Gunicorn workers
--workers $((2 * $(nproc) + 1))

# Adjust timeouts
--timeout 300

# Enable worker class
--worker-class gevent  # Requires gevent
```

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Review logs: `docker-compose logs -f`
- Check health: `curl http://localhost:8080/api/health`
- Open an issue on GitHub