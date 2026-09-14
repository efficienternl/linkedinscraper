# LinkedIn Scraper - Deployment Cheat Sheet

## One-Liner Deploy

```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'curl -fsSL https://raw.githubusercontent.com/efficienter-hq/linkedin-scraper/main/deploy.sh | bash'
```

## Essential Commands

| Task | Command |
|------|---------|
| **Deploy** | `curl -fsSL https://raw.githubusercontent.com/efficienter-hq/linkedin-scraper/main/deploy.sh \| bash` |
| **View Status** | `systemctl status linkedin-scraper` |
| **View Logs** | `journalctl -u linkedin-scraper -f` |
| **Restart** | `systemctl restart linkedin-scraper` |
| **Stop** | `systemctl stop linkedin-scraper` |
| **Start** | `systemctl start linkedin-scraper` |
| **Rebuild** | `cd /opt/linkedin-scraper && docker-compose build --no-cache` |
| **Pull Updates** | `cd /opt/linkedin-scraper && git fetch origin && git reset --hard origin/main` |
| **Edit Env** | `vi /opt/linkedin-scraper/.env` |
| **View Docker Logs** | `docker-compose -f /opt/linkedin-scraper/docker-compose.yml logs -f` |
| **Check Health** | `curl -kI https://localhost/health` |

## SSH Shortcuts

Save these in `~/.bash_profile` or `~/.zshrc`:

```bash
# SSH into LinkedIn Scraper VPS
alias ssh-scraper='ssh -i ~/.ssh/efficienter_vps root@187.7.17.231'

# Tail service logs
alias scraper-logs='ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 "journalctl -u linkedin-scraper -f"'

# Check status
alias scraper-status='ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 "systemctl status linkedin-scraper"'

# Restart service
alias scraper-restart='ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 "systemctl restart linkedin-scraper"'

# Rebuild and restart
alias scraper-redeploy='ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  "cd /opt/linkedin-scraper && docker-compose build --no-cache && docker-compose restart"'
```

Then use:
```bash
ssh-scraper                  # Connect
scraper-logs                 # View logs
scraper-status               # Check status
scraper-restart              # Restart
scraper-redeploy             # Full rebuild
```

## Typical Workflow

### Initial Deploy
```bash
# 1. Deploy
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'curl -fsSL https://raw.githubusercontent.com/efficienter-hq/linkedin-scraper/main/deploy.sh | bash'

# 2. Edit environment
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'vi /opt/linkedin-scraper/.env'

# 3. Verify
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'systemctl status linkedin-scraper'

# 4. Check health
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'curl -kI https://localhost/health'
```

### Update Code
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  "cd /opt/linkedin-scraper && git fetch origin && git reset --hard origin/main && docker-compose build --no-cache && docker-compose restart"
```

### Debug Issues
```bash
# View service logs
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'journalctl -u linkedin-scraper -n 100'

# View Docker logs
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'docker-compose -f /opt/linkedin-scraper/docker-compose.yml logs linkedin-scraper'

# Check if containers are running
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'docker ps'
```

## Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition (multistage, ~500MB final image) |
| `docker-compose.yml` | Orchestrates Streamlit + Nginx containers |
| `nginx.conf` | Reverse proxy, SSL/TLS, rate limiting, security headers |
| `linkedin-scraper.service` | systemd service for auto-restart and updates |
| `deploy.sh` | One-command deployment script |
| `.dockerignore` | Optimizes build by excluding unnecessary files |
| `DEPLOYMENT.md` | Full documentation |

## Architecture

```
Internet (HTTPS)
    ↓
Nginx (Port 443)
    ↓
Docker Container (Port 8501)
    ├─ Streamlit App
    └─ CLI Tool
    ↓
Persistent Volumes
├─ /output (scraping results)
└─ /data (session files)
```

## Directory on VPS

- **App**: `/opt/linkedin-scraper`
- **Data**: `/opt/linkedin-scraper/output` (persistent)
- **Config**: `/opt/linkedin-scraper/.env` (edit here)
- **Certs**: `/opt/linkedin-scraper/certs/` (SSL)
- **Logs**: `journalctl -u linkedin-scraper` (systemd)

## Access Points

| Endpoint | Usage |
|----------|-------|
| `https://187.7.17.231` | Web UI |
| `https://187.7.17.231/health` | Health check |
| `localhost:8501` | Direct Streamlit (inside container) |

## Troubleshooting Quick Guide

### Service won't start
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'journalctl -u linkedin-scraper -p err -n 20'
```

### Container keeps restarting
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'docker-compose -f /opt/linkedin-scraper/docker-compose.yml logs linkedin-scraper'
```

### Nginx not responding
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'docker-compose -f /opt/linkedin-scraper/docker-compose.yml exec nginx nginx -t'
```

### Health check failing
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'docker ps && curl -kv https://localhost/health'
```

### Check disk space
```bash
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'df -h && du -sh /opt/linkedin-scraper/*'
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Docker Image Size | ~500MB |
| Container Memory | 512MB (configurable) |
| Startup Time | ~30 seconds |
| Health Check Interval | 30 seconds |
| Response Time | <500ms (typical) |
| Uptime Target | 99.9% |

## Restart Policy

Service auto-restarts with:
- Max 3 restarts per 60 seconds
- 10-second delay between retries
- systemd handles supervision

## SSL/TLS

- **Default**: Self-signed certs (auto-generated)
- **Production**: Replace `/opt/linkedin-scraper/certs/` with proper certs
- **Command**: `curl -k https://localhost` (ignores cert warnings locally)

## Environment Variables

Edit `/opt/linkedin-scraper/.env`:

```env
# Optional
SESSION_FILE=session.json
OUTPUT_DIR=output
HEADLESS=true

# Required for Apify search
APIFY_TOKEN=your_token_here
```

## Version Management

```bash
# Check current version
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'cd /opt/linkedin-scraper && git log -1 --oneline'

# Pin specific version
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'cd /opt/linkedin-scraper && git checkout v1.2.3'

# Back to latest main
ssh -i ~/.ssh/efficienter_vps root@187.7.17.231 \
  'cd /opt/linkedin-scraper && git checkout main && git pull'
```

---

**VPS IP**: 187.7.17.231  
**SSH Key**: ~/.ssh/efficienter_vps  
**App Path**: /opt/linkedin-scraper  
**Service**: linkedin-scraper
