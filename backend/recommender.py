from graph_engine import GraphEngine
from typing import List, Dict, Tuple
import numpy as np

class BookRecommender:
    def __init__(self, graph_engine: GraphEngine):
        """Inicializa el sistema recomendador"""
        self.graph = graph_engine
    
    def recommend_collaborative(self, user_id: str, top_n: int = 5) -> List[Dict]:
        """
        Recomendación por filtrado colaborativo:
        Encuentra usuarios similares y recomienda libros que ellos calificaron bien
        """
        if user_id not in self.graph.users:
            return []
        
        # 1. Obtener libros que el usuario ya calificó
        user_books = set(self.graph.get_user_books(user_id).keys())
        
        # 2. Encontrar usuarios similares
        similar_users = self._find_similar_users(user_id)
        
        # 3. Recolectar libros recomendados con puntajes
        recommendations = {}
        
        for similar_user, similarity in similar_users:
            similar_user_books = self.graph.get_user_books(similar_user)
            
            for book_id, rating in similar_user_books.items():
                # Solo recomendar libros que el usuario no ha leído
                if book_id not in user_books:
                    if book_id not in recommendations:
                        recommendations[book_id] = 0
                    # Puntaje ponderado por similitud del usuario
                    recommendations[book_id] += rating * similarity
        
        # 4. Ordenar y retornar top N
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return [
            {
                'book_id': book_id,
                'score': round(score, 2),
                'method': 'collaborative_filtering'
            }
            for book_id, score in sorted_recommendations
        ]
    
    def recommend_by_book(self, book_id: str, top_n: int = 5) -> List[Dict]:
        """
        Recomendación basada en similitud de libros:
        Encuentra libros similares según usuarios en común
        """
        if book_id not in self.graph.books:
            return []
        
        # Calcular similitud con todos los demás libros
        similarities = {}
        
        for other_book in self.graph.books:
            if other_book != book_id:
                similarity = self._calculate_book_similarity(book_id, other_book)
                if similarity > 0:
                    similarities[other_book] = similarity
        
        # Ordenar y retornar top N
        sorted_similar = sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return [
            {
                'book_id': book_id,
                'similarity': round(sim, 2),
                'method': 'item_similarity'
            }
            for book_id, sim in sorted_similar
        ]
    
    def _find_similar_users(self, user_id: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """Encuentra los usuarios más similares usando similitud de Jaccard"""
        user_books = set(self.graph.get_user_books(user_id).keys())
        
        similarities = {}
        
        for other_user in self.graph.users:
            if other_user != user_id:
                other_books = set(self.graph.get_user_books(other_user).keys())
                
                # Similitud de Jaccard
                intersection = len(user_books & other_books)
                union = len(user_books | other_books)
                
                if union > 0:
                    similarity = intersection / union
                    similarities[other_user] = similarity
        
        # Retornar top N usuarios más similares
        return sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
    
    def _calculate_book_similarity(self, book1: str, book2: str) -> float:
        """Calcula similitud entre dos libros basado en usuarios en común"""
        users_book1 = set(self.graph.get_book_users(book1).keys())
        users_book2 = set(self.graph.get_book_users(book2).keys())
        
        intersection = len(users_book1 & users_book2)
        union = len(users_book1 | users_book2)
        
        if union == 0:
            return 0.0
        
        # Similitud de Jaccard
        return intersection / union