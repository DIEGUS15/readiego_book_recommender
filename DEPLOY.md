# 🚀 Despliegue Rápido con Docker

## ⚡ Inicio Rápido (3 pasos)

### 1. Crear configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y cambiar las contraseñas
# DB_PASSWORD=tu_password_aqui
```

### 2. Iniciar servicios

```bash
docker-compose up -d
```

### 3. Verificar

Abre tu navegador en: http://localhost:5000/api/health

¡Listo! 🎉

---

## 📦 Qué se Inicia

✅ **PostgreSQL** en puerto `5432`
✅ **Backend Flask** en puerto `5000`

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener todo
docker-compose down

# Reiniciar
docker-compose restart

# Ver estado
docker-compose ps
```

---

## 📊 Cargar Datos

Si es la primera vez y tienes los CSV:

```bash
# 1. Copiar CSVs a carpeta data/
#    - Books.csv
#    - Ratings.csv
#    - Users.csv

# 2. Ejecutar migración
docker-compose exec backend python ../database/migrate_csv_to_db.py
```

---

## 🔧 Acceder a PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d readiego
```

Comandos útiles dentro de psql:
```sql
\dt                      -- Ver tablas
SELECT COUNT(*) FROM books;
SELECT COUNT(*) FROM ratings;
\q                       -- Salir
```

---

## 🐛 Problemas Comunes

### "Port already in use"

Cambia el puerto en `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Cambia 8080 al que quieras
```

### Backend no inicia

```bash
# Ver logs
docker-compose logs backend

# Reconstruir
docker-compose build --no-cache backend
docker-compose up -d
```

### Error de conexión a BD

```bash
# Verificar que PostgreSQL esté listo
docker-compose exec postgres pg_isready -U postgres
```

---

## 🔐 Producción

Antes de deployar en producción:

1. **Cambia las contraseñas** en `.env`
2. **Configura HTTPS** (Nginx + Let's Encrypt)
3. **No expongas PostgreSQL** (comenta el puerto 5432 en docker-compose.yml)
4. **Configura backups** de la base de datos

Ver [DOCKER_SETUP.md](DOCKER_SETUP.md) para guía completa.

---

## 📚 Más Info

- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Guía completa de Docker
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migración de CSV a PostgreSQL
- [CLAUDE.md](CLAUDE.md) - Documentación del proyecto
