from flask import Flask, jsonify, request
from flask_cors import CORS
from graph_engine import GraphEngine
from recommender import BookRecommender
from hybrid_recommender import HybridRecommender
from data_loader import DataLoader
from app_routes import register_auth_routes
import sys
import os

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Secret key para sesiones
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Variables globales
graph_engine = None
recommender = None
hybrid_recommender = None
data_loader = None

def initialize_system(use_sample=True, sample_size=10000):
    """
    Inicializa el sistema cargando los datos desde PostgreSQL
    use_sample: Si True, usa solo una muestra de datos (recomendado para desarrollo)
    sample_size: Tamaño de la muestra
    """
    global graph_engine, recommender, hybrid_recommender, data_loader

    print("🚀 Iniciando sistema de recomendación...")
    print("📊 Cargando datos desde PostgreSQL...")

    # Cargar datos desde base de datos (no necesita ruta)
    data_loader = DataLoader()

    try:
        if use_sample:
            books_df, ratings_df, users_df = data_loader.load_all(sample_size=sample_size)
        else:
            books_df, ratings_df, users_df = data_loader.load_all()
    except Exception as e:
        print(f"❌ Error: No se pudo conectar a la base de datos PostgreSQL")
        print(f"   Detalles: {e}")
        print(f"   Asegúrate de que PostgreSQL esté corriendo y que las credenciales en .env sean correctas")
        sys.exit(1)

    # Crear grafo
    graph_engine = GraphEngine()
    processed_ratings = data_loader.get_processed_ratings()
    graph_engine.load_from_dataframe(processed_ratings)

    # Crear recomendadores
    recommender = BookRecommender(graph_engine)
    hybrid_recommender = HybridRecommender(graph_engine, data_loader)

    print("✅ Sistema listo!")
    print("   🎯 Recomendador híbrido habilitado")
    return True

@app.route('/')
def home():
    return jsonify({
        'message': 'API de Recomendador de Libros - Readiego',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'recommend_user': '/api/recommend/user/<user_id>',
            'recommend_book': '/api/recommend/book/<isbn>',
            'book_info': '/api/book/<isbn>',
            'user_info': '/api/user/<user_id>',
            'user_books': '/api/user/<user_id>/books'
        }
    })

@app.route('/api/health')
def health():
    if graph_engine is None:
        return jsonify({'status': 'error', 'message': 'Sistema no inicializado'}), 500
    
    stats = graph_engine.get_graph_stats()
    return jsonify({
        'status': 'ok',
        'stats': stats
    })

@app.route('/api/recommend/user/<user_id>')
def recommend_for_user(user_id):
    if recommender is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    top_n = request.args.get('top_n', default=10, type=int)
    recommendations = recommender.recommend_collaborative(user_id, top_n)
    
    # Enriquecer con información de los libros
    enriched_recommendations = []
    for rec in recommendations:
        book_info = data_loader.get_book_info(rec['book_id'])
        if book_info:
            rec['book_info'] = book_info
        enriched_recommendations.append(rec)
    
    return jsonify({
        'user_id': user_id,
        'recommendations': enriched_recommendations
    })

@app.route('/api/recommend/book/<isbn>')
def recommend_similar_books(isbn):
    if recommender is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    top_n = request.args.get('top_n', default=10, type=int)
    recommendations = recommender.recommend_by_book(isbn, top_n)
    
    # Enriquecer con información de los libros
    enriched_recommendations = []
    for rec in recommendations:
        book_info = data_loader.get_book_info(rec['book_id'])
        if book_info:
            rec['book_info'] = book_info
        enriched_recommendations.append(rec)
    
    # Obtener info del libro base
    base_book = data_loader.get_book_info(isbn)
    
    return jsonify({
        'base_book': base_book,
        'similar_books': enriched_recommendations
    })

@app.route('/api/book/<isbn>')
def get_book_info(isbn):
    if data_loader is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    book_info = data_loader.get_book_info(isbn)
    if book_info is None:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    return jsonify(book_info)

@app.route('/api/user/<user_id>')
def get_user_info(user_id):
    if data_loader is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    user_info = data_loader.get_user_info(user_id)
    if user_info is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(user_info)

@app.route('/api/user/<user_id>/books')
def get_user_books(user_id):
    if graph_engine is None or data_loader is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    user_books = graph_engine.get_user_books(user_id)
    
    # Enriquecer con información de los libros
    enriched_books = []
    for isbn, rating in user_books.items():
        book_info = data_loader.get_book_info(isbn)
        if book_info:
            book_info['user_rating'] = rating
            enriched_books.append(book_info)
    
    # Ordenar por calificación
    enriched_books.sort(key=lambda x: x['user_rating'], reverse=True)
    
    return jsonify({
        'user_id': user_id,
        'books': enriched_books,
        'total': len(enriched_books)
    })

@app.route('/api/debug/sample-users')
def get_sample_users():
    """Endpoint de debug para obtener usuarios de ejemplo"""
    if graph_engine is None:
        return jsonify({'error': 'Sistema no inicializado'}), 500
    
    # Obtener 20 usuarios aleatorios que tengan al menos 3 libros calificados
    sample_users = []
    for user_id in list(graph_engine.users)[:100]:  # Revisar primeros 100
        user_books = graph_engine.get_user_books(user_id)
        if len(user_books) >= 3:
            sample_users.append({
                'user_id': user_id,
                'books_count': len(user_books)
            })
        if len(sample_users) >= 20:
            break
    
    return jsonify({
        'sample_users': sample_users,
        'total_users_in_graph': len(graph_engine.users)
    })

if __name__ == '__main__':
    # Inicializar con muestra de 10,000 calificaciones para desarrollo
    # Cambia a use_sample=False para usar todos los datos
    initialize_system(use_sample=True, sample_size=10000)

    # Registrar las nuevas rutas de autenticación y gestión
    register_auth_routes(app, data_loader, recommender, hybrid_recommender, graph_engine)

    print("\n📚 Endpoints disponibles:")
    print("\n  🔐 Autenticación:")
    print("  - POST /api/auth/register")
    print("  - POST /api/auth/login")
    print("  - GET  /api/auth/me")
    print("\n  📖 Catálogo:")
    print("  - GET  /api/catalog/books")
    print("\n  ⭐ Calificaciones:")
    print("  - GET  /api/ratings/my-ratings")
    print("  - POST /api/ratings/rate")
    print("  - DELETE /api/ratings/delete/<isbn>")
    print("\n  🎯 Recomendaciones:")
    print("  - GET  /api/recommendations/for-me")
    print("\n  📊 Sistema (legacy):")
    print("  - GET  /api/health")
    print("  - GET  /api/recommend/user/<user_id>")
    print("  - GET  /api/recommend/book/<isbn>")
    print("  - GET  /api/book/<isbn>")
    print("\n🌐 Servidor: http://localhost:5000")
    print("👤 Usuarios de prueba: juan, maria, carlos (password: password123)\n")

    app.run(debug=True, host='0.0.0.0', port=5000)