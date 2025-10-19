import axiosInstance from "./axios.js";

// Obtener estadísticas del sistema
export const getHealthStats = () => axiosInstance.get("/health");

// Recomendaciones para usuario
export const getRecommendationsForUser = (userId, topN = 10) =>
  axiosInstance.get(`/recommend/user/${userId}`, {
    params: { top_n: topN },
  });

// Libros similares
export const getSimilarBooks = (isbn, topN = 10) =>
  axiosInstance.get(`/recommend/book/${isbn}`, {
    params: { top_n: topN },
  });

// Libros de un usuario
export const getUserBooks = (userId) =>
  axiosInstance.get(`/user/${userId}/books`);

// Información de un libro
export const getBookInfo = (isbn) => axiosInstance.get(`/book/${isbn}`);

// Información de un usuario
export const getUserInfo = (userId) => axiosInstance.get(`/user/${userId}`);

// Usuarios de ejemplo (debug)
export const getSampleUsers = () => axiosInstance.get("/debug/sample-users");
