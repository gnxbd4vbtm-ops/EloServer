#!/usr/bin/env fish
set SCRIPT_DIR (cd (dirname (status --current-filename)) && pwd)
cd "$SCRIPT_DIR"

if test -d "$SCRIPT_DIR/.venv"
    echo "Removing virtual environment..."
    rm -rf "$SCRIPT_DIR/.venv"
end

if test -f "$SCRIPT_DIR/.env"
    echo "Removing .env file..."
    rm -f "$SCRIPT_DIR/.env"
end

if test -f "$SCRIPT_DIR/db.sqlite3"
    echo "Removing database file..."
    rm -f "$SCRIPT_DIR/db.sqlite3"
end

echo "Uninstall complete."
