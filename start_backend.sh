set -e

# Function to handle errors
handle_error() {
    echo "🚨 Error at line $1: $2"
    exit 1
}

# Function for cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    if [ -n "$UVICORN_PID" ]; then
        echo "🛑 Stopping Uvicorn (PID: $UVICORN_PID)..."
        kill $UVICORN_PID 2>/dev/null || true
    fi
    echo "✅ Cleanup complete"
}

# Trap errors and cleanup
trap 'handle_error $LINENO "$BASH_COMMAND"' ERR
trap cleanup EXIT

echo "🚀 Starting DockDineStay Production Deployment..."

# --- Backend Setup ---
echo ""
echo "🔧 Backend Setup"
echo "📂 Entering backend directory..."
cd backend || handle_error $LINENO "Failed to enter backend directory"

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🛠️ Installing backend package..."
pip install .

echo "🌐 Starting Uvicorn server in production mode..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 >> uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "✅ Uvicorn running (PID: $UVICORN_PID) - http://localhost:8000"
echo "📝 Logs: backend/uvicorn.log"

cd ..