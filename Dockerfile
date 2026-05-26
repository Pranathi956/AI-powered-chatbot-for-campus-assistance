FROM python:3.9-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Ports
EXPOSE 8080
EXPOSE 8000

# Final Command:
# 1. Action server (Backend folder nundi run chestunnam)
# 2. Rasa server (Port 8080)
# 3. Flask app (Port 8000)
CMD rasa run actions --actions Backend.actions --port 5055 & \
    rasa run --enable-api --cors "*" --port 8080 & \
    python3 frontend/app.py