#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Cleanup function
cleanup() {
    if [ -n "$CONTAINER_ID" ]; then
        log_info "Cleaning up container $CONTAINER_ID..."
        docker stop "$CONTAINER_ID" 2>/dev/null || true
        docker rm "$CONTAINER_ID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# ============================================================================
# SECTION 1: Docker Prerequisites
# ============================================================================
log_section "SECTION 1: Docker Prerequisites"

if ! command -v docker &> /dev/null; then
    log_fail "Docker not installed"
    exit 1
fi

log_pass "Docker is installed"
DOCKER_VERSION=$(docker --version)
log_info "Version: $DOCKER_VERSION"

# Check Docker daemon
if docker info > /dev/null 2>&1; then
    log_pass "Docker daemon is running"
else
    log_fail "Docker daemon is not running"
    exit 1
fi

# ============================================================================
# SECTION 2: Dockerfile Validation
# ============================================================================
log_section "SECTION 2: Dockerfile Validation"

if [ -f "Dockerfile" ]; then
    log_pass "Dockerfile exists"
else
    log_fail "Dockerfile not found"
    exit 1
fi

# Check for required Dockerfile elements
DOCKERFILE_CHECKS=(
    "FROM python:3.11-slim:Base image"
    "WORKDIR /app:Working directory"
    "COPY requirements.txt:Requirements copy"
    "pip install:Dependency installation"
    "EXPOSE 8501:Port exposure"
    "streamlit run:Streamlit launch"
)

for check in "${DOCKERFILE_CHECKS[@]}"; do
    pattern="${check%:*}"
    description="${check#*:}"
    if grep -q "$pattern" Dockerfile; then
        log_pass "Dockerfile contains: $description"
    else
        log_fail "Dockerfile missing: $description"
    fi
done

# ============================================================================
# SECTION 3: Docker Image Build
# ============================================================================
log_section "SECTION 3: Docker Image Build"

IMAGE_NAME="linkedin-scraper:test-$(date +%s)"
log_info "Building image: $IMAGE_NAME"
log_info "This may take 2-5 minutes..."

# Build image with timeout
BUILD_START=$(date +%s)
if timeout 600 docker build -t "$IMAGE_NAME" . > /tmp/docker_build.log 2>&1; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    log_pass "Docker image built successfully in ${BUILD_TIME}s"
else
    log_fail "Docker image build failed"
    log_info "Build log:"
    tail -30 /tmp/docker_build.log | sed 's/^/  /'
    exit 1
fi

# Check image exists
if docker images | grep -q "linkedin-scraper"; then
    log_pass "Image appears in docker images"
else
    log_fail "Image not found after build"
    exit 1
fi

# Get image details
IMAGE_SIZE=$(docker inspect "$IMAGE_NAME" --format='{{.Size}}')
IMAGE_SIZE_MB=$((IMAGE_SIZE / 1048576))
log_info "Image size: ${IMAGE_SIZE_MB}MB"

if [ "$IMAGE_SIZE_MB" -lt 2048 ]; then
    log_pass "Image size is reasonable (under 2GB)"
else
    log_warn "Image size is large (${IMAGE_SIZE_MB}MB)"
fi

# ============================================================================
# SECTION 4: Docker Container Runtime
# ============================================================================
log_section "SECTION 4: Docker Container Runtime"

log_info "Starting container from image..."
CONTAINER_ID=$(docker run -d -p 8501:8501 "$IMAGE_NAME")
log_pass "Container started with ID: $CONTAINER_ID"

# Wait for container to stabilize
log_info "Waiting for Streamlit to start (max 30 seconds)..."
STARTED=false
for i in {1..60}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        STARTED=true
        log_pass "Streamlit is accessible on http://localhost:8501"
        break
    fi
    echo -n "."
    sleep 0.5
done
echo ""

if [ "$STARTED" = false ]; then
    log_fail "Streamlit did not start within 30 seconds"
    log_info "Container logs:"
    docker logs "$CONTAINER_ID" | tail -20 | sed 's/^/  /'
    exit 1
fi

# ============================================================================
# SECTION 5: Container Verification
# ============================================================================
log_section "SECTION 5: Container Verification"

# Check container is running
CONTAINER_STATE=$(docker inspect "$CONTAINER_ID" --format='{{.State.Running}}')
if [ "$CONTAINER_STATE" = "true" ]; then
    log_pass "Container is running"
else
    log_fail "Container is not running"
    exit 1
fi

# Test HTTP endpoint
log_info "Testing HTTP endpoint..."
if curl -s http://localhost:8501 | grep -q "<!DOCTYPE" 2>/dev/null; then
    log_pass "HTTP endpoint returns valid HTML"
else
    log_warn "HTTP endpoint response looks unexpected"
fi

# Check for Streamlit app title
if curl -s http://localhost:8501 | grep -q "LinkedIn Scraper" 2>/dev/null; then
    log_pass "Page contains 'LinkedIn Scraper' title"
else
    log_warn "Could not verify page title (may be loaded dynamically)"
fi

# Check container logs for errors
log_info "Checking container logs for errors..."
CONTAINER_LOGS=$(docker logs "$CONTAINER_ID" 2>&1)
if echo "$CONTAINER_LOGS" | grep -qi "error\|failed\|exception" | head -5; then
    log_warn "Container logs contain error messages"
else
    log_pass "No obvious errors in container logs"
fi

# ============================================================================
# SECTION 6: Port & Network Validation
# ============================================================================
log_section "SECTION 6: Port & Network Validation"

# Check port mapping
if docker inspect "$CONTAINER_ID" --format='{{.NetworkSettings.Ports}}' | grep -q "8501"; then
    log_pass "Port 8501 is mapped"
else
    log_fail "Port 8501 not found in mappings"
fi

# Test port connectivity from host
if nc -z localhost 8501 2>/dev/null || curl -s http://localhost:8501 > /dev/null 2>&1; then
    log_pass "Port 8501 is accessible from host"
else
    log_fail "Port 8501 is not accessible"
fi

# ============================================================================
# SECTION 7: Container Stop & Cleanup
# ============================================================================
log_section "SECTION 7: Container Stop & Cleanup"

log_info "Stopping container..."
if docker stop "$CONTAINER_ID" > /dev/null 2>&1; then
    log_pass "Container stopped gracefully"
else
    log_fail "Failed to stop container"
fi

# Wait for port to be released
sleep 2

# Verify port is released
if ! curl -s http://localhost:8501 > /dev/null 2>&1; then
    log_pass "Port 8501 released after container stop"
else
    log_warn "Port 8501 still seems to be in use"
fi

# Remove container
if docker rm "$CONTAINER_ID" > /dev/null 2>&1; then
    log_pass "Container removed"
    CONTAINER_ID=""
else
    log_fail "Failed to remove container"
fi

# ============================================================================
# SECTION 8: Image Cleanup
# ============================================================================
log_section "SECTION 8: Image Cleanup"

log_info "Cleaning up test image..."
if docker rmi "$IMAGE_NAME" > /dev/null 2>&1; then
    log_pass "Test image removed"
else
    log_warn "Could not remove test image (may still be in use)"
fi

# ============================================================================
# SUMMARY
# ============================================================================
log_section "TEST EXECUTION SUMMARY"

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$((PASSED * 100 / TOTAL))
else
    PASS_RATE=0
fi

echo ""
echo "Tests Passed:  ${GREEN}$PASSED${NC}"
echo "Tests Failed:  ${RED}$FAILED${NC}"
echo "Warnings:      ${YELLOW}$WARNED${NC}"
echo "Total Tests:   $TOTAL"
echo "Pass Rate:     ${PASS_RATE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ ALL DOCKER TESTS PASSED${NC}"
    echo -e "${GREEN}Docker image and container are working correctly${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ SOME DOCKER TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
