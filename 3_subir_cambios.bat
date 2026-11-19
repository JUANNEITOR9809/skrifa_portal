@echo off
cd /d "%~dp0"
echo Subiendo cambios de Skrifa Labs a GitHub...
git add -A
git commit -m "Agregar logo de Skrifa Labs"
git push
echo.
echo Listo. Render publicara los cambios en unos minutos.
pause
