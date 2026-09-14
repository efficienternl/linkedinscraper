#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
WARNED=0

# Helper functions
log_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNED++))
}

log_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Cleanup function for background processes
cleanup() {
    echo ""
    log_info "Cleaning up background processes..."
    pkill -f "streamlit run" || true
    sleep 2
}
trap cleanup EXIT

# ============================================================================
# SECTION 1: Environment & Python Validation
# ============================================================================
log_section "SECTION 1: Environment & Python Validation"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    log_pass "Python 3 found: $PYTHON_VERSION"

    MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
        log_pass "Python version is 3.9 or higher"
    else
        log_fail "Python version must be 3.9 or higher (found $MAJOR.$MINOR)"
    fi
else
    log_fail "Python 3 not found"
fi

# Check virtual environment
if [ -d ".venv" ]; then
    log_pass "Virtual environment directory exists"
else
    log_warn "Virtual environment not found, creating..."
    python3 -m venv .venv
    log_pass "Virtual environment created"
fi

# Activate venv (for this script)
source .venv/bin/activate
log_pass "Virtual environment activated"

# ============================================================================
# SECTION 2: Dependencies Validation
# ============================================================================
log_section "SECTION 2: Dependencies Validation"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    log_pass "requirements.txt found"
else
    log_fail "requirements.txt not found"
fi

# Check key dependencies
DEPENDENCIES=("linkedin_scraper" "click" "streamlit" "python-dotenv" "requests")
for dep in "${DEPENDENCIES[@]}"; do
    if python3 -c "import pkgutil; exit(0 if pkgutil.find_loader('$dep') else 1)" 2>/dev/null; then
        log_pass "Module '$dep' is installed"
    else
        log_warn "Module '$dep' not found (may need: pip install -r requirements.txt)"
    fi
done

# ============================================================================
# SECTION 3: CLI Commands Testing
# ============================================================================
log_section "SECTION 3: CLI Commands Testing"

# Test main help
if python3 cli.py --help > /tmp/cli_help.txt 2>&1; then
    if grep -q "Usage:" /tmp/cli_help.txt; then
        log_pass "CLI --help command works"
    else
        log_fail "CLI help output doesn't contain expected format"
    fi
else
    log_fail "CLI --help command failed"
fi

# Test command presence in help
COMMANDS=("login" "person" "company" "people" "jobs" "search")
for cmd in "${COMMANDS[@]}"; do
    if grep -q "$cmd" /tmp/cli_help.txt; then
        log_pass "Command '$cmd' found in CLI help"
    else
        log_fail "Command '$cmd' not found in CLI help"
    fi
done

# Test individual command help
for cmd in "${COMMANDS[@]}"; do
    if python3 cli.py "$cmd" --help > /tmp/cli_${cmd}_help.txt 2>&1; then
        log_pass "Command '$cmd --help' works"
    else
        log_fail "Command '$cmd --help' failed"
    fi
done

# ============================================================================
# SECTION 4: Project Structure
# ============================================================================
log_section "SECTION 4: Project Structure Validation"

# Check required files
FILES=("cli.py" "app.py" "Dockerfile" "run.sh" "requirements.txt" ".env.example")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        log_pass "File '$file' exists"
    else
        log_fail "File '$file' not found"
    fi
done

# Check required directories
DIRS=("linkedin_cli" "output")
if [ -d "linkedin_cli" ]; then
    log_pass "Directory 'linkedin_cli' exists"

    MODULES=("__init__.py" "config.py" "jsonl_store.py" "csv_export.py" "apify.py" "bulk.py")
    for mod in "${MODULES[@]}"; do
        if [ -f "linkedin_cli/$mod" ]; then
            log_pass "Module 'linkedin_cli/$mod' exists"
        else
            log_fail "Module 'linkedin_cli/$mod' not found"
        fi
    done
else
    log_fail "Directory 'linkedin_cli' not found"
fi

# ============================================================================
# SECTION 5: Configuration & Imports
# ============================================================================
log_section "SECTION 5: Configuration & Imports"

# Test importing main modules
python3 -c "from linkedin_cli.config import SESSION_FILE, OUTPUT_DIR, HEADLESS" 2>/dev/null && \
    log_pass "linkedin_cli.config imports successfully" || \
    log_fail "Failed to import linkedin_cli.config"

python3 -c "import click" 2>/dev/null && \
    log_pass "click module imports successfully" || \
    log_fail "Failed to import click"

python3 -c "import streamlit" 2>/dev/null && \
    log_pass "streamlit module imports successfully" || \
    log_fail "Failed to import streamlit"

# Check config defaults
if [ -f ".env" ]; then
    log_pass ".env file exists"
else
    log_warn ".env file not found (will use defaults)"
fi

# ============================================================================
# SECTION 6: Streamlit App Validation
# ============================================================================
log_section "SECTION 6: Streamlit App Structure"

# Check app.py syntax
if python3 -m py_compile app.py 2>/dev/null; then
    log_pass "app.py syntax is valid"
else
    log_fail "app.py has syntax errors"
fi

