# --- Frontend Setup ---
echo ""
echo "🎨 Frontend Setup"
echo "📂 Current directory: $(pwd)"
echo "📂 Directory contents:"
ls -l

echo "📂 Entering frontend directory..."
cd frontend/dockDineStay || handle_error $LINENO "Failed to enter frontend directory"

# Node.js setup
echo "🛠️ Checking Node.js..."
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "⚠️ Node.js/npm not found. Installing..."
    
    # Platform-specific installation
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install node
    else
        handle_error $LINENO "Unsupported OS for Node.js installation"
    fi
fi
echo "✅ Node.js $(node -v) and npm $(npm -v) installed"

# Install all dependencies including devDependencies
echo "📦 Installing all dependencies..."
npm install --include=dev

# Fix specific package versions to avoid conflicts
echo "📦 Ensuring correct package versions..."
npm install --save-exact \
    react-router-dom@6.14.2 \
    jwt-decode@3.1.2 \
    vite@4.4.9 \
    axios@1.5.0

# Fix jwt-decode import issue
echo "🔄 Fixing jwt-decode import..."
sed -i "s/import { jwtDecode } from \"jwt-decode\"/import jwtDecode from \"jwt-decode\"/g" src/context/AuthContext.tsx

# Fix axios resolution issue
echo "🔄 Fixing axios resolution..."
if [ -f "node_modules/axios/index.js" ]; then
    sed -i "s/\.\/lib\/axios.js/\.\/dist\/axios.js/g" node_modules/axios/index.js
fi

# Production build with specific Vite config
echo "🏗️ Building production assets..."
NODE_ENV=production npx vite build --emptyOutDir

echo "✅ Frontend build complete!"
echo "📦 Production assets created in: frontend/dockDineStay/dist"

echo ""
echo "🎉 Deployment Successful!"
echo "🔹 Backend: http://localhost:8000"
echo "🔹 Frontend production assets built"
echo "🔹 Uvicorn running (PID: $UVICORN_PID)"
echo "🔹 Check logs for detailed output"