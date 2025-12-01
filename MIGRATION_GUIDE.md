# Guía de Migración: CSV → PostgreSQL

Esta guía te ayudará a migrar tu aplicación Readiego de archivos CSV a PostgreSQL.

## 📋 Resumen de Cambios

### Archivos Nuevos
- `database/schema.sql` - Script SQL para crear las tablas
- `database/migrate_csv_to_db.py` - Script Python para migrar datos
- `database/README.md` - Documentación detallada de la migración
- `backend/database.py` - Clase para manejar conexiones a PostgreSQL
- `backend/.env` - Configuración de base de datos
- `backend/.env.example` - Plantilla de configuración

### Archivos Modificados
- `backend/requirements.txt` - Agregadas dependencias de PostgreSQL
- `backend/data_loader.py` - Ahora usa PostgreSQL en lugar de CSV

### Archivos Respaldados
- `backend/data_loader_csv_backup.py` - Versión original que usa CSV (por si necesitas volver atrás)

## 🚀 Pasos para Migrar

### Paso 1: Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

Esto instalará:
- `psycopg2-binary` - Driver de PostgreSQL
- `sqlalchemy` - ORM (opcional, para uso futuro)
- `tqdm` - Barra de progreso para la migración

### Paso 2: Configurar Credenciales

Edita el archivo `backend/.env` y actualiza la contraseña de PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=readiego
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_AQUI  # ← Cambia esto
```

**IMPORTANTE**: Si tu PostgreSQL usa un puerto diferente o usuario diferente, actualiza esos valores también.

### Paso 3: Ejecutar Migración

```bash
cd database
python migrate_csv_to_db.py
```

El script hará:
1. ✅ Crear la base de datos `readiego`
2. ✅ Crear las tablas (books, users, ratings)
3. ✅ Migrar ~271,000 libros
4. ✅ Migrar ~278,000 usuarios
5. ✅ Migrar ~1,149,000 calificaciones
6. ✅ Crear índices para optimizar consultas
7. ✅ Verificar que todo esté correcto

**Tiempo estimado**: 5-10 minutos (dependiendo de tu hardware)

### Paso 4: Iniciar la Aplicación

```bash
cd backend
python app.py
```

¡Eso es todo! La aplicación ahora usa PostgreSQL automáticamente.

## 🔍 Verificación

Para verificar que todo funciona correctamente:

### 1. Verificar Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres -d readiego

# Ver estadísticas
SELECT COUNT(*) FROM books;    -- Debería ser ~271,360
SELECT COUNT(*) FROM users;    -- Debería ser ~278,858
SELECT COUNT(*) FROM ratings;  -- Debería ser ~1,149,780
```

### 2. Probar API

Abre el navegador en `http://localhost:5000/api/health`

Deberías ver estadísticas del sistema.

### 3. Probar Frontend

```bash
cd frontend
npm run dev
```

Navega a `http://localhost:5173` y prueba las recomendaciones.

## 📊 Ventajas de PostgreSQL vs CSV

### Rendimiento
- ✅ **Consultas más rápidas**: Los índices aceleran las búsquedas
- ✅ **Menos memoria**: No carga todos los datos en RAM
- ✅ **Muestreo aleatorio eficiente**: `ORDER BY RANDOM() LIMIT N` es más rápido

### Escalabilidad
- ✅ **Datos persistentes**: No necesitas recargar CSV cada vez
- ✅ **Actualizaciones en tiempo real**: Puedes agregar/modificar datos sin reiniciar
- ✅ **Múltiples aplicaciones**: Otras apps pueden conectarse a la misma BD

### Mantenimiento
- ✅ **Integridad referencial**: Las foreign keys previenen datos inconsistentes
- ✅ **Transacciones**: Operaciones ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad)
- ✅ **Respaldos**: PostgreSQL tiene herramientas de backup integradas

## 🔧 Configuración Avanzada

### Ajustar Tamaño de Muestra

En el archivo `.env`:

```env
USE_SAMPLE=True      # False para usar todos los datos
SAMPLE_SIZE=10000    # Número de calificaciones para modo desarrollo
```

O directamente en `backend/app.py`:

```python
initialize_system(use_sample=True, sample_size=5000)
```

### Optimización de PostgreSQL

Para mejor rendimiento con el dataset completo:

```sql
-- Conectar a la BD
psql -U postgres -d readiego

-- Analizar tablas para optimizar queries
ANALYZE books;
ANALYZE users;
ANALYZE ratings;

-- Ver tamaño de las tablas
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables
WHERE schemaname = 'public';
```

## 🔙 Rollback (Volver a CSV)

Si necesitas volver a la versión con CSV:

```bash
cd backend
mv data_loader.py data_loader_db_backup.py
mv data_loader_csv_backup.py data_loader.py
```

Luego reinicia `python app.py`

## ❓ Problemas Comunes

### Error: "could not connect to server"
- Verifica que PostgreSQL esté corriendo:
  ```bash
  # Windows
  services.msc  # Buscar "PostgreSQL"

  # Linux/Mac
  sudo systemctl status postgresql
  ```

### Error: "password authentication failed"
- Verifica la contraseña en `backend/.env`
- Prueba conectarte manualmente: `psql -U postgres`

### Error: "relation does not exist"
- Vuelve a ejecutar el schema:
  ```bash
  psql -U postgres -d readiego -f database/schema.sql
  ```

### La migración es muy lenta
- Es normal, 1M+ registros toman tiempo
- El script muestra el progreso
- Puedes tomar un café ☕

### Error: "FATAL: database does not exist"
- Crea la base de datos manualmente:
  ```bash
  psql -U postgres
  CREATE DATABASE readiego;
  \q
  ```

## 📚 Próximos Pasos

Ahora que tienes PostgreSQL, puedes:

1. **Agregar nuevas funcionalidades**:
   - Sistema de usuarios con autenticación
   - Agregar/editar calificaciones en tiempo real
   - Guardar listas de favoritos

2. **Optimizar recomendaciones**:
   - Cachear resultados en una tabla
   - Calcular similitudes de forma batch
   - Usar materialized views

3. **Analytics**:
   - Crear dashboards con estadísticas
   - Trending books del mes
   - Recomendaciones por demografía

4. **Deploy**:
   - Usar servicios como Heroku PostgreSQL
   - Amazon RDS
   - Digital Ocean Managed Databases

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del script de migración
2. Consulta `database/README.md` para comandos SQL útiles
3. Verifica que PostgreSQL esté corriendo y accesible

¡Disfruta de tu nueva base de datos! 🎉