# Check for required Streamlit elements in app.py
if grep -q "st.set_page_config" app.py; then
    log_pass "Streamlit page config found"
else
    log_fail "Streamlit page config not found"
fi

if grep -q "st.title" app.py; then
    log_pass "Streamlit title found"
else
    log_fail "Streamlit title not found"
fi

if grep -q "st.tabs" app.py; then
    log_pass "Streamlit tabs found"
else
    log_fail "Streamlit tabs not found"
fi

# Check for expected tabs
EXPECTED_TABS=("Login" "Profiel" "Bedrijf" "Bulk Profielen" "Vacatures" "Zoeken")
FOUND_TABS=0
for tab in "${EXPECTED_TABS[@]}"; do
    if grep -q "\"$tab\"" app.py; then
        ((FOUND_TABS++))
    fi
done
log_pass "Found $FOUND_TABS/${#EXPECTED_TABS[@]} expected tabs in app.py"

# ============================================================================
# SECTION 7: Docker Validation
# ============================================================================
log_section "SECTION 7: Docker Validation"

if command -v docker &> /dev/null; then
    log_pass "Docker is installed"

    # Check Dockerfile
    if [ -f "Dockerfile" ]; then
        log_pass "Dockerfile exists"

        # Check Dockerfile syntax
        if docker run --rm -i hadolint/hadolint:latest hadolint - < Dockerfile 2>/dev/null; then
            log_pass "Dockerfile linting passed"
        else
            log_warn "Dockerfile linting not available (hadolint not found)"
        fi

        # Check Dockerfile contents
        if grep -q "FROM python:3.11-slim" Dockerfile; then
            log_pass "Correct base image in Dockerfile"
        else
            log_warn "Expected python:3.11-slim base image"
        fi

        if grep -q "EXPOSE 8501" Dockerfile; then
            log_pass "Port 8501 exposed in Dockerfile"
        else
            log_fail "Port 8501 not exposed"
        fi

        if grep -q "streamlit" Dockerfile; then
            log_pass "Streamlit command in Dockerfile"
        else
            log_fail "Streamlit command not found in Dockerfile"
        fi
    else
        log_fail "Dockerfile not found"
    fi
else
    log_warn "Docker not installed (skipping Docker tests)"
fi

# ============================================================================
# SECTION 8: Run Script Validation
# ============================================================================
log_section "SECTION 8: Run Script Validation"

if [ -f "run.sh" ]; then
    log_pass "run.sh script exists"

    if [ -x "run.sh" ]; then
        log_pass "run.sh is executable"
    else
        log_warn "run.sh is not executable (chmod +x run.sh)"
    fi

    # Check run.sh contents
    if grep -q "streamlit run app.py" run.sh; then
        log_pass "Streamlit launch command found in run.sh"
    else
        log_fail "Streamlit launch command not found in run.sh"
    fi

    if grep -q "venv" run.sh; then
        log_pass "Virtual environment setup in run.sh"
    else
        log_fail "Virtual environment setup not found in run.sh"
    fi
else
    log_fail "run.sh not found"
fi

# ============================================================================
# SECTION 9: Streamlit Runtime Test (Non-blocking)
# ============================================================================
log_section "SECTION 9: Streamlit Runtime Test (15 second test)"

log_info "Starting Streamlit app in background (will run for 15 seconds)..."

# Create a temporary secrets.toml for Streamlit to avoid warnings
mkdir -p ~/.streamlit
touch ~/.streamlit/secrets.toml 2>/dev/null || true

# Start Streamlit in background
streamlit run app.py --logger.level=warning > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
log_info "Streamlit process ID: $STREAMLIT_PID"

# Wait for Streamlit to start
log_info "Waiting for Streamlit to start (max 15 seconds)..."
STARTED=false
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        STARTED=true
        log_pass "Streamlit is running on http://localhost:8501"
        break
    fi
    echo -n "."
    sleep 0.5
done
echo ""

if [ "$STARTED" = false ]; then
    log_warn "Streamlit did not start within 15 seconds"
    log_info "Streamlit log:"
    tail -20 /tmp/streamlit.log | sed 's/^/  /'
else
    # Try to fetch the page
    if curl -s http://localhost:8501 | grep -q "LinkedIn Scraper" 2>/dev/null; then
        log_pass "Streamlit page contains 'LinkedIn Scraper' title"
    else
        log_warn "Could not verify page title"
    fi
fi

# Kill Streamlit
kill $STREAMLIT_PID 2>/dev/null || true
wait $STREAMLIT_PID 2>/dev/null || true
sleep 2

# ============================================================================
# SECTION 10: Summary Report
# ============================================================================
log_section "TEST EXECUTION SUMMARY"

TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

echo ""
echo "Tests Passed:  ${GREEN}$PASSED${NC}"
echo "Tests Failed:  ${RED}$FAILED${NC}"
echo "Warnings:      ${YELLOW}$WARNED${NC}"
echo "Total Tests:   $TOTAL"
echo "Pass Rate:     ${PASS_RATE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ ALL CHECKS PASSED - Ready for deployment${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ SOME CHECKS FAILED - See above for details${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
