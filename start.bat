@echo off
chcp 65001 > nul
echo ============================================================
echo  统一太乙系统 - 一键启动
echo ============================================================

:: 杀掉占用5000端口的进程
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5000 "') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 > nul

:: 启动Flask
cd /d "%~dp0"
echo [启动] Flask 后端...
start "统一太乙系统" python app.py

:: 等待启动
timeout /t 4 > nul

echo [完成] 服务已启动
echo [访问] http://localhost:5000
echo ============================================================
pause
