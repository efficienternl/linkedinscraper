# LinkedIn Scraper - Test Execution Guide

**Status:** Ready for Testing  
**Date:** 2026-09-14  
**Scope:** Full end-to-end testing without live LinkedIn integration

---

## Quick Start

### Option 1: Run All Tests (Recommended)
```bash
cd /Users/rensklaucke/efficienter-hq/linkedin-scraper

# Make scripts executable
chmod +x verify_setup.sh verify_docker.sh

# Run setup verification (CLI, Python, Streamlit)
./verify_setup.sh

# Run Docker verification (Docker build, container runtime)
./verify_docker.sh

# Check results
echo "All tests completed. See TEST_CHECKLIST.md for manual validation."
```

### Option 2: Manual Testing
See **TEST_CHECKLIST.md** for detailed manual test procedures.

---

## What Gets Tested

### Automated Tests (via Scripts)

#### `verify_setup.sh` - Local Setup Verification
Tests performed (no Docker required):
1. Python version (3.9+)
2. Virtual environment setup
3. All dependencies (click, streamlit, linkedin_scraper, etc.)
4. CLI command availability (--help for all commands)
5. Project file structure
6. Configuration loading
7. Streamlit app startup (15 second runtime test)
8. Dockerfile structure

**Expected Duration:** 2-3 minutes  
**Requirements:** Python 3.9+, pip, bash

