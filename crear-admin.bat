@echo off
title Drive Tec · crear superusuario
cd /d "%~dp0"
set DEBUG=1
python manage.py createsuperuser
echo.
echo Listo. Inicia sesion en http://127.0.0.1:8000/admin/ o en http://127.0.0.1:8000/
pause
