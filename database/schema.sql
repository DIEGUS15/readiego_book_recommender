-- Readiego Book Recommender - Database Schema
-- PostgreSQL Database

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Books table
CREATE TABLE books (
    isbn VARCHAR(13) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(300),
    year_of_publication INTEGER,
    publisher VARCHAR(300),
    image_url_s VARCHAR(500),
    image_url_m VARCHAR(500),
    image_url_l VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    location VARCHAR(300),
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Ratings table
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 0 AND rating <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES books(isbn) ON DELETE CASCADE,
    UNIQUE(user_id, isbn)
);

-- Create indexes for better query performance
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_isbn ON ratings(isbn);
CREATE INDEX idx_ratings_rating ON ratings(rating);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);

-- Create a view for explicit ratings only (rating > 0)
CREATE VIEW explicit_ratings AS
SELECT
    r.id,
    r.user_id,
    r.isbn,
    r.rating,
    r.created_at
FROM ratings r
WHERE r.rating > 0;

-- Create App Users table (for registered users)
DROP TABLE IF EXISTS app_user_ratings CASCADE;
DROP TABLE IF EXISTS app_users CASCADE;

CREATE TABLE app_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create App User Ratings table
CREATE TABLE app_user_ratings (
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

-- Create indexes for app users
CREATE INDEX idx_app_users_email ON app_users(email);
CREATE INDEX idx_app_users_username ON app_users(username);
CREATE INDEX idx_app_user_ratings_user_id ON app_user_ratings(app_user_id);
CREATE INDEX idx_app_user_ratings_isbn ON app_user_ratings(isbn);

-- Insert test users (password: password123)
INSERT INTO app_users (email, username, password_hash, full_name) VALUES
('juan@example.com', 'juan', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.u0VHx1Ju', 'Juan Pérez'),
('maria@example.com', 'maria', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.u0VHx1Ju', 'María García'),
('carlos@example.com', 'carlos', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.u0VHx1Ju', 'Carlos López');

-- Comments for documentation
COMMENT ON TABLE books IS 'Book metadata from Book-Crossing dataset';
COMMENT ON TABLE users IS 'User information from Book-Crossing dataset';
COMMENT ON TABLE ratings IS 'User ratings for books (0-10 scale, 0 = implicit)';
COMMENT ON VIEW explicit_ratings IS 'Only explicit ratings (rating > 0) used for recommendations';
COMMENT ON TABLE app_users IS 'Registered application users (separate from Book-Crossing dataset)';
COMMENT ON TABLE app_user_ratings IS 'Ratings from registered app users (1-10 scale)';
