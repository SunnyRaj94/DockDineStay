import { Link, Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import ManageUsersPage from "./pages/ManageUsersPage";
import ProfilePage from "./pages/ProfilePage"; // <--- Import ProfilePage

function App() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <>
      <nav
        style={{
          padding: "10px 20px",
          backgroundColor: "#f8f9fa",
          borderBottom: "1px solid #e9ecef",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontWeight: "bold", fontSize: "1.2em" }}>
          DockDineStay
        </div>
        <div>
          {isAuthenticated ? (
            <>
              <span style={{ marginRight: "15px" }}>
                Hello, {user?.username} ({user?.role})
              </span>
              <Link
                to="/dashboard"
                style={{
                  marginRight: "15px",
                  textDecoration: "none",
                  color: "#007bff",
                }}
              >
                Dashboard
              </Link>
              {/* NEW: Link to Profile Page */}
              <Link
                to="/profile"
                style={{
                  marginRight: "15px",
                  textDecoration: "none",
                  color: "#007bff",
                }}
              >
                Profile
              </Link>
              {/* Show Manage Users link only for Admin */}
              {user?.role === "admin" && (
                <Link
                  to="/manage-users"
                  style={{
                    marginRight: "15px",
                    textDecoration: "none",
                    color: "#007bff",
                  }}
                >
                  Manage Users
                </Link>
              )}
              <button
                onClick={logout}
                style={{
                  background: "none",
                  border: "none",
                  color: "#dc3545",
                  cursor: "pointer",
                  fontSize: "1em",
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              style={{ textDecoration: "none", color: "#007bff" }}
            >
              Login
            </Link>
          )}
        </div>
      </nav>

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        {/* Route for ProfilePage, protected for any authenticated user */}
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
        {/* Add the protected route for ManageUsersPage */}
        <Route
          path="/manage-users"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <ManageUsersPage />
            </ProtectedRoute>
          }
        />
        {/* Placeholder for unauthorized access */}
        <Route
          path="/unauthorized"
          element={
            <div
              style={{ textAlign: "center", marginTop: "50px", color: "red" }}
            >
              <h3>403 - Unauthorized Access</h3>
              <p>You do not have permission to view this page.</p>
              <Link to="/dashboard">Go to Dashboard</Link>
            </div>
          }
        />
        {/* Default redirect to login if no other path matches */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  );
}

export default App;