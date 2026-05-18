@echo off
title SmartLearn Startup

echo.
echo  ============================================
echo     SmartLearn - One-Click Startup
echo  ============================================
echo.

set "BASE_DIR=%~dp0"

:: ---- Kill old services ----
echo  Stopping old services...
taskkill /F /IM java.exe  >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe   >nul 2>&1
timeout /t 2 /nobreak >nul
echo  Cleanup done.
echo.

echo  [1/3] Starting FastAPI on port 8000...
start "SmartLearn-FastAPI" cmd /k "cd /d "%BASE_DIR%fastapi-ai" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 4 /nobreak >nul

echo  [2/3] Starting SpringBoot on port 8080...
start "SmartLearn-SpringBoot" cmd /k "cd /d "%BASE_DIR%springboot-backend" && mvn spring-boot:run"

timeout /t 15 /nobreak >nul

echo  [3/3] Starting Vue3 Frontend on port 5173...
start "SmartLearn-Vue" cmd /k "cd /d "%BASE_DIR%frontend" && npm run dev"

echo.
echo  ============================================
echo    All services launching!
echo.
echo    FastAPI   : http://localhost:8000/docs
echo    SpringBoot: http://localhost:8080
echo    Frontend  : http://localhost:5173
echo  ============================================
echo.
echo  Press any key to open frontend...
pause >nul
start http://localhost:5173
