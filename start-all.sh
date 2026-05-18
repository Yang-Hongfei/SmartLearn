#!/bin/bash
# SmartLearn One-Click Startup (Git Bash / Linux / macOS)

set -e
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "============================================"
echo "  SmartLearn - One-Click Startup"
echo "============================================"
echo ""

# ---- Kill existing processes on target ports ----
cleanup_port() {
    local port=$1
    local pid=$(netstat -ano 2>/dev/null | grep ":$port " | grep "LISTENING" | awk '{print $5}' | head -1)
    if [ -n "$pid" ]; then
        echo "  Stopping process on port $port (PID: $pid)"
        taskkill //F //PID "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
    fi
}

echo "Cleaning up existing services..."
cleanup_port 8000
cleanup_port 8080
cleanup_port 5173
sleep 2
echo "Cleanup done."
echo ""

# ---- Start FastAPI ----
echo "[1/3] Starting FastAPI on port 8000..."
cd "$BASE_DIR/fastapi-ai"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
FAPI_PID=$!
echo "       PID: $FAPI_PID"
sleep 3

# ---- Start SpringBoot ----
echo "[2/3] Starting SpringBoot on port 8080..."
cd "$BASE_DIR/springboot-backend"
mvn spring-boot:run &
BOOT_PID=$!
echo "       PID: $BOOT_PID"
sleep 15

# ---- Start Vue3 Frontend ----
echo "[3/3] Starting Vue3 Frontend on port 5173..."
cd "$BASE_DIR/frontend"
npm run dev &
VUE_PID=$!
echo "       PID: $VUE_PID"

echo ""
echo "============================================"
echo "  All services launching!"
echo ""
echo "  FastAPI   : http://localhost:8000/docs"
echo "  SpringBoot: http://localhost:8080"
echo "  Frontend  : http://localhost:5173"
echo "============================================"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $FAPI_PID 2>/dev/null
    kill $BOOT_PID 2>/dev/null
    kill $VUE_PID 2>/dev/null
    echo "All services stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM
wait
