-- Script para limpiar y resetear la base de datos
-- Ejecutar: psql -U postgres -d readiego -f reset_database.sql

-- Eliminar todas las calificaciones (si existen)
TRUNCATE TABLE ratings CASCADE;

-- Opcional: Si quieres eliminar TODO y empezar de cero, descomenta estas líneas:
-- DROP TABLE IF EXISTS ratings CASCADE;
-- DROP TABLE IF EXISTS books CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP VIEW IF EXISTS explicit_ratings CASCADE;

-- Mensaje de confirmación
SELECT 'Base de datos limpiada exitosamente' as mensaje;
