// src/App.tsx
import { Link, Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

// Import your pages
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import ManageUsersPage from "./pages/ManageUsersPage";
import ProfilePage from "./pages/ProfilePage";

// Import the new App.css
import "./App.css";
// Make sure src/index.css is also imported in src/main.tsx or here for global styles
// import './index.css'; // If not already in main.tsx

function App() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <>
      <nav className="navbar">
        {" "}
        {/* Use class for navbar */}
        <Link to="/" className="navbar-brand">
          {" "}
          {/* Use class for brand */}
          DockDineStay
        </Link>
        <div className="navbar-links">
          {" "}
          {/* Use class for links container */}
          {isAuthenticated ? (
            <>
              <span className="navbar-greeting">
                {" "}
                {/* Use class for greeting */}
                Hello, {user?.username} ({user?.role})
              </span>
              <Link to="/dashboard" className="navbar-link">
                {" "}
                {/* Use class for links */}
                Dashboard
              </Link>
              <Link to="/profile" className="navbar-link">
                {" "}
                {/* Use class for links */}
                Profile
              </Link>
              {/* Show Manage Users link only for Admin */}
              {user?.role === "admin" && (
                <Link to="/manage-users" className="navbar-link">
                  {" "}
                  {/* Use class for links */}
                  Manage Users
                </Link>
              )}
              <button onClick={logout} className="navbar-button">
                {" "}
                {/* Use class for button */}
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="navbar-link">
              {" "}
              {/* Use class for links */}
              Login
            </Link>
          )}
        </div>
      </nav>

      <div className="app-content-container">
        {" "}
        {/* Apply the main content container style */}
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
          <Route
            path="/unauthorized"
            element={
              <div className="unauthorized-container">
                {" "}
                {/* Use class for unauthorized message */}
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
    </>
  );
}

export default App;
