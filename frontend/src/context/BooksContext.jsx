import { createContext, useState, useContext } from "react";
import {
  getHealthStats,
  getRecommendationsForUser,
  getSimilarBooks,
  getUserBooks,
} from "../api/books";

const BooksContext = createContext();

export const useBooksContext = () => {
  const context = useContext(BooksContext);
  if (!context) {
    throw new Error("useBooksContext must be used within BooksProvider");
  }
  return context;
};

export const BooksProvider = ({ children }) => {
  const [stats, setStats] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [userBooks, setUserBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar estadísticas
  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await getHealthStats();
      setStats(response.data.stats);
      setError(null);
    } catch (err) {
      setError("Error al cargar estadísticas");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Obtener recomendaciones por usuario
  const loadUserRecommendations = async (userId, topN = 10) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getRecommendationsForUser(userId, topN);
      setRecommendations(response.data.recommendations);
      return response.data;
    } catch (err) {
      setError(`Usuario ${userId} no encontrado o sin recomendaciones`);
      setRecommendations([]);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Obtener libros similares
  const loadSimilarBooks = async (isbn, topN = 10) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getSimilarBooks(isbn, topN);
      setRecommendations(response.data.similar_books);
      return response.data;
    } catch (err) {
      setError(`Libro con ISBN ${isbn} no encontrado`);
      setRecommendations([]);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Obtener libros de un usuario
  const loadUserBooks = async (userId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getUserBooks(userId);
      setUserBooks(response.data.books);
      return response.data;
    } catch (err) {
      setError(`Usuario ${userId} no encontrado o sin libros`);
      setUserBooks([]);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  return (
    <BooksContext.Provider
      value={{
        stats,
        recommendations,
        userBooks,
        loading,
        error,
        loadStats,
        loadUserRecommendations,
        loadSimilarBooks,
        loadUserBooks,
        clearError,
      }}
    >
      {children}
    </BooksContext.Provider>
  );
};
