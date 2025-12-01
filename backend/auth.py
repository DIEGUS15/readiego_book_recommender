"""
Sistema de Autenticación para Readiego
Maneja registro, login y gestión de usuarios
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from database import DatabaseConnection
import os

# Secret key para JWT (debería estar en .env en producción)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

def hash_password(password):
    """Hashea una contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, email, username):
    """Genera un JWT token para el usuario"""
    payload = {
        'user_id': user_id,
        'email': email,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token válido por 7 días
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decodifica y valida un JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401

        # Decodificar token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401

        # Pasar información del usuario a la función
        return f(current_user=payload, *args, **kwargs)

    return decorated

def register_user(email, username, password, full_name=None):
    """
    Registra un nuevo usuario
    Returns: (success: bool, message: str, user_id: int or None)
    """
    try:
        db = DatabaseConnection()
        db.connect()
        cursor = db.get_cursor(dict_cursor=True)

        # Verificar que el email no exista
        cursor.execute("SELECT id FROM app_users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return False, "El email ya está registrado", None

        # Verificar que el username no exista
        cursor.execute("SELECT id FROM app_users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return False, "El nombre de usuario ya está en uso", None

        # Hash de la contraseña
        password_hash = hash_password(password)

        # Insertar usuario
        cursor.execute("""
            INSERT INTO app_users (email, username, password_hash, full_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, username, password_hash, full_name))

        user_id = cursor.fetchone()['id']
        db.conn.commit()

        cursor.close()
        db.close()

        return True, "Usuario registrado exitosamente", user_id

    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False, "Error al registrar usuario", None

def login_user(email_or_username, password):
    """
    Autentica un usuario
    Returns: (success: bool, message: str, token: str or None, user: dict or None)
    """
    try:
        db = DatabaseConnection()
        db.connect()
        cursor = db.get_cursor(dict_cursor=True)

        # Buscar usuario por email o username
        cursor.execute("""
            SELECT id, email, username, password_hash, full_name, is_active
            FROM app_users
            WHERE email = %s OR username = %s
        """, (email_or_username, email_or_username))

        user = cursor.fetchone()

        if not user:
            cursor.close()
            db.close()
            return False, "Usuario no encontrado", None, None

        if not user['is_active']:
            cursor.close()
            db.close()
            return False, "Usuario desactivado", None, None

        # Verificar contraseña
        if not verify_password(password, user['password_hash']):
            cursor.close()
            db.close()
            return False, "Contraseña incorrecta", None, None

        # Actualizar last_login
        cursor.execute("""
            UPDATE app_users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (user['id'],))
        db.conn.commit()

        # Generar token
        token = generate_token(user['id'], user['email'], user['username'])

        # Información del usuario (sin el hash de contraseña)
        user_info = {
            'id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'full_name': user['full_name']
        }

        cursor.close()
        db.close()

        return True, "Login exitoso", token, user_info

    except Exception as e:
        print(f"Error al hacer login: {e}")
        return False, "Error al hacer login", None, None

def get_user_by_id(user_id):
    """Obtiene información de un usuario por su ID"""
    try:
        db = DatabaseConnection()
        db.connect()
        cursor = db.get_cursor(dict_cursor=True)

        cursor.execute("""
            SELECT id, email, username, full_name, created_at, last_login
            FROM app_users
            WHERE id = %s AND is_active = TRUE
        """, (user_id,))

        user = cursor.fetchone()

        cursor.close()
        db.close()

        return user

    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None
