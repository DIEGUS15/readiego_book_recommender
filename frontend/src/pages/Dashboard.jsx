import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import BookCard from "../components/BookCard";

export default function Dashboard() {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [basedOnRatings, setBasedOnRatings] = useState(0);
  const [algorithm, setAlgorithm] = useState("");

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        "http://localhost:5000/api/recommendations/for-me"
      );
      setRecommendations(response.data.recommendations || []);
      setBasedOnRatings(response.data.based_on_ratings || 0);
      setAlgorithm(response.data.algorithm || "");
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || "Error al cargar recomendaciones");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Bienvenido, {user?.full_name || user?.username}!
          </h1>
          <p className="mt-2 text-gray-600">
            Aquí están tus recomendaciones personalizadas
          </p>
          {basedOnRatings > 0 && (
            <p className="mt-1 text-sm text-indigo-600">
              📊 Basado en {basedOnRatings} calificaciones · {algorithm === 'hybrid_cosine_content' ? '🎯 Algoritmo Híbrido Avanzado' : ''}
            </p>
          )}
        </div>
        <button
          onClick={loadRecommendations}
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <span>🔄</span>
          <span>Actualizar</span>
        </button>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Cargando recomendaciones...</p>
        </div>
      )}

      {error && (
        <div className="bg-yellow-50 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          {error}
          <p className="mt-2 text-sm">
            Califica algunos libros en el{" "}
            <a href="/catalog" className="underline">
              catálogo
            </a>{" "}
            para recibir recomendaciones personalizadas.
          </p>
        </div>
      )}

      {!loading && !error && recommendations.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-4">
            📖 Recomendados para ti
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {recommendations.map((rec) => (
              <BookCard key={rec.isbn} book={rec.book} showRating={false} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
