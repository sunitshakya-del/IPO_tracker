#!/usr/bin/env python3
"""
Standalone test script for the SQLite backend.
This simulates what will happen when Electron starts the backend.
"""

import sys
import os
from pathlib import Path

# Set environment for desktop mode
os.environ['ELECTRON_MODE'] = 'true'
os.environ['DB_PATH'] = str(Path(__file__).parent / 'test_ipo_tracker.db')

print("=" * 60)
print("IPO Tracker Desktop - Backend Test")
print("=" * 60)
print(f"Database path: {os.environ['DB_PATH']}")
print(f"Starting FastAPI server on http://127.0.0.1:8001")
print("=" * 60)

# Change to backend directory and run
os.chdir(Path(__file__).parent / 'backend')

# Import and run the SQLite server
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server_sqlite:app",
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
