"""Configuration and environment loading."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SESSION_FILE = os.getenv("SESSION_FILE", "session.json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
