#!/bin/bash

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "node server.js"
pkill -f "streamlit run app.py"

# Ensure venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Determine absolute paths for venv executables
VENV_PYTHON="./.venv/bin/python"
VENV_PIP="./.venv/bin/pip"
VENV_STREAMLIT="./.venv/bin/streamlit"

echo "Installing dependencies..."
# Update npm install to be silent to reduce noise
npm install --silent
$VENV_PIP install -r requirements.txt

echo "Starting backend..."
node server.js > backend.log 2>&1 &

echo "Starting frontend..."
$VENV_STREAMLIT run app.py > streamlit.log 2>&1 &

echo "Project started."
tail -f streamlit.log
