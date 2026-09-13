#!/bin/bash
set -e

echo "🚀 LinkedIn Scraper Setup & Launch"
echo "===================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 niet gevonden. Installeer Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION"

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Install Playwright browser
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "🌐 Installing Playwright Chromium..."
    playwright install chromium
fi

# Create output dir
mkdir -p output

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting web interface on http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Launch Streamlit
streamlit run app.py --logger.level=warning
