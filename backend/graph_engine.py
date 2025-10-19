import networkx as nx
import pandas as pd
from typing import List, Dict, Set

class GraphEngine:
    def __init__(self):
        """Inicializa el grafo bipartito para usuarios y libros"""
        self.G = nx.Graph()
        self.users = set()
        self.books = set()
        
    def add_rating(self, user_id: str, book_id: str, rating: float):
        """Agrega una calificación (arista) entre usuario y libro"""
        # Agregar nodos si no existen
        if user_id not in self.users:
            self.G.add_node(user_id, bipartite=0, type='user')
            self.users.add(user_id)
            
        if book_id not in self.books:
            self.G.add_node(book_id, bipartite=1, type='book')
            self.books.add(book_id)
        
        # Agregar arista con peso (rating)
        self.G.add_edge(user_id, book_id, rating=rating)
    
    def load_from_dataframe(self, df: pd.DataFrame):
        """Carga datos desde un DataFrame con columnas: user_id, book_id, rating"""
        for _, row in df.iterrows():
            self.add_rating(
                str(row['user_id']),
                str(row['book_id']),
                float(row['rating'])
            )
        print(f"✅ Grafo cargado: {len(self.users)} usuarios, {len(self.books)} libros")
    
    def get_user_books(self, user_id: str) -> Dict[str, float]:
        """Obtiene todos los libros calificados por un usuario"""
        if user_id not in self.G:
            return {}
        
        books = {}
        for neighbor in self.G.neighbors(user_id):
            if neighbor in self.books:
                books[neighbor] = self.G[user_id][neighbor]['rating']
        return books
    
    def get_book_users(self, book_id: str) -> Dict[str, float]:
        """Obtiene todos los usuarios que calificaron un libro"""
        if book_id not in self.G:
            return {}
        
        users = {}
        for neighbor in self.G.neighbors(book_id):
            if neighbor in self.users:
                users[neighbor] = self.G[neighbor][book_id]['rating']
        return users
    
    def get_user_count(self) -> int:
        """Retorna el número de usuarios en el grafo"""
        return len(self.users)
    
    def get_book_count(self) -> int:
        """Retorna el número de libros en el grafo"""
        return len(self.books)
    
    def get_rating(self, user_id: str, book_id: str) -> float:
        """Obtiene la calificación de un usuario a un libro"""
        if self.G.has_edge(user_id, book_id):
            return self.G[user_id][book_id]['rating']
        return 0.0
    
    def get_graph_stats(self) -> Dict:
        """Retorna estadísticas del grafo"""
        return {
            'users': len(self.users),
            'books': len(self.books),
            'ratings': self.G.number_of_edges(),
            'density': nx.density(self.G)
        }