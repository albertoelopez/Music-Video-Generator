#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Audio to Music Video - Run Script ==="
echo ""

cd "$PROJECT_ROOT/backend"
source venv/bin/activate

echo "Starting backend API server..."
python run_server.py &
BACKEND_PID=$!

sleep 2

cd "$PROJECT_ROOT/frontend"
echo "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "Application is running!"
echo "  Backend API: http://localhost:5000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"

wait
