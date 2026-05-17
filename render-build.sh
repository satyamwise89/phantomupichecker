#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python requirements standard modules
pip install -r requirements.txt

# Download and install required headless system dependencies for chromium engine inside Render linux container
playwright install chromium
playwright install-deps chromium