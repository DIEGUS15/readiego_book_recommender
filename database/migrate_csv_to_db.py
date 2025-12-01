"""
Script para migrar datos CSV a PostgreSQL
Ejecutar: python migrate_csv_to_db.py
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import sys
import os
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

def create_database_if_not_exists():
    """Crea la base de datos si no existe"""
    try:
        # Conectar a la base de datos postgres por defecto
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar si la base de datos existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
        exists = cursor.fetchone()

        if not exists:
            print(f"📦 Creando base de datos '{DB_CONFIG['dbname']}'...")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
            print(f"✅ Base de datos '{DB_CONFIG['dbname']}' creada")
        else:
            print(f"✅ Base de datos '{DB_CONFIG['dbname']}' ya existe")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        sys.exit(1)

def execute_schema():
    """Ejecuta el script SQL para crear las tablas"""
    try:
        schema_path = Path(__file__).parent / 'schema.sql'

        # Intentar diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(schema_path, 'r', encoding=encoding) as f:
                    schema_sql = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("No se pudo leer schema.sql con ningún encoding conocido")

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("🔨 Creando tablas...")
        cursor.execute(schema_sql)
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ Tablas creadas exitosamente")

    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
        sys.exit(1)

def migrate_books():
    """Migra los libros desde Books.csv"""
    print("\n📚 Migrando Books.csv...")

    try:
        # Leer CSV
        books_path = Path(__file__).parent.parent / 'data' / 'Books.csv'
        df = pd.read_csv(books_path, encoding='latin-1', on_bad_lines='skip')

        # Limpiar datos
        df.columns = ['ISBN', 'Title', 'Author', 'Year', 'Publisher', 'Image_S', 'Image_M', 'Image_L']
        df['Title'] = df['Title'].fillna('Unknown')
        df['Author'] = df['Author'].fillna('Unknown')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Preparar datos para inserción
        insert_query = """
            INSERT INTO books (isbn, title, author, year_of_publication, publisher,
                             image_url_s, image_url_m, image_url_l)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (isbn) DO NOTHING
        """

        # Convertir DataFrame a lista de tuplas
        data = []
        for _, row in df.iterrows():
            data.append((
                str(row['ISBN']),
                str(row['Title']),
                str(row['Author']),
                int(row['Year']) if pd.notna(row['Year']) else None,
                str(row['Publisher']) if pd.notna(row['Publisher']) else None,
                str(row['Image_S']) if pd.notna(row['Image_S']) else None,
                str(row['Image_M']) if pd.notna(row['Image_M']) else None,
                str(row['Image_L']) if pd.notna(row['Image_L']) else None
            ))

        # Insertar en lotes para mejor rendimiento
        print(f"   Insertando {len(data)} libros...")
        execute_batch(cursor, insert_query, data, page_size=1000)
        conn.commit()

        cursor.close()
        conn.close()

        print(f"✅ {len(data)} libros migrados exitosamente")

    except Exception as e:
        print(f"❌ Error al migrar libros: {e}")
        sys.exit(1)

def migrate_users():
    """Migra los usuarios desde Users.csv"""
    print("\n👥 Migrando Users.csv...")

    try:
        # Leer CSV
        users_path = Path(__file__).parent.parent / 'data' / 'Users.csv'
        df = pd.read_csv(users_path, encoding='latin-1', on_bad_lines='skip')

        # Limpiar datos
        df.columns = ['User_ID', 'Location', 'Age']
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Preparar datos para inserción
        insert_query = """
            INSERT INTO users (user_id, location, age)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """

        # Convertir DataFrame a lista de tuplas
        data = []
        for _, row in df.iterrows():
            data.append((
                int(row['User_ID']),
                str(row['Location']) if pd.notna(row['Location']) else None,
                int(row['Age']) if pd.notna(row['Age']) and row['Age'] > 0 else None
            ))

        # Insertar en lotes
        print(f"   Insertando {len(data)} usuarios...")
        execute_batch(cursor, insert_query, data, page_size=1000)
        conn.commit()

        cursor.close()
        conn.close()

        print(f"✅ {len(data)} usuarios migrados exitosamente")

    except Exception as e:
        print(f"❌ Error al migrar usuarios: {e}")
        sys.exit(1)

def migrate_ratings():
    """Migra las calificaciones desde Ratings.csv"""
    print("\n⭐ Migrando Ratings.csv...")

    try:
        # Conectar a la base de datos primero para obtener ISBNs y User IDs válidos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener todos los ISBNs válidos
        print("   Obteniendo ISBNs validos de la base de datos...")
        cursor.execute("SELECT isbn FROM books")
        valid_isbns = set(row[0] for row in cursor.fetchall())
        print(f"   {len(valid_isbns):,} ISBNs validos encontrados")

        # Obtener todos los User IDs válidos
        print("   Obteniendo User IDs validos de la base de datos...")
        cursor.execute("SELECT user_id FROM users")
        valid_users = set(row[0] for row in cursor.fetchall())
        print(f"   {len(valid_users):,} usuarios validos encontrados")

        # Leer CSV
        print("   Cargando Ratings.csv...")
        ratings_path = Path(__file__).parent.parent / 'data' / 'Ratings.csv'
        df = pd.read_csv(ratings_path, encoding='latin-1', on_bad_lines='skip')

        # Limpiar datos
        df.columns = ['User_ID', 'ISBN', 'Rating']

        print(f"   Total de calificaciones en CSV: {len(df):,}")

        # Filtrar solo ratings con ISBNs y User IDs válidos
        print("   Filtrando calificaciones validas...")
        df['ISBN'] = df['ISBN'].astype(str)
        df['User_ID'] = df['User_ID'].astype(int)

        df_valid = df[
            (df['ISBN'].isin(valid_isbns)) &
            (df['User_ID'].isin(valid_users))
        ]

        print(f"   Calificaciones validas a insertar: {len(df_valid):,}")
        print(f"   Calificaciones descartadas (ISBN/User invalido): {len(df) - len(df_valid):,}")

        # Preparar datos para inserción
        insert_query = """
            INSERT INTO ratings (user_id, isbn, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, isbn) DO NOTHING
        """

        # Procesar en lotes para mostrar progreso
        batch_size = 10000
        total_inserted = 0
        total_batches = (len(df_valid) + batch_size - 1) // batch_size

        print(f"   Insertando en {total_batches} lotes...")

        for i in range(0, len(df_valid), batch_size):
            batch = df_valid.iloc[i:i+batch_size]

            # Convertir batch a lista de tuplas
            data = []
            for _, row in batch.iterrows():
                try:
                    data.append((
                        int(row['User_ID']),
                        str(row['ISBN']),
                        int(row['Rating'])
                    ))
                except:
                    continue

            if data:
                execute_batch(cursor, insert_query, data, page_size=1000)
                conn.commit()
                total_inserted += len(data)

                batch_num = (i // batch_size) + 1
                progress = (total_inserted / len(df_valid)) * 100
                print(f"   Lote {batch_num}/{total_batches}: {total_inserted:,} / {len(df_valid):,} ({progress:.1f}%)")

        cursor.close()
        conn.close()

        print(f"✅ {total_inserted:,} calificaciones migradas exitosamente")

    except Exception as e:
        print(f"❌ Error al migrar calificaciones: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def verify_migration():
    """Verifica que la migración fue exitosa"""
    print("\n🔍 Verificando migración...")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM books")
        books_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ratings")
        ratings_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM explicit_ratings")
        explicit_ratings_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        print(f"\n📊 Estadísticas de la base de datos:")
        print(f"   📚 Libros: {books_count:,}")
        print(f"   👥 Usuarios: {users_count:,}")
        print(f"   ⭐ Calificaciones totales: {ratings_count:,}")
        print(f"   ⭐ Calificaciones explícitas (rating > 0): {explicit_ratings_count:,}")

    except Exception as e:
        print(f"❌ Error al verificar migración: {e}")

if __name__ == '__main__':
    # Configurar encoding en Windows
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("=" * 60)
    print("  READIEGO - Migracion CSV a PostgreSQL")
    print("=" * 60)

    print("\nConfiguracion de la base de datos:")
    print(f"   Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['dbname']}")
    print(f"   User: {DB_CONFIG['user']}")

    print("\nIMPORTANTE: Asegurate de que PostgreSQL este corriendo")
    print("y que las credenciales sean correctas\n")

    input("Presiona ENTER para continuar o Ctrl+C para cancelar...")

    # Paso 1: Crear base de datos
    create_database_if_not_exists()

    # Paso 2: Crear tablas
    execute_schema()

    # Paso 3: Migrar datos
    migrate_books()
    migrate_users()
    migrate_ratings()

    # Paso 4: Verificar
    verify_migration()

    print("\nMigracion completada exitosamente!")
    print("\nProximos pasos:")
    print("   1. El archivo .env ya tiene tus credenciales")
    print("   2. El codigo ya esta configurado para usar la base de datos")
