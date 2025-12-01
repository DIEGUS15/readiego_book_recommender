# 🐳 Guía de Despliegue con Docker

Esta guía te ayudará a desplegar Readiego usando Docker y Docker Compose.

## 📋 Requisitos Previos

- Docker Desktop instalado ([Descargar aquí](https://www.docker.com/products/docker-desktop/))
- Docker Compose (viene incluido con Docker Desktop)

## 🚀 Inicio Rápido

### 1. Crear archivo `.env`

Copia el archivo de ejemplo y edítalo con tus configuraciones:

```bash
# En Windows (PowerShell)
cp backend\.env.example backend\.env

# En Linux/Mac
cp backend/.env.example backend/.env
```

Edita `backend/.env` y cambia las contraseñas:

```env
DB_PASSWORD=tu_contraseña_segura_aqui
SECRET_KEY=tu_secret_key_aqui
JWT_SECRET_KEY=tu_jwt_secret_aqui
```

### 2. Iniciar los Contenedores

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Ver los logs
docker-compose logs -f
```

Esto iniciará:
- ✅ PostgreSQL en puerto `5432`
- ✅ Backend Flask en puerto `5000`

### 3. Verificar que Funciona

Abre tu navegador en:
```
http://localhost:5000/api/health
```

Deberías ver las estadísticas del sistema.

## 📊 Cargar Datos Iniciales

### Opción 1: Migrar desde CSV (Primera vez)

Si tienes los archivos CSV del dataset Book-Crossing:

```bash
# 1. Copiar los CSVs a la carpeta data/
#    - Books.csv
#    - Ratings.csv
#    - Users.csv

# 2. Ejecutar el script de migración dentro del contenedor
docker-compose exec backend python /app/../database/migrate_csv_to_db.py
```

### Opción 2: Restaurar desde Backup

Si tienes un backup de PostgreSQL:

```bash
# Restaurar desde un archivo dump
docker-compose exec -T postgres pg_restore -U postgres -d readiego < backup.dump
```

## 🛠️ Comandos Útiles

### Ver Logs

```bash
# Logs de todos los servicios
docker-compose logs -f

# Solo logs del backend
docker-compose logs -f backend

# Solo logs de PostgreSQL
docker-compose logs -f postgres
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo el backend
docker-compose restart backend
```

### Detener y Borrar Todo

```bash
# Detener servicios
docker-compose down

# Detener Y borrar volúmenes (¡CUIDADO! Borra la BD)
docker-compose down -v
```

### Acceder a la Base de Datos

```bash
# Conectarse a PostgreSQL
docker-compose exec postgres psql -U postgres -d readiego

# Dentro de psql:
\dt              # Ver tablas
\d books         # Ver estructura de tabla 'books'
SELECT COUNT(*) FROM books;
\q               # Salir
```

### Ejecutar Comandos en el Backend

```bash
# Abrir una terminal en el contenedor del backend
docker-compose exec backend bash

# Ejecutar Python dentro del contenedor
docker-compose exec backend python -c "print('Hola desde Docker!')"
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Puedes crear un archivo `.env` en la raíz del proyecto para configurar Docker Compose:

```env
# .env (en la raíz, NO en backend/)
DB_PASSWORD=mi_password_super_segura
SECRET_KEY=mi_secret_key
JWT_SECRET_KEY=mi_jwt_secret
FLASK_ENV=production
```

### Usar Modo Desarrollo

Para desarrollo local con hot-reload:

```yaml
# Editar docker-compose.yml
services:
  backend:
    environment:
      FLASK_ENV: development
    volumes:
      - ./backend:/app  # Esto ya está configurado
```

Ahora cualquier cambio en el código se reflejará automáticamente.

### Cambiar Puerto del Backend

Si el puerto 5000 está ocupado:

```yaml
# En docker-compose.yml
services:
  backend:
    ports:
      - "8080:5000"  # Cambia 8080 al puerto que quieras
```

## 📦 Despliegue en Producción

### 1. Crear un Dockerfile para Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Servir con nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Agregar Frontend a docker-compose.yml

```yaml
services:
  # ... postgres y backend ...

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: readiego_frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - readiego_network
```

### 3. Configurar Nginx (frontend/nginx.conf)

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔐 Seguridad en Producción

### 1. Cambiar Contraseñas

```bash
# Generar contraseñas seguras
openssl rand -base64 32
```

Actualiza `.env`:
```env
DB_PASSWORD=<contraseña_generada_1>
SECRET_KEY=<contraseña_generada_2>
JWT_SECRET_KEY=<contraseña_generada_3>
```

### 2. No Exponer PostgreSQL

```yaml
# En docker-compose.yml
services:
  postgres:
    # ports:
    #   - "5432:5432"  # Comentar esta línea
```

PostgreSQL solo será accesible desde el backend, no desde fuera.

### 3. Usar HTTPS

Para producción, usa un reverse proxy con SSL (Nginx + Let's Encrypt).

## 🐛 Troubleshooting

### Error: "Cannot connect to database"

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Ver logs de PostgreSQL
docker-compose logs postgres

# Esperar a que PostgreSQL esté listo
docker-compose exec postgres pg_isready -U postgres
```

### Error: "Port already in use"

```bash
# Ver qué está usando el puerto 5000
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Cambiar el puerto en docker-compose.yml
```

### Error: "No space left on device"

```bash
# Limpiar imágenes y contenedores viejos
docker system prune -a

# Ver uso de espacio
docker system df
```

### Backend no se inicia

```bash
# Ver logs completos
docker-compose logs backend

# Reconstruir la imagen
docker-compose build --no-cache backend
docker-compose up -d backend
```

## 📊 Monitoreo

### Ver Uso de Recursos

```bash
# Recursos en tiempo real
docker stats

# Espacio usado
docker system df -v
```

### Backups de la Base de Datos

```bash
# Crear backup
docker-compose exec postgres pg_dump -U postgres readiego > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres -d readiego < backup_20250130.sql
```

## 🚀 Comandos Completos para Deploy

### Primera Vez

```bash
# 1. Clonar el repositorio
git clone <tu-repo>
cd readiego_book_recommender

# 2. Crear .env
cp backend/.env.example backend/.env
# Editar .env con tus contraseñas

# 3. Iniciar
docker-compose up -d

# 4. Verificar
docker-compose ps
docker-compose logs -f

# 5. Cargar datos (si es necesario)
docker-compose exec backend python ../database/migrate_csv_to_db.py
```

### Actualizar Código

```bash
# 1. Obtener últimos cambios
git pull

# 2. Reconstruir y reiniciar
docker-compose up -d --build

# 3. Verificar
docker-compose logs -f backend
```

## 📚 Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)

## ✅ Checklist de Producción

- [ ] Cambiar todas las contraseñas en `.env`
- [ ] Configurar `FLASK_ENV=production`
- [ ] No exponer puerto de PostgreSQL (5432)
- [ ] Configurar HTTPS con reverse proxy
- [ ] Configurar backups automáticos de la BD
- [ ] Configurar logs persistentes
- [ ] Monitorear recursos (CPU, RAM, Disco)
- [ ] Configurar restart policies (`restart: unless-stopped`)

---

¡Listo! Tu aplicación Readiego ahora corre en contenedores Docker 🐳
