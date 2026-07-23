@echo off
chcp 65001 >nul
REM ========================================
REM 云南省人社厅通知监控 - 每日定时任务脚本
REM 用途：配合 Windows 任务计划程序，每天10:00执行
REM ========================================

cd /d "%~dp0"

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python
    exit /b 1
)

REM 单次运行模式执行监控任务
python monitor.py --once

exit /b 0
