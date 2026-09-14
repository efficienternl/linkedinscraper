#!/bin/bash

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/linkedin-scraper"
SERVICE_NAME="linkedin-scraper"
REPO_URL="https://github.com/efficienternl/linkedinscraper.git"
BRANCH="main"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

log_info "LinkedIn Scraper Deployment Script"
log_info "=================================================="

# Step 1: Install Docker and Docker Compose if needed
log_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    log_info "Docker installed successfully"
else
    log_info "Docker is already installed"
fi

# Step 2: Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_info "Docker Compose installed successfully"
else
    log_info "Docker Compose is already installed"
fi

# Step 3: Create app directory
log_info "Setting up application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Step 4: Clone or pull repository
if [ -d ".git" ]; then
    log_info "Repository exists. Pulling latest changes..."
    git fetch origin
    git reset --hard "origin/$BRANCH"
else
    log_info "Cloning repository..."
    git clone -b "$BRANCH" "$REPO_URL" .
fi

# Step 5: Setup environment file
if [ ! -f ".env" ]; then
    log_warn "No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_info "Created .env file - PLEASE EDIT with your Apify token:"
        log_info "  vi $APP_DIR/.env"
    else
        log_error ".env.example not found"
        exit 1
    fi
else
    log_info ".env file exists"
fi

# Step 6: Generate SSL certificates if needed
log_info "Checking SSL certificates..."
mkdir -p certs
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    log_warn "SSL certificates not found. Generating self-signed certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem \
        -days 365 -nodes -subj "/CN=linkedin-scraper.local"
    log_info "Self-signed certificates generated"
    log_warn "NOTE: Use proper certificates in production!"
else
    log_info "SSL certificates found"
fi

# Step 7: Build Docker image
log_info "Building Docker image..."
docker-compose build --no-cache

# Step 8: Stop existing service if running
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_info "Stopping existing service..."
    systemctl stop "$SERVICE_NAME"
    sleep 2
fi

# Step 9: Install systemd service
log_info "Installing systemd service..."
cp linkedin-scraper.service /etc/systemd/system/
chmod 644 /etc/systemd/system/linkedin-scraper.service
systemctl daemon-reload

# Step 10: Start service
log_info "Starting LinkedIn Scraper service..."
systemctl start "$SERVICE_NAME"
systemctl enable "$SERVICE_NAME"

# Step 11: Verify deployment
log_info "Waiting for service to start (20 seconds)..."
sleep 20

if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_info "Service is running"
else
    log_error "Service failed to start"
    log_info "Checking logs:"
    systemctl status "$SERVICE_NAME" || true
    exit 1
fi

# Step 12: Check connectivity
log_info "Testing connectivity..."
if curl -f -k https://localhost/health 2>/dev/null || curl -f http://localhost/health 2>/dev/null; then
    log_info "Health check passed"
else
    log_warn "Health check failed - service may still be starting up"
fi

log_info "=================================================="
log_info "Deployment complete!"
log_info ""
log_info "Service Status:"
systemctl status "$SERVICE_NAME" --no-pager
log_info ""
log_info "Next steps:"
log_info "1. Check logs: journalctl -u $SERVICE_NAME -f"
log_info "2. Edit environment: vi $APP_DIR/.env (if needed)"
log_info "3. Access the app:"
log_info "   - Local: https://localhost"
log_info "   - Remote: https://187.7.17.231"
log_info ""
log_info "To redeploy: systemctl restart $SERVICE_NAME"
