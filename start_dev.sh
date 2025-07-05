#!/bin/bash

# This script automates the setup and running of your backend and frontend.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Development Environment Setup ---"

# --- Backend Setup ---
echo ""
echo "--- Setting up Backend ---"
echo "Navigating to backend directory..."
cd backend

echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Installing backend package from pyproject.toml..."
pip install .

echo "Starting Uvicorn server in the background (main:app --reload)..."
# The '&' at the end runs the command in the background
# The 'nohup' ensures it keeps running even if you close the terminal
# The '>> uvicorn.log 2>&1' redirects all output to a log file
nohup uvicorn main:app --reload >> uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "Uvicorn server started with PID: $UVICORN_PID. Check uvicorn.log for output."
echo "You can stop the backend later by running: kill $UVICORN_PID"

# Navigate back to the root directory
echo "Navigating back to root directory..."
cd ..

# --- Frontend Setup ---
echo ""
echo "--- Setting up Frontend ---"
echo "my current directory"
pwd
ls

echo "Navigating to dockdinestay (frontend) directory..."
cd DockDineStay/frontend/dockdinestay

echo "Verifying Node.js and npm installation..."
if ! command -v node &> /dev/null
then
    echo "Node.js is not installed."
    echo "npm is typically installed with Node.js."
    echo "Please install Node.js first. Recommended methods:"
    echo "  - Using nvm (Node Version Manager): https://github.com/nvm-sh/nvm#installing-and-updating"
    echo "  - Using your system's package manager (e.g., 'sudo apt install nodejs npm' on Debian/Ubuntu, 'brew install node' on macOS)."
    echo "Exiting script. Please install Node.js and npm, then run this script again."
    exit 1
fi
echo "Node.js and npm are installed."

echo "Installing frontend dependencies (npm install)..."
npm install

echo "Starting React development server (npm run dev)..."
npm run dev

echo ""
echo "--- Development Environment Setup Complete ---"
echo "Backend Uvicorn server is running in the background (PID: $UVICORN_PID)."
echo "Frontend React development server is now running."
echo "If you need to stop the Uvicorn backend, use: kill $UVICORN_PID"

# Adjust the number of workers based on your Render plan and app needs
# This assumes your FastAPI app is named 'app' in 'main.py'
# exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app