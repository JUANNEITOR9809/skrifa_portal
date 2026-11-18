@echo off
cd /d "%~dp0"
echo Iniciando el Portal Skrifa Labs en http://127.0.0.1:8000
echo Usuario: gerencia@ferreteriaeltornillo.co  Clave: Tornillo2026
echo Para detenerlo cierre esta ventana.
start "" http://127.0.0.1:8000
python manage.py runserver
pause
