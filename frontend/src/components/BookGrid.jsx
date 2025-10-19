import React from "react";
import BookCard from "./BookCard";
import "../styles/BookGrid.css";

const BookGrid = ({ books, type = "recommendations", loading }) => {
  if (loading) {
    return (
      <div className="results-section">
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando resultados...</p>
        </div>
      </div>
    );
  }

  if (!books || books.length === 0) {
    return null;
  }

  const getTitle = () => {
    switch (type) {
      case "recommendations":
        return "📚 Recomendaciones para ti";
      case "similar":
        return "📖 Libros Similares";
      case "userBooks":
        return "📕 Mis Libros";
      default:
        return "📚 Resultados";
    }
  };

  return (
    <div className="results-section">
      <div className="results-header">
        <h2>{getTitle()}</h2>
        <span className="badge">{books.length} resultados</span>
      </div>
      <div className="books-grid">
        {books.map((item, index) => {
          const book = item.book_info || item;
          return (
            <BookCard
              key={index}
              book={book}
              score={item.score}
              similarity={item.similarity}
              userRating={item.user_rating}
            />
          );
        })}
      </div>
    </div>
  );
};

export default BookGrid;
