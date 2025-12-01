import { useState, useEffect } from "react";
import axios from "axios";
import RatingStars from "../components/RatingStars";

export default function MyRatings() {
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRatings();
  }, []);

  const loadRatings = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/api/ratings/my-ratings"
      );
      setRatings(response.data.ratings);
    } catch (error) {
      console.error("Error al cargar calificaciones:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (isbn) => {
    if (confirm("¿Eliminar esta calificación?")) {
      try {
        await axios.delete(`http://localhost:5000/api/ratings/delete/${isbn}`);
        loadRatings();
      } catch (error) {
        alert("Error al eliminar calificación");
      }
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Mis Calificaciones</h1>

      {ratings.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No has calificado ningún libro aún.</p>
          <a
            href="/catalog"
            className="mt-4 inline-block px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Ir al Catálogo
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {ratings.map((rating) => (
            <div
              key={rating.isbn}
              className="flex gap-4 bg-white p-4 rounded-lg shadow"
            >
              <img
                src={rating.book.image_url}
                alt={rating.book.title}
                className="w-24 h-32 object-cover rounded"
                onError={(e) => {
                  e.target.src = "https://via.placeholder.com/96x128?text=No+Image";
                }}
              />
              <div className="flex-1">
                <h3 className="font-bold text-lg">{rating.book.title}</h3>
                <p className="text-sm text-gray-600">{rating.book.author}</p>
                <div className="mt-2">
                  <RatingStars rating={rating.rating} readonly />
                </div>
                {rating.review && (
                  <p className="mt-2 text-sm text-gray-700">{rating.review}</p>
                )}
                <button
                  onClick={() => handleDelete(rating.isbn)}
                  className="mt-3 text-sm text-red-600 hover:text-red-800"
                >
                  Eliminar calificación
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
