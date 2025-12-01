"""
Sistema de Recomendación Híbrido Mejorado
Combina filtrado colaborativo + contenido con similitud de coseno
"""
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict
from database import DatabaseConnection

class HybridRecommender:
    def __init__(self, graph_engine, data_loader):
        """Inicializa el sistema de recomendación híbrido"""
        self.graph = graph_engine
        self.data_loader = data_loader

    def recommend_for_user(self, user_id: str, top_n: int = 10) -> List[Dict]:
        """
        Genera recomendaciones híbridas para un usuario
        Combina:
        1. Filtrado colaborativo con similitud de coseno
        2. Filtrado basado en contenido (autores, años similares)
        3. Filtros de calidad (calificaciones altas)
        """
        # Obtener libros ya calificados por el usuario
        user_books = self.graph.get_user_books(user_id)

        if len(user_books) == 0:
            # Si no ha calificado nada, recomendar libros populares
            return self._get_popular_books(top_n)

        # 1. Obtener recomendaciones colaborativas (60% del peso)
        collab_scores = self._collaborative_filtering_cosine(user_id, user_books)

        # 2. Obtener recomendaciones basadas en contenido (40% del peso)
        content_scores = self._content_based_filtering(user_id, user_books)

        # 3. Combinar scores con pesos
        combined_scores = defaultdict(float)

        # Peso colaborativo: 60%
        for book_id, score in collab_scores.items():
            if book_id not in user_books:  # No recomendar libros ya calificados
                combined_scores[book_id] += score * 0.6

        # Peso contenido: 40%
        for book_id, score in content_scores.items():
            if book_id not in user_books:
                combined_scores[book_id] += score * 0.4

        # 4. Aplicar filtro de calidad (solo libros con calificación promedio > 6)
        filtered_scores = self._apply_quality_filter(combined_scores)

        # 5. Aplicar diversidad (no más de 2 libros del mismo autor)
        diverse_recommendations = self._apply_diversity(filtered_scores, user_books)

        # 6. Ordenar y retornar top N
        sorted_recommendations = sorted(
            diverse_recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        # 7. Enriquecer con información del libro
        return self._enrich_recommendations(sorted_recommendations)

    def _collaborative_filtering_cosine(self, user_id: str, user_books: Dict) -> Dict[str, float]:
        """
        Filtrado colaborativo usando similitud de coseno
        Considera las calificaciones numéricas, no solo coincidencias
        """
        # Crear vector de calificaciones del usuario
        user_vector = {}
        all_books = set()

        for book_id, rating in user_books.items():
            user_vector[book_id] = rating
            all_books.add(book_id)

        # Encontrar usuarios similares usando similitud de coseno
        similar_users = []

        for other_user in self.graph.users:
            if other_user == user_id:
                continue

            other_books = self.graph.get_user_books(other_user)

            # Calcular similitud de coseno
            similarity = self._cosine_similarity(user_vector, other_books)

            if similarity > 0.1:  # Umbral mínimo de similitud
                similar_users.append((other_user, similarity))
                # Agregar libros del otro usuario
                for book_id in other_books:
                    all_books.add(book_id)

        # Ordenar usuarios por similitud y tomar top 50
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:50]

        if not similar_users:
            return {}

        # Calcular scores de libros basados en usuarios similares
        book_scores = defaultdict(float)
        book_weights = defaultdict(float)

        for similar_user, similarity in similar_users:
            similar_user_books = self.graph.get_user_books(similar_user)

            for book_id, rating in similar_user_books.items():
                if book_id not in user_books:  # Solo libros no calificados
                    # Score ponderado por similitud del usuario y calificación
                    book_scores[book_id] += rating * similarity
                    book_weights[book_id] += similarity

        # Normalizar scores
        normalized_scores = {}
        for book_id, score in book_scores.items():
            if book_weights[book_id] > 0:
                normalized_scores[book_id] = score / book_weights[book_id]

        return normalized_scores

    def _cosine_similarity(self, vector_a: Dict, vector_b: Dict) -> float:
        """
        Calcula similitud de coseno entre dos vectores de calificaciones
        Más preciso que Jaccard porque considera las magnitudes
        """
        # Encontrar libros en común
        common_books = set(vector_a.keys()) & set(vector_b.keys())

        if not common_books:
            return 0.0

        # Calcular producto punto y magnitudes
        dot_product = sum(vector_a[book] * vector_b[book] for book in common_books)

        magnitude_a = np.sqrt(sum(vector_a[book]**2 for book in common_books))
        magnitude_b = np.sqrt(sum(vector_b[book]**2 for book in common_books))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def _content_based_filtering(self, user_id: str, user_books: Dict) -> Dict[str, float]:
        """
        Recomendaciones basadas en contenido
        Recomienda libros similares a los que le gustaron (rating >= 7)
        """
        # Obtener libros que le gustaron al usuario
        liked_books = {book_id: rating for book_id, rating in user_books.items() if rating >= 7}

        if not liked_books:
            return {}

        book_scores = defaultdict(float)

        # Para cada libro que le gustó
        for liked_book_id, user_rating in liked_books.items():
            # Encontrar libros similares por autor y características
            similar_books = self._find_similar_books_by_content(liked_book_id)

            for similar_book_id, similarity in similar_books:
                if similar_book_id not in user_books:
                    # Score basado en cuánto le gustó el libro original
                    book_scores[similar_book_id] += similarity * (user_rating / 10.0)

        return book_scores

    def _find_similar_books_by_content(self, book_id: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Encuentra libros similares basados en contenido (autor, año, etc.)
        """
        book_info = self.data_loader.get_book_info(book_id)

        if not book_info:
            return []

        try:
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor(dict_cursor=True)

            # Buscar libros del mismo autor o años cercanos
            cursor.execute("""
                SELECT isbn, author, year_of_publication
                FROM books
                WHERE isbn != %s
                AND (
                    author = %s
                    OR ABS(year_of_publication - %s) <= 3
                )
                LIMIT 50
            """, (book_id, book_info['author'], book_info['year'] or 2000))

            similar_books = cursor.fetchall()
            cursor.close()
            db.close()

            # Calcular similitud
            results = []
            for similar_book in similar_books:
                similarity = 0.0

                # Mismo autor: alta similitud
                if similar_book['author'] == book_info['author']:
                    similarity += 0.7

                # Año cercano: similitud moderada
                year_diff = abs((similar_book['year_of_publication'] or 2000) - (book_info['year'] or 2000))
                if year_diff <= 3:
                    similarity += 0.3 * (1 - year_diff / 3)

                if similarity > 0:
                    results.append((similar_book['isbn'], similarity))

            # Ordenar por similitud
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_n]

        except Exception as e:
            print(f"Error al buscar libros similares: {e}")
            return []

    def _apply_quality_filter(self, book_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Filtra libros por calidad (calificación promedio)
        Solo recomienda libros con buena calificación promedio
        """
        filtered_scores = {}

        for book_id, score in book_scores.items():
            # Obtener calificación promedio del libro
            book_ratings = self.graph.get_book_users(book_id)

            if len(book_ratings) >= 3:  # Al menos 3 calificaciones
                avg_rating = sum(book_ratings.values()) / len(book_ratings)

                # Solo recomendar si tiene calificación promedio >= 6
                if avg_rating >= 6.0:
                    filtered_scores[book_id] = score
            else:
                # Si tiene pocas calificaciones, darle una oportunidad con score reducido
                filtered_scores[book_id] = score * 0.5

        return filtered_scores

    def _apply_diversity(self, book_scores: Dict[str, float], user_books: Dict) -> Dict[str, float]:
        """
        Aplica diversidad para no recomendar muchos libros del mismo autor
        """
        # Contar libros por autor en las recomendaciones
        author_count = defaultdict(int)
        diverse_scores = {}

        # Ordenar por score
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)

        for book_id, score in sorted_books:
            book_info = self.data_loader.get_book_info(book_id)

            if book_info:
                author = book_info['author']

                # Máximo 2 libros por autor en las recomendaciones
                if author_count[author] < 2:
                    diverse_scores[book_id] = score
                    author_count[author] += 1

        return diverse_scores

    def _get_popular_books(self, top_n: int) -> List[Dict]:
        """
        Obtiene libros populares (bien calificados y con muchas calificaciones)
        Para usuarios nuevos sin calificaciones
        """
        book_scores = {}

        for book_id in self.graph.books:
            book_ratings = self.graph.get_book_users(book_id)

            if len(book_ratings) >= 10:  # Al menos 10 calificaciones
                avg_rating = sum(book_ratings.values()) / len(book_ratings)
                popularity = len(book_ratings)

                # Score combinado: calidad + popularidad
                score = (avg_rating / 10.0) * 0.7 + (min(popularity, 100) / 100.0) * 0.3
                book_scores[book_id] = score

        # Ordenar y tomar top N
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        return self._enrich_recommendations(sorted_books)

    def _enrich_recommendations(self, recommendations: List[Tuple[str, float]]) -> List[Dict]:
        """
        Enriquece las recomendaciones con información del libro
        """
        enriched = []

        for book_id, score in recommendations:
            book_info = self.data_loader.get_book_info(book_id)

            if book_info:
                enriched.append({
                    'isbn': book_id,
                    'score': round(score, 3),
                    'book': book_info
                })

        return enriched