#### `verify_docker.sh` - Docker Build & Runtime Verification
Tests performed:
1. Docker installation and daemon status
2. Dockerfile structure and syntax
3. Docker image build process
4. Image size validation
5. Container startup
6. Streamlit accessibility (http://localhost:8501)
7. Port mapping validation
8. Container stop and cleanup
9. Image removal

**Expected Duration:** 5-10 minutes (depending on internet speed)  
**Requirements:** Docker, Docker daemon running, 2GB+ free disk space

---

## Detailed Test Coverage

### Section 1: CLI Commands (✓ Automated)
Tests that verify CLI works without requiring actual scraping:

```bash
python cli.py --help              # Main help
python cli.py login --help        # Login command
python cli.py person --help       # Single profile
python cli.py company --help      # Company page
python cli.py people --help       # Bulk profiles
python cli.py jobs --help         # Job search
python cli.py search --help       # Apify search
```

**What's Verified:**
- Command syntax
- Option descriptions
- Default values shown
- Help text completeness

**No Real Data Needed:** These commands only display help text, no actual LinkedIn access required.

---

### Section 2: Python Environment (✓ Automated)
**What's Verified:**
- Python 3.9+ available
- Virtual environment functional
- All required packages installed:
  - linkedin_scraper==3.1.2
  - click==8.1.8
  - streamlit==1.40.2
  - python-dotenv==1.2.1
  - requests==2.32.5

**No Real Data Needed:** Package import checks only, no actual functionality tested.

---

### Section 3: Streamlit Web Interface (✓ Automated + Manual)
**Automated Checks:**
- App.py Python syntax valid
- Streamlit imports work
- Page configuration found
- All 6 tabs present in code

**Manual Checks (See TEST_CHECKLIST.md):**
- UI loads on http://localhost:8501
- Sidebar settings visible
- Tab switching works
- Buttons are interactive
- Command generation works

**How to Test Manually:**
```bash
# Terminal 1: Start the app
python -m streamlit run app.py

# Terminal 2: In another terminal, or just check browser at http://localhost:8501
# Verify each tab loads without errors
# Verify buttons generate correct CLI commands
```

**No Real Data Needed:** App runs without session files or credentials.

---

### Section 4: Docker Build (✓ Automated)
**What's Verified:**
- Dockerfile syntax valid
- Multi-stage build structure correct
- Base image appropriate (python:3.11-slim)
- Dependencies installation layer correct
- Output directories created
- Port 8501 exposed
- Health check configured
- Streamlit launch command correct

**Build Process:**
- Pulls base image (~200MB)
- Installs Python dependencies (~500MB)
- Copies app code (~5MB)
- Creates final image (~700MB-1GB)

**Expected Duration:** 5-10 minutes first run, 2-3 minutes if cached

**No Real Data Needed:** Docker build is stateless and self-contained.

---

### Section 5: Docker Container Runtime (✓ Automated)
**What's Verified:**
- Container starts from built image
- Port 8501 exposed correctly
- Streamlit process runs inside container
- Health check passes
- HTTP endpoint responds
- Container stops cleanly
- Resources cleaned up

**Test Sequence:**
1. Build image → `linkedin-scraper:test-TIMESTAMP`
2. Run container → `-p 8501:8501`
3. Wait for Streamlit startup (max 30 seconds)
4. Verify http://localhost:8501 accessible
5. Stop container gracefully
6. Cleanup image and container

**No Real Data Needed:** Container runs test environment only.

---

## Test Results Interpretation

### Green Checkmarks (✓ PASS)
- Feature is working correctly
- No issues found
- Safe to proceed

### Red X Marks (✗ FAIL)
- Feature is broken
- Blocks deployment
- **Action Required:** Fix issue before proceeding

### Yellow Warnings (⚠)
- Minor issue or missing feature
- Non-blocking
- Recommended to review but not required

---

## Running Each Test Independently

### Test CLI Only
```bash
cd /Users/rensklaucke/efficienter-hq/linkedin-scraper
source .venv/bin/activate
python cli.py --help
python cli.py login --help
python cli.py person --help
python cli.py search --help
```

### Test Streamlit App Only
```bash
cd /Users/rensklaucke/efficienter-hq/linkedin-scraper
source .venv/bin/activate
python -m streamlit run app.py

# Then open: http://localhost:8501 in browser
# Press Ctrl+C to stop
```

### Test Docker Build Only
```bash
cd /Users/rensklaucke/efficienter-hq/linkedin-scraper
docker build -t linkedin-scraper:latest .

# Monitor build process
# Image should be ~700MB-1GB
docker images linkedin-scraper
```

### Test Docker Runtime Only
```bash
cd /Users/rensklaucke/efficienter-hq/linkedin-scraper

# Assuming image already built as linkedin-scraper:latest
docker run -d -p 8501:8501 linkedin-scraper:latest

# Verify it's running
docker ps

# Check logs
docker logs <container-id>

# Test endpoint
curl http://localhost:8501

# Stop container
docker stop <container-id>
docker rm <container-id>
```

---

## Troubleshooting Common Issues

### Issue: Python command not found
**Solution:**
```bash
# Use python3 instead of python
python3 --version
python3 cli.py --help
```

### Issue: Module not found (linkedin_scraper, streamlit, etc.)
**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Port 8501 already in use
**Solution:**
```bash
# Find process using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port=8502
```

### Issue: Docker build fails with "Permission denied"
**Solution:**
```bash
# Ensure Docker daemon is running
docker ps

# If error persists, try with sudo
sudo docker build -t linkedin-scraper:latest .

# Or add user to docker group (permanent fix)
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: Container exits immediately
**Solution:**
```bash
# Check container logs
docker logs <container-id>

# Rebuild image with verbose output
docker build -t linkedin-scraper:latest . 2>&1 | tail -50

# Run container in foreground to see errors
docker run -it -p 8501:8501 linkedin-scraper:latest
```

### Issue: Streamlit app shows blank page
**Solution:**
```bash
# Check browser console for errors (F12)
# Try clearing browser cache
# Try different browser
# Check Streamlit logs
python -m streamlit run app.py --logger.level=debug
```

---

## Pre-Deployment Checklist

Before deploying to production, verify:

- [ ] All automated tests pass (`verify_setup.sh` and `verify_docker.sh`)
- [ ] Manual tests from TEST_CHECKLIST.md completed
- [ ] CLI commands generate correct syntax
- [ ] Streamlit UI loads all 6 tabs
- [ ] Docker image builds without warnings
- [ ] Docker container starts and stays running
- [ ] No errors in Docker container logs
- [ ] Port 8501 accessible from container
- [ ] All dependencies listed in requirements.txt
- [ ] No hardcoded credentials or secrets in code
- [ ] Environment variables properly configured
- [ ] Output directories exist and are writable
- [ ] Documentation (README, .env.example) is complete

---

## Test Metrics

### Target Coverage
- CLI Commands: 100% (7 commands tested)
- Python Dependencies: 100% (5 packages verified)
- Streamlit Tabs: 100% (6 tabs verified)
- Docker Build: 100% (Dockerfile validated)
- Docker Runtime: 100% (Container lifecycle tested)

### Pass/Fail Criteria
- **PASS:** ≥95% of tests pass with no FAIL statuses
- **WARNING:** ≥90% of tests pass with ≤2 warnings
- **FAIL:** <90% pass rate or >2 critical failures
- **DEPLOYMENT READY:** All PASS, acceptable warnings noted

---

## Test Artifacts

Generated by test scripts:
- `/tmp/cli_help.txt` - CLI help output
- `/tmp/streamlit.log` - Streamlit startup log
- `/tmp/docker_build.log` - Docker build log

Review these if tests fail to identify root cause.

---

## After Testing

### If All Tests Pass
```bash
# You're ready for deployment!
echo "✓ All tests passed. Ready to deploy."

# Next steps:
# 1. Document any warnings
# 2. Tag Docker image with version: docker tag linkedin-scraper:latest linkedin-scraper:v1.0
# 3. Push to Docker registry if applicable
# 4. Deploy to production environment
```

### If Any Tests Fail
```bash
# Fix the issue(s)
# Re-run affected test(s)
# Update TEST_CHECKLIST.md with findings
# Document the issue and resolution
# Re-run full test suite when ready
```

---

## Test Timing

Typical test execution timeline:

| Test | Duration | Notes |
|------|----------|-------|
| Python/Environment Check | 10s | Quick checks |
| CLI Commands Test | 30s | Testing help output |
| Streamlit Startup | 15s | Brief runtime test |
| Dockerfile Validation | 5s | Syntax check |
| Docker Build | 5-10min | Depends on cache/network |
| Docker Runtime | 30s | Container start/stop |
| **Total** | **7-12 min** | Full suite |

---

## Support & Questions

### Where to Find Information
- **CLI Documentation:** `python cli.py <command> --help`
- **Streamlit Guide:** https://docs.streamlit.io
- **Docker Guide:** https://docs.docker.com
- **Project Structure:** Check directory listing
- **Configuration:** `.env` and `linkedin_cli/config.py`

### If Tests Are Unclear
1. Read the test output carefully
2. Check the specific test section in TEST_CHECKLIST.md
3. Review the troubleshooting section above
4. Check Docker logs: `docker logs <container-id>`
5. Check Streamlit logs: See terminal output

---

**Ready to test? Start with: `./verify_setup.sh`**
