#!/usr/bin/env fish
set SCRIPT_DIR (cd (dirname (status --current-filename)) && pwd)
cd "$SCRIPT_DIR"

if test -x "$SCRIPT_DIR/.venv/bin/python"
    set VENV_PYTHON "$SCRIPT_DIR/.venv/bin/python"
else if test -x "$SCRIPT_DIR/.venv/Scripts/python.exe"
    set VENV_PYTHON "$SCRIPT_DIR/.venv/Scripts/python.exe"
else
    if command -s python3 >/dev/null 2>&1
        set PYTHON_BIN python3
    else if command -s python >/dev/null 2>&1
        set PYTHON_BIN python
    else
        echo "Python 3 is required but was not found in PATH." >&2
        exit 1
    end

    echo "Creating virtual environment in .venv..."
    "$PYTHON_BIN" -m venv .venv

    if test -x "$SCRIPT_DIR/.venv/bin/python"
        set VENV_PYTHON "$SCRIPT_DIR/.venv/bin/python"
    else if test -x "$SCRIPT_DIR/.venv/Scripts/python.exe"
        set VENV_PYTHON "$SCRIPT_DIR/.venv/Scripts/python.exe"
    else
        echo "Virtual environment creation failed." >&2
        exit 1
    end
end

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
"$VENV_PYTHON" -m pip install -r requirements.txt

if not test -f .env
    printf '%s
' 'SECRET_KEY=change-me-to-a-long-random-value' 'API_KEY=change-me-to-a-long-random-value' 'DEBUG=False' > .env
    echo "Created .env with default values. Please review it before using the app."
end

echo "Running Django migrations..."
"$VENV_PYTHON" manage.py makemigrations
"$VENV_PYTHON" manage.py migrate

echo "Setup complete."
echo "Activate the environment with: source .venv/bin/activate"
