#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif [ -x "$SCRIPT_DIR/.venv/Scripts/python.exe" ]; then
    VENV_PYTHON="$SCRIPT_DIR/.venv/Scripts/python.exe"
else
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN=python
    else
        echo "Python 3 is required but was not found in PATH." >&2
        exit 1
    fi

    echo "Creating virtual environment in .venv..."
    "$PYTHON_BIN" -m venv .venv

    if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
        VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
    elif [ -x "$SCRIPT_DIR/.venv/Scripts/python.exe" ]; then
        VENV_PYTHON="$SCRIPT_DIR/.venv/Scripts/python.exe"
    else
        echo "Virtual environment creation failed." >&2
        exit 1
    fi
fi

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
"$VENV_PYTHON" -m pip install -r requirements.txt

if [ ! -f .env ]; then
    cat > .env <<'EOF'
SECRET_KEY=change-me-to-a-long-random-value
API_KEY=change-me-to-a-long-random-value
DEBUG=False
EOF
    echo "Created .env with default values. Please review it before using the app." 
fi

echo "Running Django migrations..."
"$VENV_PYTHON" manage.py makemigrations
"$VENV_PYTHON" manage.py migrate

echo "Setup complete."
echo "Activate the environment with: source .venv/bin/activate"
