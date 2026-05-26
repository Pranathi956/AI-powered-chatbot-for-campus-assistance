FROM python:3.9-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy all files
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r Backend/requirements.txt

# Railway PORT variable pick cheskovadam kosam
ENV PORT=8000

# Rasa model ni properly point chesthu, memory leak avvakunda run cheyali
CMD rasa run actions --actions Backend.actions --port 5055 & \
    rasa run --enable-api --cors "*" --port 5005 --model Backend/models & \
    python3 frontend/app.py