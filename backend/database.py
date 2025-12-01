import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConnection:
    """Clase para manejar conexiones a PostgreSQL"""

    def __init__(self):
        """Inicializa la configuración de la base de datos"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'readiego'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        self.conn = None

    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = psycopg2.connect(**self.config)
            return self.conn
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            raise

    def get_cursor(self, dict_cursor=True):
        """Obtiene un cursor para ejecutar queries"""
        if self.conn is None:
            self.connect()

        if dict_cursor:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        return self.conn.cursor()

    def close(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Permite usar with statement"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del with statement"""
        self.close()
