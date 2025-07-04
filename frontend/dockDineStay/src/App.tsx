// src/App.tsx
import { Link, Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

// Import your pages
import AdminHotelRoomsPage from "./pages/AdminHotelRoomsPage"; // <--- NEW IMPORT
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import ManageUsersPage from "./pages/ManageUsersPage";
import ProfilePage from "./pages/ProfilePage";

// Import the new App.css
import "./App.css";

// Import the new Footer component
import Footer from "./components/Footer";

function App() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <>
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
          DockDineStay
        </Link>
        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <span className="navbar-greeting">
                Hello, {user?.username} ({user?.role})
              </span>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/profile" className="navbar-link">
                Profile
              </Link>
              {/* Show Manage Rooms link only for Admin */}
              {user?.role === "admin" && (
                <Link to="/admin/rooms" className="navbar-link">
                  Manage Rooms
                </Link>
              )}
              {/* Show Manage Users link only for Admin */}
              {user?.role === "admin" && (
                <Link to="/manage-users" className="navbar-link">
                  Manage Users
                </Link>
              )}
              <button onClick={logout} className="navbar-button">
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="navbar-link">
              Login
            </Link>
          )}
        </div>
      </nav>
      <div className="app-content-container">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/manage-users"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <ManageUsersPage />
              </ProtectedRoute>
            }
          />
          {/* NEW: Route for AdminHotelRoomsPage */}
          <Route
            path="/admin/rooms"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminHotelRoomsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/unauthorized"
            element={
              <div className="unauthorized-container">
                <h3>403 - Unauthorized Access</h3>
                <p>You do not have permission to view this page.</p>
                <Link to="/dashboard">Go to Dashboard</Link>
              </div>
            }
          />
          {/* Default redirect to login if no other path matches */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
      <Footer /> {/* <--- NEW: Include the Footer component here */}
    </>
  );
}

export default App;