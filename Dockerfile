# 🟢 Python standard slim image build context uthana
FROM python:3.11-slim

# Set environment system variables to optimize logs
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright

# Build space context define karna
WORKDIR /app

# System dependencies install karna jo chromium headless bypass pipelines ke liye zaroori hain
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    && rm -rf /lib/apt/lists/*

# Copy python deployment files
COPY requirements.txt .

# Install target requirements packages mapping python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 CRITICAL STEP FOR DOCKER: Install Playwright system core and download isolated Chromium binaries
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy full application tree back to virtual disk node space
COPY . .

# Expose backend port mapping context matching Render default binding setup
EXPOSE 10000

# Fire production uvicorn binary framework server mapping FastAPI application instance 
CMD ["uvicorn", "app.py:app", "--host", "0.0.0.0", "--port", "10000"]
