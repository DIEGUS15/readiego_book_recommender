# Migración de CSV a PostgreSQL

Este directorio contiene los scripts necesarios para migrar los datos de CSV a PostgreSQL.

## Prerrequisitos

1. **PostgreSQL instalado y corriendo**
   - Verifica que PostgreSQL esté instalado: `psql --version`
   - Asegúrate de que el servicio esté corriendo

2. **Credenciales de PostgreSQL**
   - Usuario: `postgres` (por defecto)
   - Contraseña: Define tu contraseña

3. **Dependencias de Python**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

## Pasos para la Migración

### 1. Configurar credenciales

Edita el archivo `backend/.env` con tus credenciales de PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=readiego
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
```

### 2. Editar configuración del script (opcional)

Si necesitas cambiar las credenciales, edita `migrate_csv_to_db.py`:

```python
DB_CONFIG = {
    'dbname': 'readiego',
    'user': 'postgres',
    'password': 'tu_contraseña',  # Cambiar aquí
    'host': 'localhost',
    'port': '5432'
}
```

### 3. Ejecutar migración

```bash
cd database
python migrate_csv_to_db.py
```

El script hará lo siguiente:
1. Crear la base de datos `readiego` si no existe
2. Crear las tablas usando `schema.sql`
3. Migrar los datos desde los archivos CSV:
   - Books.csv → tabla `books`
   - Users.csv → tabla `users`
   - Ratings.csv → tabla `ratings`
4. Verificar que la migración fue exitosa

### 4. Verificar migración

El script mostrará estadísticas al final:
```
📊 Estadísticas de la base de datos:
   📚 Libros: 271,360
   👥 Usuarios: 278,858
   ⭐ Calificaciones totales: 1,149,780
   ⭐ Calificaciones explícitas (rating > 0): 433,671
```

## Estructura de la Base de Datos

### Tabla `books`
- `isbn` (VARCHAR, PRIMARY KEY): ISBN del libro
- `title` (VARCHAR): Título del libro
- `author` (VARCHAR): Autor
- `year_of_publication` (INTEGER): Año de publicación
- `publisher` (VARCHAR): Editorial
- `image_url_s/m/l` (VARCHAR): URLs de imágenes

### Tabla `users`
- `user_id` (INTEGER, PRIMARY KEY): ID del usuario
- `location` (VARCHAR): Ubicación
- `age` (INTEGER): Edad

### Tabla `ratings`
- `id` (SERIAL, PRIMARY KEY): ID auto-incremental
- `user_id` (INTEGER, FOREIGN KEY): ID del usuario
- `isbn` (VARCHAR, FOREIGN KEY): ISBN del libro
- `rating` (INTEGER): Calificación (0-10)

### Vista `explicit_ratings`
Vista que filtra solo calificaciones explícitas (rating > 0), usada por el sistema de recomendaciones.

## Uso de la Base de Datos en la Aplicación

Después de la migración, el código ya está configurado para usar PostgreSQL automáticamente:

1. El `DataLoader` ahora lee de la base de datos en lugar de CSV
2. Las consultas se optimizan con índices
3. Los datos se cargan más rápido que desde CSV

## Comandos Útiles de PostgreSQL

### Conectar a la base de datos
```bash
psql -U postgres -d readiego
```

### Consultas útiles
```sql
-- Ver cantidad de registros
SELECT COUNT(*) FROM books;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM ratings;

-- Ver calificaciones explícitas
SELECT COUNT(*) FROM explicit_ratings;

-- Ver libros más calificados
SELECT b.title, COUNT(*) as num_ratings
FROM books b
JOIN ratings r ON b.isbn = r.isbn
GROUP BY b.title
ORDER BY num_ratings DESC
LIMIT 10;

-- Ver usuarios más activos
SELECT u.user_id, u.location, COUNT(*) as num_ratings
FROM users u
JOIN ratings r ON u.user_id = r.user_id
GROUP BY u.user_id, u.location
ORDER BY num_ratings DESC
LIMIT 10;
```

## Troubleshooting

### Error: "database does not exist"
El script debería crear la base de datos automáticamente. Si falla, créala manualmente:
```bash
psql -U postgres
CREATE DATABASE readiego;
```

### Error: "password authentication failed"
Verifica que la contraseña en `DB_CONFIG` sea correcta.

### Error: "relation does not exist"
Las tablas no fueron creadas. Ejecuta el schema manualmente:
```bash
psql -U postgres -d readiego -f schema.sql
```

### Performance lenta
La migración de 1M+ registros puede tomar varios minutos. El script muestra el progreso.

## Rollback (Volver a CSV)

Si necesitas volver a usar CSV:

```bash
cd backend
mv data_loader.py data_loader_db_backup.py
mv data_loader_csv_backup.py data_loader.py
```

Luego reinicia la aplicación.
