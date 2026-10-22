@echo off
title Drive Tec · servidor de desarrollo
cd /d "%~dp0"
set DEBUG=1
echo === Drive Tec ===
echo Modo simulado activo (sin claves de Google). Para Whisper/Google, usa start.ps1.
echo Detener el servidor: Ctrl+C en ESTA ventana.
echo.
python manage.py migrate --no-input 2>nul
if errorlevel 1 (
  echo ERROR: faltan dependencias. Ejecuta: python -m pip install -r requirements.txt
  pause
  exit /b 1
)
start "" http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
