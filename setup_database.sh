#!/bin/bash

echo "========================================"
echo "  READIEGO - Setup PostgreSQL Database"
echo "========================================"
echo ""

echo "[1/3] Instalando dependencias de Python..."
cd backend
pip install -r requirements.txt
echo ""

echo "[2/3] Configuración de credenciales"
echo "IMPORTANTE: Edita backend/.env con tu contraseña de PostgreSQL"
echo "Presiona ENTER cuando hayas actualizado el archivo .env"
read -p ""
echo ""

echo "[3/3] Ejecutando migración..."
cd ../database
python migrate_csv_to_db.py
echo ""

echo "========================================"
echo "  Migración completada!"
echo "========================================"
echo ""
echo "Próximos pasos:"
echo "  1. cd backend"
echo "  2. python app.py"
echo ""
