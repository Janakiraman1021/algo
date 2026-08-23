@echo off
echo ===================================================
echo     Starting AgentPay (A2A + x402 + Algorand)
echo ===================================================

echo [1/3] Starting FastAPI Backend on http://localhost:8000 ...
start "AgentPay Backend (Port 8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"

echo [2/3] Starting x402 Adapter on http://localhost:4020 ...
start "AgentPay x402 Adapter (Port 4020)" cmd /k "cd /d %~dp0x402-adapter && npm run dev"

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "AgentPay Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo ===================================================
echo All 3 services launched in separate windows!
echo Open your browser at: http://localhost:3000
echo ===================================================
pause
