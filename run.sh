#!/bin/bash
# ==============================================================================
# ShieldAgent: One-Click Development & Demo Runner
# PayPal AI Hackathon: Build what's next with PayPal and AI
# ==============================================================================

set -e

echo ""
echo "================================================================================"
echo " 🛡️ Starting ShieldAgent - PayPal Autonomous Dispute Defense Engine"
echo "================================================================================"
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js and npm are required but not installed."
    exit 1
fi

# Setup Python Virtual Environment if needed
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$BACKEND_DIR/.venv"
    "$BACKEND_DIR/.venv/bin/pip" install --upgrade pip
    "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

# Setup Frontend if node_modules missing
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦 Installing Frontend dependencies..."
    npm install --prefix "$FRONTEND_DIR"
fi

# Cleanup on exit
trap 'echo ""; echo "🛑 Stopping ShieldAgent servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' SIGINT SIGTERM

echo "🚀 Starting FastAPI Backend at http://localhost:8000 ..."
cd "$BACKEND_DIR"
"$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "🚀 Starting React Frontend at http://localhost:3000 ..."
cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

echo ""
echo "================================================================================"
echo " ✅ ShieldAgent is running!"
echo " 👉 Merchant Command Center:  http://localhost:3000"
echo " 👉 Interactive API Docs:     http://localhost:8000/docs"
echo " 👉 Sample Printable Packet:  http://localhost:8000/api/v1/disputes/PP-D-83921/dossier/html"
echo "================================================================================"
echo " Press Ctrl+C to stop all servers."
echo ""

wait
