@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   DataOps Studio - 一键启动
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

:: 安装后端依赖
echo [1/4] 安装后端依赖...
cd /d "%~dp0backend"
pip install -r requirements.txt -q

:: 安装前端依赖
echo [2/4] 安装前端依赖...
cd /d "%~dp0frontend"
if not exist node_modules (
    call npm install
) else (
    echo      已存在 node_modules，跳过安装
)

:: 启动后端
echo [3/4] 启动后端 API (端口 8000)...
cd /d "%~dp0backend"
start "DataOps-Backend" cmd /k "python -m uvicorn main:app --reload --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo [4/4] 启动前端 (端口 6660)...
cd /d "%~dp0frontend"
start "DataOps-Frontend" cmd /k "npx vite --port 6660 --open"

echo.
echo ============================================
echo   启动完成!
echo   前端: http://localhost:6660
echo   后端: http://localhost:8000/docs
echo ============================================
echo.
echo 按任意键退出此窗口（后端和前端会继续运行）
pause >nul
