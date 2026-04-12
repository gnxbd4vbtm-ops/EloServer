#!/bin/bash

rm *.log
rm *.log.*

set -e
sudo apt update
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null

echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list

sudo apt install ngrok

docker start postgres 2>/dev/null || docker run -d --name postgres \
  -p 5433:5432 \
  -e POSTGRES_DB=elo \
  -e POSTGRES_USER=byte.blast \
  -e POSTGRES_PASSWORD='n6T5Z8.' \
  postgres

sleep 3

python manage.py migrate
uvicorn elosystem.asgi:application --reload &
python "dc_stuff/elo getter/MCR_Bot.py" &
ngrok http 8000 &