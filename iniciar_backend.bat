@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
echo Iniciando o backend do Rato CyberLab...
where python >nul 2>nul
if %errorlevel%==0 (
  python server.py
) else (
  py server.py
)
pause
