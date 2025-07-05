#!/bin/bash

# This script automates the setup and running of your backend and frontend.

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to handle cleanup
cleanup() {
    echo ""
    echo "--- Cleaning up ---"
    if [ -n "$UVICORN_PID" ]; then
        echo "Stopping Uvicorn server (PID: $UVICORN_PID)..."
        kill $UVICORN_PID 2>/dev/null || true
    fi
    echo "Cleanup complete"
}

# Trap EXIT signal to ensure cleanup runs
trap cleanup EXIT

echo "--- Starting Development Environment Setup ---"

# --- Backend Setup ---
echo ""
echo "--- Setting up Backend ---"
echo "Navigating to backend directory..."
cd backend || { echo "Failed to enter backend directory"; exit 1; }

echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Installing backend package from pyproject.toml..."
pip install -e .

echo "Starting Uvicorn server in the background (main:app --reload)..."
# Run in background and redirect output to log file
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 >> uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "Uvicorn server started with PID: $UVICORN_PID. Check uvicorn.log for output."
echo "You can stop the backend later by running: kill $UVICORN_PID"

# Navigate back to the root directory
echo "Navigating back to root directory..."
cd ..

# --- Frontend Setup ---
echo ""
echo "--- Setting up Frontend ---"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls

echo "Navigating to frontend directory..."
cd frontend/dockDineStay || { echo "Failed to enter frontend directory"; exit 1; }

echo "Verifying Node.js and npm installation..."
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "Node.js or npm not found. Attempting to install..."
    
    # Try different installation methods
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        if ! command -v brew &> /dev/null; then
            echo "Homebrew not found. Please install Homebrew first: https://brew.sh"
            exit 1
        fi
        brew install node
    else
        echo "Unsupported OS. Please install Node.js manually from https://nodejs.org"
        exit 1
    fi
    
    echo "Node.js $(node -v) and npm $(npm -v) installed successfully"
else
    echo "Node.js $(node -v) and npm $(npm -v) are already installed"
fi

# Ensure specific versions of critical packages are installed
echo "Ensuring required package versions are installed..."
npm install --save-exact \
    react-router-dom@6.14.2 \
    jwt-decode@3.1.2 \
    @types/date-fns@2.6.0 \
    axios@1.5.0 \
    date-fns@2.30.0

echo "Installing all frontend dependencies..."
npm install

echo "Starting React development server..."
npm run dev

echo ""
echo "--- Development Environment Setup Complete ---"
echo "Backend:"
echo "  - Running on http://localhost:8000 (PID: $UVICORN_PID)"
echo "  - Logs: backend/uvicorn.log"
echo "Frontend:"
echo "  - Should be running on http://localhost:3000 (or port shown above)"
echo ""
echo "To stop both servers, simply close this terminal or press Ctrl+C"