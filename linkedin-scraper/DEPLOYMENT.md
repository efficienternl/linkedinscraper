# LinkedIn Scraper - Production Deployment Guide

Complete guide to deploy the LinkedIn Scraper to a VPS using Docker, Gunicorn, Nginx, and systemd.

## Quick Start (TL;DR)

```bash
# 1. SSH into your VPS
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231

# 2. Run the deployment script
curl -fsSL https://raw.githubusercontent.com/efficienter-hq/linkedin-scraper/main/deploy.sh | bash

# 3. Edit environment variables
vi /opt/linkedin-scraper/.env

# 4. Restart service
systemctl restart linkedin-scraper

# 5. Access the app
# Navigate to: https://187.7.17.231
```

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│         Client Browser              │
└──────────────────┬──────────────────┘
                   │
                   ▼
     ┌─────────────────────────┐
     │   Nginx (Reverse Proxy) │
     │  Port 80/443 (HTTPS)    │
     └───────────┬─────────────┘
                 │
                 ▼
     ┌─────────────────────────┐
     │ Docker Container        │
     │ - Streamlit App         │
     │ - CLI Tool              │
     │ - Port 8501             │
     └───────────┬─────────────┘
                 │
                 ▼
     ┌─────────────────────────┐
     │  Persistent Volumes     │
     │ - /opt/linkedin-scraper │
     │   /output               │
     │   /data                 │
     └─────────────────────────┘

systemd (linkedin-scraper.service) manages Docker Compose
```

---

## Prerequisites

- VPS with Ubuntu/Debian
- SSH access with sudo/root
- SSH key at `~/.ssh/efficienter_vps`
- GitHub repo access (for git clone)
- Apify token (optional, for search feature)

---

## Full Deployment Steps

### Step 1: Connect to VPS

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231
```

### Step 2: Run Deploy Script

The deploy script handles everything automatically:

**Option A: Remote (recommended for production)**
```bash
curl -fsSL https://raw.githubusercontent.com/efficienter-hq/linkedin-scraper/main/deploy.sh | bash
```

**Option B: Local (if you have the script)**
```bash
scp -i ~/.ssh/efficienter_vps deploy.sh root@187.7.17.231:/tmp/
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 bash /tmp/deploy.sh
```

### Step 3: Configure Environment

The script will create `.env` from `.env.example`. Edit it to add your Apify token:

```bash
vi /opt/linkedin-scraper/.env
```

Example `.env`:
```env
# Optional settings
SESSION_FILE=session.json
OUTPUT_DIR=output
HEADLESS=true

# Apify API token (get from https://apify.com/account/integrations)
APIFY_TOKEN=your_actual_token_here
```

### Step 4: Configure SSL Certificates

Self-signed certificates are generated automatically. For production, replace them:

```bash
# Copy your certificates to the VPS
scp -i ~/.ssh/efficienter_vps /path/to/cert.pem root@187.7.17.231:/opt/linkedin-scraper/certs/
scp -i ~/.ssh/efficienter_vps /path/to/key.pem root@187.7.17.231:/opt/linkedin-scraper/certs/

# Verify permissions
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "ls -la /opt/linkedin-scraper/certs/"

# Reload Nginx
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker-compose -f /opt/linkedin-scraper/docker-compose.yml restart nginx"
```

### Step 5: Verify Deployment

```bash
# Check service status
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "systemctl status linkedin-scraper"

# View logs (last 50 lines)
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "journalctl -u linkedin-scraper -n 50 -f"

# Test health endpoint
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "curl -kI https://localhost/health"
```

---

## Access the Application

- **URL**: `https://187.7.17.231`
- **Port**: 443 (HTTPS) or 80 (HTTP, redirects to HTTPS)
- **Default health check**: `https://187.7.17.231/health`

### First-Time Access

1. Navigate to `https://187.7.17.231`
2. Browser will show SSL warning (if using self-signed cert) - click "Advanced" > "Proceed"
3. Web interface loads
4. Use CLI commands in the provided interface for actual scraping

---

## Common Operations

### Restart Service

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "systemctl restart linkedin-scraper"
```

### View Real-Time Logs

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "journalctl -u linkedin-scraper -f"
```

### Stop Service

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "systemctl stop linkedin-scraper"
```

### Start Service

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "systemctl start linkedin-scraper"
```

### Pull Latest Code

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "cd /opt/linkedin-scraper && git fetch origin && git reset --hard origin/main"
```

### Rebuild Docker Image

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "cd /opt/linkedin-scraper && docker-compose build --no-cache"
```

