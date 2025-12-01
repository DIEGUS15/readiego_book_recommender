@echo off
echo ========================================
echo   READIEGO - Setup PostgreSQL Database
echo ========================================
echo.

echo [1/3] Instalando dependencias de Python...
cd backend
pip install -r requirements.txt
echo.

echo [2/3] Configuracion de credenciales
echo IMPORTANTE: Edita backend/.env con tu contraseña de PostgreSQL
echo Presiona cualquier tecla cuando hayas actualizado el archivo .env
pause
echo.

echo [3/3] Ejecutando migracion...
cd ..\database
python migrate_csv_to_db.py
echo.

echo ========================================
echo   Migracion completada!
echo ========================================
echo.
echo Proximos pasos:
echo   1. cd backend
echo   2. python app.py
echo.
pause
