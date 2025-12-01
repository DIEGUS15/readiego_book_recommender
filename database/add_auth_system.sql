-- Sistema de Autenticación y Usuarios de la Aplicación
-- Ejecutar: psql -U postgres -d readiego -f add_auth_system.sql

-- Tabla de usuarios de la aplicación (diferente de 'users' del dataset)
CREATE TABLE IF NOT EXISTS app_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de calificaciones de usuarios de la app
CREATE TABLE IF NOT EXISTS app_user_ratings (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES books(isbn) ON DELETE CASCADE,
    UNIQUE(app_user_id, isbn)
);

-- Tabla para guardar listas de favoritos (opcional)
CREATE TABLE IF NOT EXISTS app_user_favorites (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES books(isbn) ON DELETE CASCADE,
    UNIQUE(app_user_id, isbn)
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_app_users_email ON app_users(email);
CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users(username);
CREATE INDEX IF NOT EXISTS idx_app_user_ratings_user ON app_user_ratings(app_user_id);
CREATE INDEX IF NOT EXISTS idx_app_user_ratings_isbn ON app_user_ratings(isbn);
CREATE INDEX IF NOT EXISTS idx_app_user_favorites_user ON app_user_favorites(app_user_id);

-- Vista combinada de ratings (del dataset + de la app)
CREATE OR REPLACE VIEW all_ratings AS
SELECT
    'dataset' as source,
    user_id::text as user_identifier,
    isbn,
    rating,
    created_at
FROM ratings
WHERE rating > 0
UNION ALL
SELECT
    'app' as source,
    'app_' || app_user_id::text as user_identifier,
    isbn,
    rating,
    created_at
FROM app_user_ratings;

-- Insertar 3 usuarios de ejemplo para testing
-- Contraseña para todos: "password123" (hash bcrypt)
INSERT INTO app_users (email, username, password_hash, full_name) VALUES
    ('juan@example.com', 'juan', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOe4Bq', 'Juan Pérez'),
    ('maria@example.com', 'maria', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOe4Bq', 'María García'),
    ('carlos@example.com', 'carlos', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOe4Bq', 'Carlos López')
ON CONFLICT (email) DO NOTHING;

-- Agregar algunas calificaciones de ejemplo para juan
-- (usa ISBNs que sabemos que existen en la BD)
INSERT INTO app_user_ratings (app_user_id, isbn, rating, review)
SELECT
    1,
    isbn,
    8,
    'Gran libro, muy recomendado!'
FROM books
WHERE isbn IN ('0195153448', '0002005018', '0060973129')
ON CONFLICT (app_user_id, isbn) DO NOTHING;

-- Comentarios
COMMENT ON TABLE app_users IS 'Usuarios registrados en la aplicación web';
COMMENT ON TABLE app_user_ratings IS 'Calificaciones de libros por usuarios de la app';
COMMENT ON TABLE app_user_favorites IS 'Lista de libros favoritos de usuarios';
COMMENT ON VIEW all_ratings IS 'Combinación de ratings del dataset y de la app para recomendaciones';

-- Mostrar resultado
SELECT 'Sistema de autenticacion creado exitosamente' as mensaje;
SELECT 'Usuarios de prueba creados (password: password123):' as info;
SELECT id, email, username, full_name FROM app_users;
