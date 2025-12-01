import pandas as pd
import os
from pathlib import Path
from database import DatabaseConnection

class DataLoader:
    def __init__(self):
        """Inicializa el cargador de datos desde PostgreSQL"""
        self.db = DatabaseConnection()
        self.books_df = None
        self.ratings_df = None
        self.users_df = None

    def load_all(self, sample_size=None):
        """
        Carga todos los datasets desde la base de datos
        sample_size: Si se especifica, carga solo una muestra (útil para pruebas)
        """
        print("📚 Cargando Books desde base de datos...")
        self.books_df = self._load_books()

        print("⭐ Cargando Ratings desde base de datos...")
        self.ratings_df = self._load_ratings(sample_size)

        print("👥 Cargando Users desde base de datos...")
        self.users_df = self._load_users()

        print(f"✅ Datos cargados:")
        print(f"   - {len(self.books_df)} libros")
        print(f"   - {len(self.ratings_df)} calificaciones")
        print(f"   - {len(self.users_df)} usuarios")

        return self.books_df, self.ratings_df, self.users_df

    def _load_books(self):
        """Carga los libros desde la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=False)

                query = """
                    SELECT isbn, title, author, year_of_publication,
                           publisher, image_url_s, image_url_m, image_url_l
                    FROM books
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                # Convertir a DataFrame
                df = pd.DataFrame(rows, columns=[
                    'ISBN', 'Title', 'Author', 'Year',
                    'Publisher', 'Image_S', 'Image_M', 'Image_L'
                ])

                # Limpiar datos
                df['Title'] = df['Title'].fillna('Unknown')
                df['Author'] = df['Author'].fillna('Unknown')

                cursor.close()

                return df

        except Exception as e:
            print(f"❌ Error al cargar libros: {e}")
            raise

    def _load_ratings(self, sample_size=None):
        """Carga las calificaciones desde la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=False)

                # Usar la vista de calificaciones explícitas (rating > 0)
                if sample_size:
                    query = """
                        SELECT user_id, isbn, rating
                        FROM explicit_ratings
                        ORDER BY RANDOM()
                        LIMIT %s
                    """
                    print(f"⚠️  Usando muestra de {sample_size} calificaciones para pruebas")
                    cursor.execute(query, (sample_size,))
                else:
                    query = """
                        SELECT user_id, isbn, rating
                        FROM explicit_ratings
                    """
                    cursor.execute(query)

                rows = cursor.fetchall()

                # Convertir a DataFrame
                df = pd.DataFrame(rows, columns=['User_ID', 'ISBN', 'Rating'])

                cursor.close()

                return df

        except Exception as e:
            print(f"❌ Error al cargar calificaciones: {e}")
            raise

    def _load_users(self):
        """Carga los usuarios desde la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=False)

                query = """
                    SELECT user_id, location, age
                    FROM users
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                # Convertir a DataFrame
                df = pd.DataFrame(rows, columns=['User_ID', 'Location', 'Age'])

                # Limpiar edad
                df['Age'] = df['Age'].fillna(0)

                cursor.close()

                return df

        except Exception as e:
            print(f"❌ Error al cargar usuarios: {e}")
            raise

    def get_processed_ratings(self):
        """
        Retorna ratings procesados listos para el grafo
        Formato: DataFrame con columnas [user_id, book_id, rating]
        """
        if self.ratings_df is None:
            raise ValueError("Debes llamar a load_all() primero")

        processed = self.ratings_df.copy()
        processed.columns = ['user_id', 'book_id', 'rating']

        # Convertir a strings para evitar problemas de tipos
        processed['user_id'] = processed['user_id'].astype(str)
        processed['book_id'] = processed['book_id'].astype(str)

        return processed

    def get_book_info(self, isbn):
        """Obtiene información de un libro por su ISBN desde la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=True)

                query = """
                    SELECT isbn, title, author, year_of_publication,
                           publisher, image_url_m
                    FROM books
                    WHERE isbn = %s
                """

                cursor.execute(query, (isbn,))
                book = cursor.fetchone()

                cursor.close()

                if book is None:
                    return None

                return {
                    'isbn': book['isbn'],
                    'title': book['title'],
                    'author': book['author'],
                    'year': book['year_of_publication'],
                    'publisher': book['publisher'],
                    'image_url': book['image_url_m']
                }

        except Exception as e:
            print(f"❌ Error al obtener libro {isbn}: {e}")
            return None

    def get_user_info(self, user_id):
        """Obtiene información de un usuario por su ID desde la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=True)

                query = """
                    SELECT user_id, location, age
                    FROM users
                    WHERE user_id = %s
                """

                cursor.execute(query, (int(user_id),))
                user = cursor.fetchone()

                cursor.close()

                if user is None:
                    return None

                return {
                    'user_id': str(user['user_id']),
                    'location': user['location'],
                    'age': user['age']
                }

        except Exception as e:
            print(f"❌ Error al obtener usuario {user_id}: {e}")
            return None

    def get_stats(self):
        """Obtiene estadísticas de la base de datos"""
        try:
            with self.db as db:
                cursor = db.get_cursor(dict_cursor=True)

                query = """
                    SELECT
                        (SELECT COUNT(*) FROM books) as total_books,
                        (SELECT COUNT(*) FROM users) as total_users,
                        (SELECT COUNT(*) FROM ratings) as total_ratings,
                        (SELECT COUNT(*) FROM explicit_ratings) as explicit_ratings
                """

                cursor.execute(query)
                stats = cursor.fetchone()

                cursor.close()

                return {
                    'books': stats['total_books'],
                    'users': stats['total_users'],
                    'ratings': stats['total_ratings'],
                    'explicit_ratings': stats['explicit_ratings']
                }

        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return None
