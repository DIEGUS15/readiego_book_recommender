import { useState, useEffect } from "react";
import axios from "axios";
import RatingStars from "../components/RatingStars";

export default function Catalog() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [ratedBooks, setRatedBooks] = useState(new Set());

  useEffect(() => {
    loadBooks();
  }, [page, search]);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:5000/api/catalog/books?page=${page}&limit=20&search=${search}`
      );
      setBooks(response.data.books);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error("Error al cargar catálogo:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (isbn, rating) => {
    try {
      await axios.post("http://localhost:5000/api/ratings/rate", {
        isbn,
        rating,
      });

      // Marcar libro como calificado
      setRatedBooks(prev => new Set([...prev, isbn]));

      // Mostrar notificación de éxito
      const successMsg = document.createElement('div');
      successMsg.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
      successMsg.textContent = '✓ Libro calificado! Tus recomendaciones se actualizarán';
      document.body.appendChild(successMsg);
      setTimeout(() => successMsg.remove(), 3000);

    } catch (error) {
      console.error("Error al calificar libro:", error);
      const errorMsg = document.createElement('div');
      errorMsg.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      errorMsg.textContent = '✗ Error al calificar libro';
      document.body.appendChild(errorMsg);
      setTimeout(() => errorMsg.remove(), 3000);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadBooks();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Catálogo de Libros</h1>

      <form onSubmit={handleSearchSubmit} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por título o autor..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Buscar
          </button>
        </div>
      </form>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {books.map((book) => (
              <div
                key={book.isbn}
                className={`flex gap-4 bg-white p-4 rounded-lg shadow hover:shadow-lg transition-shadow ${
                  ratedBooks.has(book.isbn) ? 'border-2 border-green-400' : ''
                }`}
              >
                <img
                  src={book.image_url || "/placeholder.png"}
                  alt={book.title}
                  className="w-24 h-32 object-cover rounded"
                  onError={(e) => {
                    e.target.src = "https://via.placeholder.com/96x128?text=No+Image";
                  }}
                />
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <h3 className="font-bold text-lg line-clamp-2 flex-1">{book.title}</h3>
                    {ratedBooks.has(book.isbn) && (
                      <span className="ml-2 text-green-600 text-xl">✓</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{book.author}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {book.year} - {book.publisher}
                  </p>
                  <div className="mt-3">
                    <p className="text-sm font-medium mb-1">
                      {ratedBooks.has(book.isbn) ? 'Calificado! Puedes cambiarlo:' : 'Calificar:'}
                    </p>
                    <RatingStars
                      rating={0}
                      onRate={(rating) => handleRate(book.isbn, rating)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex justify-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Anterior
            </button>
            <span className="px-4 py-2">
              Página {page} de {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </>
      )}
    </div>
  );
}
