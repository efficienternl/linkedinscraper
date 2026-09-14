# LinkedIn Scraper - End-to-End Testing Checklist

**Project:** LinkedIn Scraper  
**Test Date:** [TBD]  
**Tester:** [Name]  
**Status:** [DRAFT/IN PROGRESS/COMPLETE]

---

## Section 1: CLI Commands Testing

### 1.1 Help Command
- [ ] `python cli.py --help` displays main help
- [ ] Help text shows available commands (login, person, company, people, jobs, search)
- [ ] No errors in output

### 1.2 Command-Specific Help
- [ ] `python cli.py login --help` shows login options
- [ ] `python cli.py person --help` shows person command options
- [ ] `python cli.py company --help` shows company command options
- [ ] `python cli.py people --help` shows bulk people options
- [ ] `python cli.py jobs --help` shows job search options
- [ ] `python cli.py search --help` shows Apify search options with all flags

### 1.3 CLI Structure Validation
- [ ] All required options are documented
- [ ] All optional options have defaults shown
- [ ] Help text is in Dutch (expected language)

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 2: Python Dependencies & Environment

### 2.1 Virtual Environment
- [ ] `.venv` directory exists
- [ ] Virtual environment activates without errors: `source .venv/bin/activate`
- [ ] Python version is 3.9 or higher

### 2.2 Required Dependencies
- [ ] `pip list` shows: linkedin_scraper (3.1.2)
- [ ] `pip list` shows: click (8.1.8)
- [ ] `pip list` shows: streamlit (1.40.2)
- [ ] `pip list` shows: python-dotenv (1.2.1)
- [ ] `pip list` shows: requests (2.32.5)

### 2.3 Import Validation
- [ ] Can import `linkedin_scraper` without errors
- [ ] Can import `streamlit` without errors
- [ ] Can import `click` without errors
- [ ] Can import `requests` without errors

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 3: Streamlit Web Interface

### 3.1 Application Startup
- [ ] Streamlit app starts without errors
- [ ] App is accessible at http://localhost:8501
- [ ] No Python runtime errors on startup
- [ ] Streamlit logs show "ready to go"

### 3.2 Page Structure
- [ ] Page title is "LinkedIn Scraper"
- [ ] Subtitle appears: "Bulk-scrape LinkedIn profielen, bedrijven en vacatures"
- [ ] Sidebar loads with "Instellingen" (Settings)
- [ ] Sidebar settings are visible and interactive

### 3.3 Sidebar Settings
- [ ] Session file input field appears with default "session.json"
- [ ] "Headless modus" checkbox appears (checked by default)
- [ ] "Min. vertraging (s)" slider appears (range 1-30, default 5)
- [ ] "Max. vertraging (s)" slider appears (range 1-60, default 15)
- [ ] "Max. fouten op rij" slider appears (range 1-10, default 3)

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 4: UI Tabs Verification

### 4.1 Tab Presence
- [ ] Tab 1: "Login" appears
- [ ] Tab 2: "Profiel" appears
- [ ] Tab 3: "Bedrijf" appears
- [ ] Tab 4: "Bulk Profielen" appears
- [ ] Tab 5: "Vacatures" appears
- [ ] Tab 6: "Zoeken (Apify)" appears

### 4.2 Tab 1: Login
- [ ] Header "LinkedIn Inloggen" displays
- [ ] Info message displays: "Jij logt handmatig in bij LinkedIn..."
- [ ] Button "Start inloggen" is clickable
- [ ] Button shows instruction to run `python cli.py login`

### 4.3 Tab 2: Profiel
- [ ] Header "LinkedIn Profiel Scrapen" displays
- [ ] Text input for URL with placeholder shows
- [ ] "Scrape" button appears and is clickable
- [ ] Clicking with empty URL shows error message
- [ ] Clicking with URL shows command: `python cli.py person "URL"`

### 4.4 Tab 3: Bedrijf
- [ ] Header "LinkedIn Bedrijfspagina Scrapen" displays
- [ ] Text input for company URL with placeholder shows
- [ ] "Scrape" button appears and is clickable
- [ ] Clicking with empty URL shows error message
- [ ] Clicking with URL shows command: `python cli.py company "URL"`

### 4.5 Tab 4: Bulk Profielen
- [ ] Header "Bulk: Meerdere Profielen" displays
- [ ] File uploader for .txt files appears
- [ ] Output file input field appears with default path
- [ ] "Bulk Scrape" button appears
- [ ] File upload triggers command generation with correct format

### 4.6 Tab 5: Vacatures
- [ ] Header "Vacatures Zoeken & Scrapen" displays
- [ ] "Zoekterm" input field appears
- [ ] "Locatie" input field appears (optional)
- [ ] "Max. vacatures" number input appears (range 5-500, default 25)
- [ ] "Output bestand" input appears with default
- [ ] "Zoeken & Scrapen" button appears
- [ ] Clicking with no keywords shows error
- [ ] Clicking with keywords shows correct command

### 4.7 Tab 6: Zoeken (Apify)
- [ ] Header "Zoeken via Apify (meerdere keywords)" displays
- [ ] Info message about multiple keywords shows
- [ ] Multi-line text area for keywords appears
- [ ] "Seniority" dropdown appears with options: "", "manager", "director", "executive"
- [ ] "Manager type" text input appears
- [ ] "Locatie" input appears (optional)
- [ ] "Max. profielen per keyword" number input appears (range 10-500, default 100)
- [ ] "Output bestand" input appears
- [ ] "Zoeken & Scrapen" button appears
- [ ] Clicking with no keywords shows error

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 5: Command Generation & Display