### Rebuild and Restart

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "cd /opt/linkedin-scraper && \
    docker-compose build --no-cache && \
    docker-compose restart"
```

---

## Troubleshooting

### Service Won't Start

Check logs for errors:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "journalctl -u linkedin-scraper -n 100"
```

### Container Exits Immediately

Check Docker logs:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker-compose -f /opt/linkedin-scraper/docker-compose.yml logs -f"
```

### Health Check Failing

Ensure containers are running:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker ps"
```

### Nginx Configuration Error

Validate config:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker-compose -f /opt/linkedin-scraper/docker-compose.yml exec nginx nginx -t"
```

### Port Already in Use

Check what's using port 80/443:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "lsof -i :80 && lsof -i :443"
```

---

## File Structure on VPS

```
/opt/linkedin-scraper/
├── .git/                    # Git repository
├── .env                     # Environment variables (EDITED AFTER DEPLOY)
├── .env.example             # Template
├── Dockerfile               # Container definition
├── docker-compose.yml       # Service orchestration
├── nginx.conf              # Reverse proxy config
├── linkedin-scraper.service # Systemd service file
├── deploy.sh               # Deployment script
├── app.py                  # Streamlit web interface
├── cli.py                  # CLI entrypoint
├── requirements.txt        # Python dependencies
├── certs/
│   ├── cert.pem           # SSL certificate
│   └── key.pem            # SSL private key
├── output/                # Scraping results (persistent volume)
├── data/                  # Session files & cache (persistent volume)
└── linkedin_cli/          # Python package
    ├── config.py
    ├── apify.py
    ├── bulk.py
    ├── csv_export.py
    └── jsonl_store.py
```

---

## Updating to Latest Version

Pull updates and redeploy:

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "cd /opt/linkedin-scraper && \
    git fetch origin && \
    git reset --hard origin/main && \
    docker-compose build --no-cache && \
    docker-compose restart"
```

---

## Security Considerations

1. **SSL/TLS**: Self-signed certs are auto-generated. Replace with proper certs for production.
2. **Rate Limiting**: Nginx limits to 10 req/s per IP (configurable in `nginx.conf`)
3. **Security Headers**: HSTS, CSP, X-Frame-Options enabled in Nginx
4. **Environment Variables**: Keep `.env` out of version control (it's in `.gitignore`)
5. **Restart Policy**: Service auto-restarts on failure (up to 3 times in 60s)

---

## Performance Tuning

### Increase Rate Limit

Edit `/opt/linkedin-scraper/nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=50r/s;  # Change 10r/s to 50r/s
```

Then restart:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker-compose -f /opt/linkedin-scraper/docker-compose.yml restart nginx"
```

### Increase Docker Memory

Edit `/opt/linkedin-scraper/docker-compose.yml`:
```yaml
services:
  linkedin-scraper:
    deploy:
      resources:
        limits:
          memory: 2G  # Default is 1G
```

---

## Monitoring & Alerts

### Check Service Status

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "systemctl status linkedin-scraper && \
    docker ps && \
    curl -k https://localhost/health"
```

### Monitor Memory Usage

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker stats"
```

### Check Disk Usage

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "df -h && du -sh /opt/linkedin-scraper/*"
```

---

## Rollback to Previous Version

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "cd /opt/linkedin-scraper && \
    git reset --hard HEAD~1 && \
    docker-compose build --no-cache && \
    docker-compose restart"
```

---

## Uninstall / Clean Up

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 << 'EOF'
# Stop service
systemctl stop linkedin-scraper

# Remove systemd service
rm /etc/systemd/system/linkedin-scraper.service
systemctl daemon-reload

# Remove app directory (optional)
rm -rf /opt/linkedin-scraper

# Clean up Docker
docker system prune -f
EOF
```

---

## Support & Debugging

For detailed debugging:

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "journalctl -u linkedin-scraper --no-pager -p err -n 100"
```

Check Docker logs:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
    "docker-compose -f /opt/linkedin-scraper/docker-compose.yml logs linkedin-scraper nginx"
```

---

## Summary

Your LinkedIn Scraper is now deployed as a production-grade service with:
- Auto-scaling Docker containers
- Automatic restarts on failure
- HTTPS reverse proxy with Nginx
- Persistent volumes for data
- Health checks and monitoring
- One-command deployment updates

Access it at `https://187.7.17.231` and manage via:
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231
systemctl status linkedin-scraper
journalctl -u linkedin-scraper -f
```

Done!
