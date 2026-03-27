#!/usr/bin/env bash
set -euo pipefail

# setup_server.sh
# 1) Set up PostgreSQL database and user
# 2) Generate .env with secure values
# 3) Install Python dependencies
# 4) Run Django migrations

# prompt default helper
read_or_default() {
    local prompt="$1"
    local default="$2"
    read -r -p "$prompt [$default]: " val
    if [[ -z "$val" ]]; then
        echo "$default"
    else
        echo "$val"
    fi
}

# generate random string
random_string() {
    local length=${1:-64}
    tr -dc 'A-Za-z0-9_@%+=-:.,' </dev/urandom | head -c "$length" || true
}

PG_CMD_DEF='sudo -u postgres'
PG_CMD=$(read_or_default "PostgreSQL superuser command" "$PG_CMD_DEF")
DB_NAME=$(read_or_default "Database name" "elo_db")
DB_USER=$(read_or_default "Database user" "byte.blast")
read -r -p "Database password (leave empty to generate one): " DB_PASS
if [[ -z "$DB_PASS" ]]; then
    DB_PASS=$(random_string 32)
fi

read -r -p "API key (leave empty to generate one): " API_KEY
if [[ -z "$API_KEY" ]]; then
    API_KEY=$(random_string 48)
fi

read -r -p "Django SECRET_KEY (leave empty to generate one): " SECRET_KEY
if [[ -z "$SECRET_KEY" ]]; then
    SECRET_KEY=$(random_string 50)
fi

echo "\n*** Database setup ***"
$PG_CMD psql -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
$PG_CMD psql -v ON_ERROR_STOP=1 -c "DROP USER IF EXISTS \"$DB_USER\";"
$PG_CMD psql -v ON_ERROR_STOP=1 -c "CREATE USER \"$DB_USER\" WITH PASSWORD '$DB_PASS';"
$PG_CMD psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"

ENV_FILE=".env"
cat > "$ENV_FILE" <<EOF
SECRET_KEY=$SECRET_KEY
API_KEY=$API_KEY
POSTGRES_PASSWORD=$DB_PASS
EOF

echo "\n*** .env file written ***"

echo "\n*** Installing Python dependencies ***"
python -m pip install -U pip
pip install -r requirements.txt

echo "\n*** Running Django migrations ***"
python manage.py migrate

echo "\n*** Finished! ***"
cat <<INFO
Your project is now configured with:
  DB_NAME = $DB_NAME
  DB_USER = $DB_USER
  API_KEY = $API_KEY
  Secret key = $SECRET_KEY

Run server:
  python manage.py runserver

Use endpoint example:
  curl -s "http://localhost:8000/api/v1/leaderboard/mace/?page=1"
INFO
