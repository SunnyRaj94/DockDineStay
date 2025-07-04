import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";

// Define CSS variables as constants for consistent styling
const styles = {
  container: {
    maxWidth: "1000px",
    margin: "50px auto",
    padding: "20px",
    border: "1px solid var(--border-color, #ccc)", // Fallback color
    borderRadius: "8px",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
    backgroundColor: "var(--background-color, #fff)", // Fallback color
    color: "var(--text-color, #333)", // Fallback color
  },
  heading: {
    textAlign: "center" as const,
    color: "var(--primary-color, #007bff)",
    marginBottom: "20px",
  },
  loading: {
    textAlign: "center" as const,
    marginTop: "50px",
    fontSize: "1.2em",
    color: "var(--text-color, #555)",
  },
  error: {
    textAlign: "center" as const,
    marginTop: "20px",
    padding: "10px",
    backgroundColor: "var(--error-background, #ffebeb)", // Fallback color
    color: "var(--error-color, #dc3545)", // Fallback color
    border: "1px solid var(--error-color, #dc3545)",
    borderRadius: "5px",
    fontWeight: "bold",
  },
  formContainer: {
    marginBottom: "40px",
    padding: "25px",
    border: "1px solid var(--border-light, #eee)", // Fallback color
    borderRadius: "8px",
    backgroundColor: "var(--card-background, #f9f9f9)", // Fallback color
  },
  formTitle: {
    marginBottom: "20px",
    color: "var(--primary-color, #007bff)",
  },
  formGroup: {
    marginBottom: "15px",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: "bold",
    color: "var(--text-color-light, #555)", // Fallback color
  },
  input: {
    width: "calc(100% - 18px)", // Account for padding and border
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid var(--input-border-color, #ccc)", // Fallback color
    fontSize: "1em",
    backgroundColor: "var(--input-background, #fff)", // Fallback color
    color: "var(--text-color, #333)", // Fallback color
  },
  select: {
    width: "100%",
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid var(--input-border-color, #ccc)", // Fallback color
    fontSize: "1em",
    backgroundColor: "var(--input-background, #fff)", // Fallback color
    color: "var(--text-color, #333)", // Fallback color
  },
  button: {
    padding: "10px 20px",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "1em",
    transition: "background-color 0.2s ease-in-out",
    marginTop: "10px", // Give some space
  },
  buttonPrimary: {
    backgroundColor: "var(--primary-color, #007bff)",
    "&:hover": {
      backgroundColor: "var(--primary-hover-color, #0056b3)",
    },
  },
  buttonSuccess: {
    backgroundColor: "var(--success-color, #28a745)",
    "&:hover": {
      backgroundColor: "var(--success-hover-color, #218838)",
    },
  },
  buttonDanger: {
    backgroundColor: "var(--danger-color, #dc3545)",
    "&:hover": {
      backgroundColor: "var(--danger-hover-color, #c82333)",
    },
  },
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    marginTop: "30px",
    backgroundColor: "var(--table-background, #fff)", // Fallback color
  },
  tableHeader: {
    padding: "12px 15px",
    border: "1px solid var(--border-color, #ccc)",
    textAlign: "left" as const,
    backgroundColor: "var(--table-header-bg, #f2f2f2)", // Fallback color
    fontWeight: "bold",
    color: "var(--text-color-dark, #333)", // Fallback color
  },
  tableCell: {
    padding: "12px 15px",
    border: "1px solid var(--border-color, #ccc)",
    color: "var(--text-color, #333)", // Fallback color
  },
  actionButton: {
    padding: "8px 12px",
    marginRight: "8px",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "0.9em",
    transition: "background-color 0.2s ease-in-out",
  },
};

// Define a basic User interface based on your backend User model
interface User {
  id: string; // The ID from backend, expected to be string
  username: string;
  email: string;
  password?: string; // Password is only sent on creation, not typically retrieved
  name?: string;
  role: "admin" | "front-desk" | "back-desk" | "customer";
  phone: string; // Made required based on backend
  profile_pic?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

const ManageUsersPage: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // State for new user form
  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newName, setNewName] = useState(""); // Changed from newFullName for clarity
  const [newPhone, setNewPhone] = useState(""); // Added phone state
  const [newRole, setNewRole] = useState<
    "admin" | "front-desk" | "back-desk" | "customer"
  >("front-desk");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<User[]>("/users/");
      setUsers(response.data);
    } catch (err: any) {
      console.error("Failed to fetch users:", err);
      // More robust error parsing for fetch users
      let errorMessage = "Failed to fetch users. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          const messages = err.response.data.detail.map(
            (errorItem: any) =>
              `${
                Array.isArray(errorItem.loc) && errorItem.loc.length > 1
                  ? errorItem.loc[errorItem.loc.length - 1]
                  : "unknown_field"
              }: ${errorItem.msg}`
          );
          errorMessage = `Validation Error: ${messages.join("; ")}`;
        } else if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); // Clear previous errors
    try {
      const newUserPayload = {
        username: newUsername,
        email: newEmail,
        password: newPassword,
        name: newName || undefined, // Use newName, allow undefined if empty
        phone: newPhone, // Include the new phone field
        role: newRole,
      };

      await api.post<User>("/users/", newUserPayload);
      // Clear form fields after successful creation
      setNewUsername("");
      setNewEmail("");
      setNewPassword("");
      setNewName("");
      setNewPhone(""); // Reset phone field
      setNewRole("front-desk"); // Reset role to a default or keep as last selected
      fetchUsers(); // Refresh the list of users
    } catch (err: any) {
      console.error("Failed to create user:", err);
      // Log full backend response for debugging 422 errors
      if (err.response && err.response.data) {
        console.error("Backend validation error details:", err.response.data);
      }

      // More robust error message parsing from FastAPI's 422 response
      let errorMessage = "Failed to create user. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          const messages = err.response.data.detail.map((errorItem: any) => {
            const loc =
              Array.isArray(errorItem.loc) && errorItem.loc.length > 1
                ? errorItem.loc[errorItem.loc.length - 1] // Get the field name
                : "unknown_field";
            return `${loc}: ${errorItem.msg}`;
          });
          errorMessage = `Validation Error: ${messages.join("; ")}`;
        } else if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        } else {
          // Fallback for an unexpected object structure if not an array of detail items
          errorMessage =
            "An unexpected validation error occurred. Check console for details.";
        }
      } else if (err.response) {
        // If there's a response but no 'detail' field
        errorMessage = `Error: ${
          err.response.status
        } ${err.response.statusText || "Unknown"}. Check console for response data.`;
      } else {
        // No response at all (e.g., network error)
        errorMessage = "Failed to create user. Please check your network connection.";
      }
      setError(errorMessage); // Set the safely formatted string error
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (
      !window.confirm(`Are you sure you want to delete user with ID: ${userId}?`)
    ) {
      return;
    }
    setError(null);
    try {
      await api.delete(`/users/${userId}`);
      fetchUsers(); // Refresh the list after deletion
    } catch (err: any) {
      console.error("Failed to delete user:", err);
      // More robust error handling for delete
      let errorMessage = "Failed to delete user. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        }
      }
      setError(errorMessage);
    }
  };

  const handleUpdateUser = (user: User) => {
    // Placeholder for actual update logic
    alert(`Implement update functionality for user: ${user.username}`);
  };

  if (loading) {
    return <div style={styles.loading}>Loading users...</div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Manage Users ({currentUser?.role})</h2>

      {error && <div style={styles.error}>{error}</div>} {/* Display error message here */}

      {/* New User Creation Form */}
      <div style={styles.formContainer}>
        <h3 style={styles.formTitle}>Create New User</h3>
        <form onSubmit={handleCreateUser}>
          <div style={styles.formGroup}>
            <label htmlFor="newUsername" style={styles.label}>
              Username:
            </label>
            <input
              type="text"
              id="newUsername"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="newEmail" style={styles.label}>
              Email:
            </label>
            <input
              type="email"
              id="newEmail"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="newPassword" style={styles.label}>
              Password:
            </label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="newName" style={styles.label}>
              Full Name (Optional):
            </label>
            <input
              type="text"
              id="newName"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="newPhone" style={styles.label}>
              Phone:
            </label>
            <input
              type="text" // Use "tel" for better mobile keyboard, but "text" is fine
              id="newPhone"
              value={newPhone}
              onChange={(e) => setNewPhone(e.target.value)}
              required // Make it required as per backend
              style={styles.input}
            />
          </div>
          <div style={{ ...styles.formGroup, marginBottom: "20px" }}>
            <label htmlFor="newRole" style={styles.label}>
              Role:
            </label>
            <select
              id="newRole"
              value={newRole}
              onChange={(e) =>
                setNewRole(
                  e.target.value as
                    | "admin"
                    | "front-desk"
                    | "back-desk"
                    | "customer"
                )
              }
              style={styles.select}
            >
              <option value="admin">Admin</option>
              <option value="front-desk">Front Desk</option>
              <option value="back-desk">Back Desk</option>
              <option value="customer">Customer</option>
            </select>
          </div>
          <button
            type="submit"
            style={{ ...styles.button, ...styles.buttonSuccess }}
          >
            Add User
          </button>
        </form>
      </div>

      {/* Users List */}
      <h3 style={styles.formTitle}>Existing Users</h3>
      {users.length === 0 ? (
        <p style={{ textAlign: "center", fontStyle: "italic" }}>No users found.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.tableHeader}>Username</th>
              <th style={styles.tableHeader}>Email</th>
              <th style={styles.tableHeader}>Role</th>
              <th style={styles.tableHeader}>Full Name</th>
              <th style={styles.tableHeader}>Phone</th> {/* Added phone header */}
              <th style={styles.tableHeader}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td style={styles.tableCell}>{user.username}</td>
                <td style={styles.tableCell}>{user.email}</td>
                <td style={styles.tableCell}>{user.role}</td>
                <td style={styles.tableCell}>{user.name || "N/A"}</td>
                <td style={styles.tableCell}>{user.phone || "N/A"}</td> {/* Display phone */}
                <td style={styles.tableCell}>
                  <button
                    onClick={() => handleUpdateUser(user)}
                    style={{ ...styles.actionButton, ...styles.buttonPrimary }}
                  >
                    Edit
                  </button>
                  {/* Hide delete button for the current logged-in user */}
                  {currentUser?.id !== user.id && (
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      style={{ ...styles.actionButton, ...styles.buttonDanger }}
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ManageUsersPage;