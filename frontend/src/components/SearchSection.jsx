import React, { useState } from "react";
import "../styles/SearchSection.css";

const SearchSection = ({ onSearch, loading }) => {
  const [activeTab, setActiveTab] = useState("user");
  const [userId, setUserId] = useState("");
  const [isbn, setIsbn] = useState("");
  const [userBooksId, setUserBooksId] = useState("");

  const handleUserRecommendations = () => {
    if (userId.trim()) {
      onSearch("user", userId.trim());
    }
  };

  const handleSimilarBooks = () => {
    if (isbn.trim()) {
      onSearch("book", isbn.trim());
    }
  };

  const handleUserBooks = () => {
    if (userBooksId.trim()) {
      onSearch("userBooks", userBooksId.trim());
    }
  };

  const handleKeyPress = (e, handler) => {
    if (e.key === "Enter") {
      handler();
    }
  };

  return (
    <div className="search-section">
      <h2>🔍 Buscar Recomendaciones</h2>

      <div className="tabs">
        <button
          className={`tab ${activeTab === "user" ? "active" : ""}`}
          onClick={() => setActiveTab("user")}
        >
          Por Usuario
        </button>
        <button
          className={`tab ${activeTab === "book" ? "active" : ""}`}
          onClick={() => setActiveTab("book")}
        >
          Libros Similares
        </button>
        <button
          className={`tab ${activeTab === "userBooks" ? "active" : ""}`}
          onClick={() => setActiveTab("userBooks")}
        >
          Mis Libros
        </button>
      </div>

      {activeTab === "user" && (
        <div className="tab-content">
          <p className="tab-description">
            Ingresa el ID de un usuario para obtener recomendaciones
            personalizadas
          </p>
          <div className="input-group">
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, handleUserRecommendations)}
              placeholder="Ej: 276725, 11676, 198711..."
              disabled={loading}
            />
            <button onClick={handleUserRecommendations} disabled={loading}>
              {loading ? "Buscando..." : "Recomendar"}
            </button>
          </div>
        </div>
      )}

      {activeTab === "book" && (
        <div className="tab-content">
          <p className="tab-description">
            Ingresa el ISBN de un libro para encontrar libros similares
          </p>
          <div className="input-group">
            <input
              type="text"
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, handleSimilarBooks)}
              placeholder="Ej: 0439136350, 0060256672..."
              disabled={loading}
            />
            <button onClick={handleSimilarBooks} disabled={loading}>
              {loading ? "Buscando..." : "Buscar Similares"}
            </button>
          </div>
        </div>
      )}

      {activeTab === "userBooks" && (
        <div className="tab-content">
          <p className="tab-description">
            Ve los libros que un usuario ha calificado
          </p>
          <div className="input-group">
            <input
              type="text"
              value={userBooksId}
              onChange={(e) => setUserBooksId(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, handleUserBooks)}
              placeholder="Ej: 276725, 11676..."
              disabled={loading}
            />
            <button onClick={handleUserBooks} disabled={loading}>
              {loading ? "Cargando..." : "Ver Libros"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchSection;
