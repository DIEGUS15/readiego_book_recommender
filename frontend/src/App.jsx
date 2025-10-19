import React from "react";
import { BooksProvider } from "./context/BooksContext";
import Home from "./pages/Home";
import "./styles/App.css";

function App() {
  return (
    <BooksProvider>
      <div className="app-container">
        <div className="container">
          <div className="header">
            <h1>📚 Readiego</h1>
            <p>Sistema Inteligente de Recomendación de Libros con Grafos</p>
          </div>
          <Home />
        </div>
      </div>
    </BooksProvider>
  );
}

export default App;
