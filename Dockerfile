# Playwright ka official image jisme pehle se Chromium aur saari dependencies loaded hain
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Work directory set karein
WORKDIR /app

# Requirements file copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki ka poora code copy karein
COPY . .

# Render ke port par app ko run karne ke liye environment handle karein
EXPOSE 10000

# App ko start karne ka master command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
