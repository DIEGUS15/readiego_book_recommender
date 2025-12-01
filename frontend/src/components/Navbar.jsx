import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <a href="/dashboard" className="text-xl font-bold">
              📚 Readiego
            </a>

            {isAuthenticated && (
              <>
                <a href="/dashboard" className="hover:text-indigo-200">
                  Inicio
                </a>
                <a href="/catalog" className="hover:text-indigo-200">
                  Catálogo
                </a>
                <a href="/my-ratings" className="hover:text-indigo-200">
                  Mis Calificaciones
                </a>
              </>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm">Hola, {user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-md text-sm"
                >
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <>
                <a href="/login" className="hover:text-indigo-200">
                  Iniciar Sesión
                </a>
                <a
                  href="/register"
                  className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-md"
                >
                  Registrarse
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
