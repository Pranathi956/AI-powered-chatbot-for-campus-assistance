FROM python:3.9-slim

WORKDIR /app

# 1. System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 2. Copy all files first (Idhi chesthe Backend, frontend, models anni okesaari vachestayi)
COPY . .

# 3. Install requirements (Backend folder nundi pick chestunnam)
RUN pip install --no-cache-dir -r Backend/requirements.txt

# 4. Ports expose cheyalsina avasaram ledu kaani safety ki uncham
EXPOSE 8000
EXPOSE 5005
EXPOSE 5055

# 5. Final Command
# Rasa ni 5005 port lo, Model ni Backend/models folder nundi load chestunnam
CMD rasa run actions --actions Backend.actions --port 5055 & \
    rasa run --enable-api --cors "*" --port 5005 --model Backend/models & \
    python3 frontend/app.py