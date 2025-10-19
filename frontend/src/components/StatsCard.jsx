import React from "react";
import "../styles/StatsCard.css";

const StatsCard = ({ stats, loading }) => {
  if (loading) {
    return (
      <div className="stats-card">
        <h2>📊 Estadísticas del Sistema</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="stats-card">
      <h2>📊 Estadísticas del Sistema</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-number">
            {stats.users?.toLocaleString() || 0}
          </div>
          <div className="stat-label">Usuarios</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {stats.books?.toLocaleString() || 0}
          </div>
          <div className="stat-label">Libros</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {stats.ratings?.toLocaleString() || 0}
          </div>
          <div className="stat-label">Calificaciones</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {stats.density ? (stats.density * 100).toFixed(4) : 0}%
          </div>
          <div className="stat-label">Densidad del Grafo</div>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
