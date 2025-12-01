# 🐳 Resumen: Docker Setup Completo

## ✅ Archivos Creados

```
readiego_book_recommender/
├── docker-compose.yml          ← Configuración de servicios
├── .env.example                ← Variables de entorno (ejemplo)
├── DEPLOY.md                   ← Guía rápida de despliegue
├── DOCKER_SETUP.md             ← Guía completa de Docker
│
├── backend/
│   ├── Dockerfile              ← Imagen del backend
│   ├── .dockerignore           ← Archivos a ignorar
│   └── .env.example            ← Actualizado con nuevas variables
│
└── database/
    └── schema.sql              ← Actualizado con tablas app_users
```

---

## 🚀 Cómo Usar (3 Comandos)

### 1️⃣ Configurar

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tus contraseñas
notepad .env   # Windows
nano .env      # Linux/Mac
```

### 2️⃣ Iniciar

```bash
docker-compose up -d
```

### 3️⃣ Verificar

```bash
# Ver que todo esté corriendo
docker-compose ps

# Ver logs
docker-compose logs -f

# Abrir en navegador
http://localhost:5000/api/health
```

---

## 📦 Qué Incluye

### Servicios Docker

1. **PostgreSQL** (puerto 5432)
   - Base de datos con schema completo
   - Usuarios de prueba: juan, maria, carlos
   - Datos persistentes en volumen

2. **Backend Flask** (puerto 5000)
   - API REST completa
   - Sistema de recomendaciones con grafos
   - Autenticación JWT

### Características

✅ **Persistencia de datos**: Volumen Docker para PostgreSQL
✅ **Health checks**: Verifica que la BD esté lista
✅ **Auto-restart**: Los servicios se reinician automáticamente
✅ **Networking**: Los contenedores se comunican entre sí
✅ **Variables de entorno**: Configuración flexible
✅ **Usuarios de prueba**: 3 usuarios listos para usar

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Contraseña de PostgreSQL
DB_PASSWORD=postgres123

# Claves de seguridad (¡CAMBIAR EN PRODUCCIÓN!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# Ambiente
FLASK_ENV=production
```

### Puertos

- **5000**: Backend Flask API
- **5432**: PostgreSQL (opcional, puede comentarse en producción)

---

## 📊 Cargar Datos del Dataset

### Si tienes los CSV (Book-Crossing)

```bash
# 1. Asegúrate de que los CSV estén en data/
ls data/
# Books.csv, Ratings.csv, Users.csv

# 2. Ejecutar migración
docker-compose exec backend python ../database/migrate_csv_to_db.py
```

### Si NO tienes los CSV

El sistema funcionará con las tablas vacías. Puedes:
- Registrar usuarios nuevos
- Calificar libros (cuando agregues algunos)
- Usar datos de prueba

---

## 🎯 Usuarios de Prueba

**Precreados en el sistema**:

| Usuario | Password | Email |
|---------|----------|-------|
| juan | password123 | juan@example.com |
| maria | password123 | maria@example.com |
| carlos | password123 | carlos@example.com |

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Detener y borrar datos (¡CUIDADO!)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Ver uso de recursos
docker stats

# Acceder a PostgreSQL
docker-compose exec postgres psql -U postgres -d readiego

# Ejecutar comandos en backend
docker-compose exec backend python -c "print('Hola')"
```

---

## 🔐 Producción

### Checklist

- [ ] Cambiar `DB_PASSWORD` a algo seguro
- [ ] Cambiar `SECRET_KEY` y `JWT_SECRET_KEY`
- [ ] Configurar `FLASK_ENV=production`
- [ ] Comentar puerto 5432 en docker-compose.yml (no exponer PostgreSQL)
- [ ] Configurar HTTPS (Nginx + Let's Encrypt)
- [ ] Configurar backups automáticos
- [ ] Limitar recursos de CPU/RAM si es necesario

### Generar Contraseñas Seguras

```bash
# Linux/Mac
openssl rand -base64 32

# Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## 🐛 Problemas Comunes

### "Port 5000 already in use"

```yaml
# En docker-compose.yml, cambiar:
ports:
  - "8080:5000"  # Usa otro puerto
```

### "Cannot connect to database"

```bash
# Verificar que PostgreSQL esté listo
docker-compose exec postgres pg_isready -U postgres

# Ver logs
docker-compose logs postgres
```

### Backend se reinicia constantemente

```bash
# Ver qué está pasando
docker-compose logs backend

# Reconstruir imagen
docker-compose build --no-cache backend
docker-compose up -d
```

---

## 📚 Documentación

- **[DEPLOY.md](DEPLOY.md)**: Guía rápida (5 minutos)
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)**: Guía completa (20 minutos)
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**: Cómo cargar datos
- **[CLAUDE.md](CLAUDE.md)**: Documentación del proyecto

---

## 🎉 ¡Listo para Deploy!

Tu sistema ahora:

✅ Corre en contenedores Docker
✅ Tiene PostgreSQL configurado
✅ Incluye usuarios de prueba
✅ Es fácil de desplegar en cualquier servidor
✅ Tiene persistencia de datos
✅ Se reinicia automáticamente

**Siguiente paso**: Despliega en un servidor (AWS, DigitalOcean, Heroku, etc.)