### 5.1 Command Accuracy
- [ ] Single profile command format: `python cli.py person "URL"`
- [ ] Company command format: `python cli.py company "URL"`
- [ ] Bulk command includes all options: `--file`, `--out`, `--delay-min`, `--delay-max`
- [ ] Job search command includes: `--keywords`, `--limit`, `--out` (and optional `--location`)
- [ ] Apify search command builds multiple `--keywords` flags correctly
- [ ] Apify search adds `--seniority` when selected
- [ ] Apify search adds `--manager-type` when provided
- [ ] Apify search adds `--location` when provided

### 5.2 Command Display
- [ ] Commands appear in code blocks with syntax highlighting
- [ ] Commands are properly escaped for shell execution
- [ ] Long commands wrap appropriately without breaking

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 6: Docker Build & Deployment

### 6.1 Docker Image Build
- [ ] Dockerfile exists and is readable
- [ ] Multi-stage build syntax is valid
- [ ] `docker build -t linkedin-scraper:latest .` completes without errors
- [ ] Build takes less than 5 minutes
- [ ] Image size is reasonable (under 1GB)

### 6.2 Docker Image Validation
- [ ] Image appears in `docker images` output
- [ ] Image tag is `linkedin-scraper:latest`
- [ ] `docker inspect linkedin-scraper:latest` shows correct configuration

### 6.3 Dockerfile Contents
- [ ] Base image is `python:3.11-slim` (appropriate for size)
- [ ] Working directory is set to `/app`
- [ ] Requirements.txt is copied and dependencies installed
- [ ] Application code is copied
- [ ] Output/data directories are created
- [ ] Environment variables are set (PATH, PYTHONUNBUFFERED, PORT)
- [ ] EXPOSE 8501 is declared
- [ ] HEALTHCHECK is configured
- [ ] CMD runs streamlit correctly

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 7: Docker Container Runtime

### 7.1 Container Startup
- [ ] `docker run -d -p 8501:8501 linkedin-scraper:latest` starts successfully
- [ ] Container is running: `docker ps` shows the container
- [ ] No immediate errors in logs: `docker logs <container-id>`

### 7.2 Container Health
- [ ] Health check returns HEALTHY status after 40 seconds
- [ ] Container remains running (no auto-exit)
- [ ] `curl http://localhost:8501/health` returns 200 status (if endpoint exists)

### 7.3 Streamlit Accessibility via Container
- [ ] `curl http://localhost:8501` returns Streamlit HTML
- [ ] Port 8501 is responsive
- [ ] No permission errors in container logs

### 7.4 Container Cleanup
- [ ] `docker stop <container-id>` stops container gracefully
- [ ] `docker rm <container-id>` removes container without errors

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 8: File Structure & Configuration

### 8.1 Project Files
- [ ] `cli.py` exists and is executable
- [ ] `app.py` exists and contains Streamlit code
- [ ] `requirements.txt` exists with all dependencies
- [ ] `Dockerfile` exists and is valid
- [ ] `run.sh` exists and is executable
- [ ] `.env.example` exists
- [ ] `.env` exists (with test values, no real credentials)

### 8.2 Directory Structure
- [ ] `linkedin_cli/` directory exists with modules
- [ ] `linkedin_cli/__init__.py` exists
- [ ] `linkedin_cli/config.py` exists
- [ ] `linkedin_cli/jsonl_store.py` exists
- [ ] `linkedin_cli/csv_export.py` exists
- [ ] `linkedin_cli/apify.py` exists
- [ ] `linkedin_cli/bulk.py` exists
- [ ] `output/` directory can be created

### 8.3 Configuration Files
- [ ] Config loads from `.env` file
- [ ] Default values are provided for all config variables
- [ ] SESSION_FILE default is "session.json"
- [ ] OUTPUT_DIR default is "output"
- [ ] HEADLESS default is true

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 9: Error Handling & Edge Cases

### 9.1 CLI Error Handling
- [ ] Running without arguments shows help (doesn't crash)
- [ ] Invalid command shows error message
- [ ] Missing required arguments shows clear error
- [ ] Invalid URL format doesn't cause silent failures

### 9.2 Web UI Error Handling
- [ ] Closing Streamlit doesn't leave zombie processes
- [ ] Reloading page doesn't cause errors
- [ ] Rapid button clicks are handled gracefully

### 9.3 Docker Error Handling
- [ ] Container exits cleanly when stopped
- [ ] Container handles missing environment variables gracefully
- [ ] Port already in use shows meaningful error

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Section 10: Performance Baseline

### 10.1 CLI Performance
- [ ] CLI help displays in under 1 second
- [ ] App starts in under 30 seconds

### 10.2 Streamlit Performance
- [ ] Streamlit app loads initial page in under 15 seconds
- [ ] Tab switching is instant (no lag)
- [ ] Command generation is immediate (under 100ms)
- [ ] All buttons are responsive

### 10.3 Docker Performance
- [ ] Image build completes in under 5 minutes
- [ ] Container starts in under 60 seconds
- [ ] Health check passes within 45 seconds

**Result: [ ] PASS [ ] FAIL**  
**Notes:**

---

## Summary

### Overall Status
**Total Sections:** 10  
**Sections Passed:** ___  
**Sections Failed:** ___  

### Critical Issues Found
```
[List any blocking issues]
```

### Non-Critical Issues Found
```
[List any minor issues]
```

### Recommendations
```
[List improvements needed before production]
```

---

### Test Execution Log

**Test Start Time:** ___________  
**Test End Time:** ___________  
**Total Duration:** ___________  

**Approved for Deployment:** [ ] YES [ ] NO

**Sign-off:**
- Tester Name: _______________
- Date: _______________
- Comments: _______________
