"""
Script para borrar y recrear la base de datos completamente
Ejecutar: python reset_and_migrate.py
"""
import psycopg2
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde backend/.env
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'readiego'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def drop_and_create_database():
    """Borra la base de datos si existe y la crea de nuevo"""
    try:
        # Configurar encoding en Windows
        if sys.platform == 'win32':
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

        print("=" * 60)
        print("  READIEGO - Reset y Migracion Completa")
        print("=" * 60)
        print("\nEsto borrara la base de datos 'readiego' si existe")
        print("y la creara de nuevo con todos los datos frescos.\n")

        respuesta = input("Estas seguro? (escribe 'si' para continuar): ")

        if respuesta.lower() != 'si':
            print("Operacion cancelada.")
            sys.exit(0)

        # Conectar a la base de datos postgres por defecto
        print("\nConectando a PostgreSQL...")
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Terminar conexiones activas a la base de datos readiego
        print("Cerrando conexiones activas a 'readiego'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{DB_CONFIG['dbname']}'
            AND pid <> pg_backend_pid();
        """)

        # Borrar la base de datos si existe
        print(f"Borrando base de datos '{DB_CONFIG['dbname']}' si existe...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['dbname']}")
        print(f"Base de datos '{DB_CONFIG['dbname']}' eliminada")

        # Crear la base de datos de nuevo
        print(f"Creando base de datos '{DB_CONFIG['dbname']}'...")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
        print(f"Base de datos '{DB_CONFIG['dbname']}' creada exitosamente")

        cursor.close()
        conn.close()

        print("\nListo! Ahora ejecutando migracion completa...\n")
        print("=" * 60)

        # Importar y ejecutar el script de migración
        import migrate_csv_to_db

        # Ejecutar las funciones de migración directamente
        migrate_csv_to_db.execute_schema()
        migrate_csv_to_db.migrate_books()
        migrate_csv_to_db.migrate_users()
        migrate_csv_to_db.migrate_ratings()
        migrate_csv_to_db.verify_migration()

        print("\n" + "=" * 60)
        print("  Reset y Migracion completados exitosamente!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    drop_and_create_database()
