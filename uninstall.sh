#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "Removing virtual environment..."
    rm -rf "$SCRIPT_DIR/.venv"
fi

if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Removing .env file..."
    rm -f "$SCRIPT_DIR/.env"
fi

if [ -f "$SCRIPT_DIR/db.sqlite3" ]; then
    echo "Removing database file..."
    rm -f "$SCRIPT_DIR/db.sqlite3"
fi

echo "Uninstall complete."
