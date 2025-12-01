"""
Nuevos endpoints para el sistema de autenticación y gestión de libros
"""
from flask import jsonify, request
from auth import register_user, login_user, token_required, get_user_by_id
from database import DatabaseConnection
from data_loader import DataLoader

def register_auth_routes(app, data_loader_instance, recommender_instance, hybrid_recommender_instance, graph_engine_instance):
    """Registra todas las rutas de autenticación y gestión de usuarios"""

    # ==================== AUTENTICACIÓN ====================

    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """Registro de nuevos usuarios"""
        data = request.get_json()

        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')

        if not email or not username or not password:
            return jsonify({'error': 'Email, username y password son requeridos'}), 400

        success, message, user_id = register_user(email, username, password, full_name)

        if success:
            return jsonify({
                'message': message,
                'user_id': user_id
            }), 201
        else:
            return jsonify({'error': message}), 400

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """Login de usuarios"""
        data = request.get_json()

        email_or_username = data.get('email_or_username')
        password = data.get('password')

        if not email_or_username or not password:
            return jsonify({'error': 'Email/username y password son requeridos'}), 400

        success, message, token, user_info = login_user(email_or_username, password)

        if success:
            return jsonify({
                'message': message,
                'token': token,
                'user': user_info
            }), 200
        else:
            return jsonify({'error': message}), 401

    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def api_get_current_user(current_user):
        """Obtiene información del usuario autenticado"""
        user = get_user_by_id(current_user['user_id'])

        if user:
            return jsonify({'user': dict(user)}), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404

    # ==================== CATÁLOGO DE LIBROS ====================

    @app.route('/api/catalog/books', methods=['GET'])
    def api_get_catalog():
        """Obtiene el catálogo de libros con paginación y búsqueda"""
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        search = request.args.get('search', default='', type=str)

        try:
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor(dict_cursor=True)

            offset = (page - 1) * limit

            if search:
                # Búsqueda por título o autor
                cursor.execute("""
                    SELECT isbn, title, author, year_of_publication, publisher, image_url_m,
                           COUNT(*) OVER() as total_count
                    FROM books
                    WHERE title ILIKE %s OR author ILIKE %s
                    ORDER BY title
                    LIMIT %s OFFSET %s
                """, (f'%{search}%', f'%{search}%', limit, offset))
            else:
                # Sin búsqueda, obtener todos
                cursor.execute("""
                    SELECT isbn, title, author, year_of_publication, publisher, image_url_m,
                           COUNT(*) OVER() as total_count
                    FROM books
                    ORDER BY title
                    LIMIT %s OFFSET %s
                """, (limit, offset))

            books = cursor.fetchall()

            total_count = books[0]['total_count'] if books else 0
            total_pages = (total_count + limit - 1) // limit

            # Convertir a lista de diccionarios
            books_list = []
            for book in books:
                books_list.append({
                    'isbn': book['isbn'],
                    'title': book['title'],
                    'author': book['author'],
                    'year': book['year_of_publication'],
                    'publisher': book['publisher'],
                    'image_url': book['image_url_m']
                })

            cursor.close()
            db.close()

            return jsonify({
                'books': books_list,
                'page': page,
                'limit': limit,
                'total': total_count,
                'total_pages': total_pages
            }), 200

        except Exception as e:
            print(f"Error al obtener catálogo: {e}")
            return jsonify({'error': 'Error al obtener catálogo'}), 500

    # ==================== CALIFICACIONES DE USUARIOS ====================

    @app.route('/api/ratings/my-ratings', methods=['GET'])
    @token_required
    def api_get_my_ratings(current_user):
        """Obtiene las calificaciones del usuario autenticado"""
        try:
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor(dict_cursor=True)

            cursor.execute("""
                SELECT
                    r.isbn,
                    r.rating,
                    r.review,
                    r.created_at,
                    b.title,
                    b.author,
                    b.image_url_m,
                    b.year_of_publication
                FROM app_user_ratings r
                JOIN books b ON r.isbn = b.isbn
                WHERE r.app_user_id = %s
                ORDER BY r.created_at DESC
            """, (current_user['user_id'],))

            ratings = cursor.fetchall()

            ratings_list = []
            for rating in ratings:
                ratings_list.append({
                    'isbn': rating['isbn'],
                    'rating': rating['rating'],
                    'review': rating['review'],
                    'created_at': rating['created_at'].isoformat() if rating['created_at'] else None,
                    'book': {
                        'title': rating['title'],
                        'author': rating['author'],
                        'image_url': rating['image_url_m'],
                        'year': rating['year_of_publication']
                    }
                })

            cursor.close()
            db.close()

            return jsonify({'ratings': ratings_list}), 200

        except Exception as e:
            print(f"Error al obtener calificaciones: {e}")
            return jsonify({'error': 'Error al obtener calificaciones'}), 500

    @app.route('/api/ratings/rate', methods=['POST'])
    @token_required
    def api_rate_book(current_user):
        """Permite al usuario calificar un libro"""
        data = request.get_json()

        isbn = data.get('isbn')
        rating = data.get('rating')
        review = data.get('review', '')

        if not isbn or rating is None:
            return jsonify({'error': 'ISBN y rating son requeridos'}), 400

        if rating < 1 or rating > 10:
            return jsonify({'error': 'El rating debe estar entre 1 y 10'}), 400

        try:
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor(dict_cursor=True)

            # Verificar que el libro exista
            cursor.execute("SELECT isbn FROM books WHERE isbn = %s", (isbn,))
            if not cursor.fetchone():
                cursor.close()
                db.close()
                return jsonify({'error': 'Libro no encontrado'}), 404

            # Insertar o actualizar calificación
            cursor.execute("""
                INSERT INTO app_user_ratings (app_user_id, isbn, rating, review)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (app_user_id, isbn)
                DO UPDATE SET
                    rating = EXCLUDED.rating,
                    review = EXCLUDED.review,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (current_user['user_id'], isbn, rating, review))

            db.conn.commit()
            cursor.close()
            db.close()

            return jsonify({'message': 'Libro calificado exitosamente'}), 200

        except Exception as e:
            print(f"Error al calificar libro: {e}")
            return jsonify({'error': 'Error al calificar libro'}), 500

    @app.route('/api/ratings/delete/<isbn>', methods=['DELETE'])
    @token_required
    def api_delete_rating(current_user, isbn):
        """Elimina una calificación del usuario"""
        try:
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor()

            cursor.execute("""
                DELETE FROM app_user_ratings
                WHERE app_user_id = %s AND isbn = %s
            """, (current_user['user_id'], isbn))

            db.conn.commit()
            cursor.close()
            db.close()

            return jsonify({'message': 'Calificación eliminada'}), 200

        except Exception as e:
            print(f"Error al eliminar calificación: {e}")
            return jsonify({'error': 'Error al eliminar calificación'}), 500

    # ==================== RECOMENDACIONES PERSONALIZADAS ====================

    @app.route('/api/recommendations/for-me', methods=['GET'])
    @token_required
    def api_get_my_recommendations(current_user):
        """Obtiene recomendaciones personalizadas para el usuario autenticado usando el sistema híbrido"""
        if hybrid_recommender_instance is None:
            return jsonify({'error': 'Sistema de recomendaciones no inicializado'}), 500

        top_n = request.args.get('top_n', default=10, type=int)

        try:
            # Obtener calificaciones del usuario de la app
            db = DatabaseConnection()
            db.connect()
            cursor = db.get_cursor(dict_cursor=True)

            cursor.execute("""
                SELECT isbn, rating
                FROM app_user_ratings
                WHERE app_user_id = %s
            """, (current_user['user_id'],))

            user_ratings = cursor.fetchall()
            cursor.close()
            db.close()

            if len(user_ratings) == 0:
                return jsonify({
                    'message': 'No tienes calificaciones aún. Califica algunos libros para recibir recomendaciones.',
                    'recommendations': []
                }), 200

            # Crear un ID único para el usuario en el grafo
            user_graph_id = f"app_{current_user['user_id']}"

            # Sincronizar las calificaciones del usuario con el grafo
            # Primero, limpiar calificaciones antiguas del usuario si existen
            if user_graph_id in graph_engine_instance.users:
                # Obtener libros actuales en el grafo para este usuario
                current_books_in_graph = list(graph_engine_instance.get_user_books(user_graph_id).keys())
                # Remover todas las aristas del usuario
                for book_id in current_books_in_graph:
                    if graph_engine_instance.G.has_edge(user_graph_id, book_id):
                        graph_engine_instance.G.remove_edge(user_graph_id, book_id)

            # Agregar/actualizar todas las calificaciones actuales del usuario al grafo
            for rating_data in user_ratings:
                graph_engine_instance.add_rating(
                    user_graph_id,
                    rating_data['isbn'],
                    float(rating_data['rating'])
                )

            # Obtener recomendaciones usando el sistema híbrido mejorado
            recommendations = hybrid_recommender_instance.recommend_for_user(user_graph_id, top_n)

            return jsonify({
                'recommendations': recommendations,
                'based_on_ratings': len(user_ratings),
                'algorithm': 'hybrid_cosine_content'
            }), 200

        except Exception as e:
            print(f"Error al obtener recomendaciones: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Error al obtener recomendaciones'}), 500

    return app
