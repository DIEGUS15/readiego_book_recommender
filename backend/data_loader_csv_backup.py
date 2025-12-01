import pandas as pd
import os
from pathlib import Path

class DataLoader:
    def __init__(self, data_dir='../data'):
        """Inicializa el cargador de datos"""
        self.data_dir = Path(data_dir)
        self.books_df = None
        self.ratings_df = None
        self.users_df = None
        
    def load_all(self, sample_size=None):
        """
        Carga todos los datasets
        sample_size: Si se especifica, carga solo una muestra (útil para pruebas)
        """
        print("📚 Cargando Books.csv...")
        self.books_df = self._load_books()
        
        print("⭐ Cargando Ratings.csv...")
        self.ratings_df = self._load_ratings(sample_size)
        
        print("👥 Cargando Users.csv...")
        self.users_df = self._load_users()
        
        print(f"✅ Datos cargados:")
        print(f"   - {len(self.books_df)} libros")
        print(f"   - {len(self.ratings_df)} calificaciones")
        print(f"   - {len(self.users_df)} usuarios")
        
        return self.books_df, self.ratings_df, self.users_df
    
    def _load_books(self):
        """Carga el archivo Books.csv"""
        books_path = self.data_dir / 'Books.csv'
        
        # Usar encoding='latin-1' porque el dataset tiene caracteres especiales
        df = pd.read_csv(books_path, encoding='latin-1', on_bad_lines='skip')
        
        # Renombrar columnas para que sean más fáciles de usar
        df.columns = ['ISBN', 'Title', 'Author', 'Year', 'Publisher', 
                      'Image_S', 'Image_M', 'Image_L']
        
        # Limpiar datos
        df['Title'] = df['Title'].fillna('Unknown')
        df['Author'] = df['Author'].fillna('Unknown')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        return df
    
    def _load_ratings(self, sample_size=None):
        """Carga el archivo Ratings.csv"""
        ratings_path = self.data_dir / 'Ratings.csv'
        
        df = pd.read_csv(ratings_path, encoding='latin-1', on_bad_lines='skip')
        df.columns = ['User_ID', 'ISBN', 'Rating']
        
        # Filtrar solo calificaciones explícitas (mayores a 0)
        # Las calificaciones de 0 son implícitas (no indican preferencia)
        df = df[df['Rating'] > 0]
        
        # Si se especifica sample_size, tomar una muestra
        if sample_size:
            print(f"⚠️  Usando muestra de {sample_size} calificaciones para pruebas")
            df = df.sample(n=min(sample_size, len(df)), random_state=42)
        
        return df
    
    def _load_users(self):
        """Carga el archivo Users.csv"""
        users_path = self.data_dir / 'Users.csv'
        
        df = pd.read_csv(users_path, encoding='latin-1', on_bad_lines='skip')
        df.columns = ['User_ID', 'Location', 'Age']
        
        # Limpiar edad (algunos valores son inválidos)
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        df['Age'] = df['Age'].fillna(0)
        
        return df
    
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
        """Obtiene información de un libro por su ISBN"""
        if self.books_df is None:
            return None
        
        book = self.books_df[self.books_df['ISBN'] == isbn]
        if len(book) == 0:
            return None
        
        book = book.iloc[0]
        return {
            'isbn': book['ISBN'],
            'title': book['Title'],
            'author': book['Author'],
            'year': int(book['Year']) if pd.notna(book['Year']) else None,
            'publisher': book['Publisher'],
            'image_url': book['Image_M']
        }
    
    def get_user_info(self, user_id):
        """Obtiene información de un usuario por su ID"""
        if self.users_df is None:
            return None
        
        user = self.users_df[self.users_df['User_ID'] == int(user_id)]
        if len(user) == 0:
            return None
        
        user = user.iloc[0]
        return {
            'user_id': str(user['User_ID']),
            'location': user['Location'],
            'age': int(user['Age']) if user['Age'] > 0 else None
        }