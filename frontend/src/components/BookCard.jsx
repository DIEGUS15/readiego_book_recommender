import React from "react";
import "../styles/BookCard.css";

const BookCard = ({ book, score, similarity, userRating }) => {
  const displayScore = score || similarity || userRating;

  return (
    <div className="book-card">
      <img
        src={
          book.image_url || "https://via.placeholder.com/150x220?text=No+Image"
        }
        alt={book.title}
        className="book-image"
        onError={(e) => {
          e.target.src = "https://via.placeholder.com/150x220?text=No+Image";
        }}
      />
      <div className="book-info">
        <h3 className="book-title">{book.title || "Título no disponible"}</h3>
        <p className="book-author">{book.author || "Autor desconocido"}</p>
        <div className="book-meta">
          <span className="book-year">{book.year || "Año desconocido"}</span>
          {displayScore && (
            <span className="book-score">
              {userRating
                ? `⭐ ${displayScore}`
                : `📊 ${displayScore.toFixed(2)}`}
            </span>
          )}
        </div>
        {book.isbn && <p className="book-isbn">ISBN: {book.isbn}</p>}
      </div>
    </div>
  );
};

export default BookCard;
