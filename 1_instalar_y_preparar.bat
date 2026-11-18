@echo off
cd /d "%~dp0"
echo Instalando dependencias del Portal Skrifa Labs...
python -m pip install -r requirements.txt
echo.
echo Preparando la base de datos y el cliente de ejemplo...
python manage.py migrate
python manage.py crear_demo
echo.
echo Revisando el proyecto...
python manage.py check
python manage.py makemigrations --check --dry-run
echo.
echo Listo. Ahora abra 2_iniciar_servidor.bat
pause
