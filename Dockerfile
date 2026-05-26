FROM python:3.9-slim

WORKDIR /app

# System requirements
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Expose ports for Rasa and Frontend
EXPOSE 8080
EXPOSE 8000

# Start Action Server, Rasa Server, and Frontend
CMD rasa run actions --port 5055 & rasa run --enable-api --cors "*" --port 8080 & python3 frontend/app.py