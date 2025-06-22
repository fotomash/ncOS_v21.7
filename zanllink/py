# launch.sh
#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start the full ZanLink system

echo "[🔄] Building containers..."
docker-compose build

echo "[🚀] Launching ZanLink API and Macro Cron..."
docker-compose up -d

echo "[✅] ZanLink is live at http://localhost:${ZANLINK_PORT}"
echo "[📡] Macro updates every 15 minutes from cron container"
