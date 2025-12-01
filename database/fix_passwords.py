"""
Script para actualizar las contraseñas de los usuarios de prueba
"""
import bcrypt
import psycopg2
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'readiego'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def hash_password(password):
    """Hashea una contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def update_passwords():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Nueva contraseña
        new_password = "password123"
        password_hash = hash_password(new_password)

        # Actualizar usuarios de prueba
        usuarios = ['juan', 'maria', 'carlos']

        for username in usuarios:
            cursor.execute("""
                UPDATE app_users
                SET password_hash = %s
                WHERE username = %s
            """, (password_hash, username))

        conn.commit()
        print(f"✅ Contraseñas actualizadas para: {', '.join(usuarios)}")
        print(f"   Nueva contraseña: {new_password}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_passwords()
