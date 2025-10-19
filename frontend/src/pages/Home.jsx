import React, { useEffect } from "react";
import { useBooksContext } from "../context/BooksContext";
import StatsCard from "../components/StatsCard";
import SearchSection from "../components/SearchSection";
import BookGrid from "../components/BookGrid";
import ErrorMessage from "../components/ErrorMessage";
import "../styles/Home.css";

const Home = () => {
  const {
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
  } = useBooksContext();

  const [resultType, setResultType] = React.useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const handleSearch = async (type, value) => {
    setResultType(type);
    try {
      switch (type) {
        case "user":
          await loadUserRecommendations(value);
          break;
        case "book":
          await loadSimilarBooks(value);
          break;
        case "userBooks":
          await loadUserBooks(value);
          break;
        default:
          break;
      }
    } catch (err) {
      console.error("Error en búsqueda:", err);
    }
  };

  const getDisplayData = () => {
    if (resultType === "userBooks") {
      return userBooks;
    }
    return recommendations;
  };

  const getGridType = () => {
    switch (resultType) {
      case "user":
        return "recommendations";
      case "book":
        return "similar";
      case "userBooks":
        return "userBooks";
      default:
        return "recommendations";
    }
  };

  return (
    <div className="home-page">
      <StatsCard stats={stats} loading={!stats} />

      <ErrorMessage message={error} onClose={clearError} />

      <SearchSection onSearch={handleSearch} loading={loading} />

      {(recommendations.length > 0 || userBooks.length > 0) && (
        <BookGrid
          books={getDisplayData()}
          type={getGridType()}
          loading={loading}
        />
      )}
    </div>
  );
};

export default Home;
