// src/pages/ProfilePage.tsx
import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";

// Define CSS variables as constants (can be reused from ManageUsersPage or put in a central file)
const styles = {
  container: {
    maxWidth: "800px",
    margin: "50px auto",
    padding: "30px",
    border: "1px solid var(--border-color, #ccc)",
    borderRadius: "10px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    backgroundColor: "var(--background-color, #fff)",
    color: "var(--text-color, #333)",
  },
  heading: {
    textAlign: "center" as const,
    color: "var(--primary-color, #007bff)",
    marginBottom: "30px",
    fontSize: "2.5em",
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
    padding: "15px",
    backgroundColor: "var(--error-background, #ffebeb)",
    color: "var(--error-color, #dc3545)",
    border: "1px solid var(--error-color, #dc3545)",
    borderRadius: "8px",
    fontWeight: "bold",
    fontSize: "1.1em",
  },
  profileDetails: {
    display: "grid",
    gridTemplateColumns: "1fr 2fr",
    gap: "15px 30px",
    fontSize: "1.1em",
    marginBottom: "30px",
  },
  label: {
    fontWeight: "bold",
    color: "var(--text-color-light, #555)",
  },
  value: {
    color: "var(--text-color, #333)",
  },
  buttonGroup: {
    textAlign: "center" as const,
    marginTop: "30px",
  },
  button: {
    padding: "12px 25px",
    margin: "0 10px",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "1.1em",
    transition: "background-color 0.2s ease-in-out",
  },
  buttonPrimary: {
    backgroundColor: "var(--primary-color, #007bff)",
    "&:hover": {
      backgroundColor: "var(--primary-hover-color, #0056b3)",
    },
  },
  buttonSecondary: {
    backgroundColor: "var(--button-secondary-color, #6c757d)", // Added a secondary button color
    "&:hover": {
      backgroundColor: "var(--button-secondary-hover-color, #5a6268)",
    },
  },
  profilePicContainer: {
    textAlign: 'center' as const,
    marginBottom: '20px',
  },
  profilePic: {
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    objectFit: 'cover' as const,
    border: '3px solid var(--primary-color, #007bff)',
  },
};

// Define a basic User interface based on your backend User model
// Ensure this matches your backend's User model and how it's serialized
interface User {
  id: string;
  username: string;
  email: string;
  name?: string;
  role: "admin" | "front-desk" | "back-desk" | "customer";
  phone?: string; // It's optional here because the backend might not always send it for profile (though you made it required for creation)
  profile_pic?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}



const ProfilePage: React.FC = () => {
  const { user: currentUser, isAuthenticated } = useAuth(); // Get current user info from AuthContext
  const [userProfile, setUserProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserProfile = async () => {
      setLoading(true);
      setError(null);
      if (!isAuthenticated) {
        setError("You must be logged in to view your profile.");
        setLoading(false);
        return;
      }
      try {
        // Fetch current user's profile using the /users/me endpoint
        const response = await api.get<User>("/users/me");
        setUserProfile(response.data);
      } catch (err: any) {
        console.error("Failed to fetch user profile:", err);
        let errorMessage = "Failed to fetch profile. Please try again.";
        if (err.response && err.response.data && err.response.data.detail) {
          if (typeof err.response.data.detail === "string") {
            errorMessage = err.response.data.detail;
          }
        }
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [isAuthenticated]); // Re-fetch if authentication status changes

  const handleEditProfile = () => {
    // Placeholder for navigating to an edit form or opening a modal
    alert("Implement profile editing functionality!");
  };

  const handleChangePassword = () => {
    // Placeholder for navigating to a change password form or opening a modal
    alert("Implement change password functionality!");
  };

  if (loading) {
    return <div style={styles.loading}>Loading profile...</div>;
  }

  if (error) {
    return <div style={styles.error}>Error: {error}</div>;
  }

  if (!userProfile) {
    return <div style={styles.error}>User profile not found.</div>;
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>My Profile</h2>

      {userProfile.profile_pic && (
        <div style={styles.profilePicContainer}>
          <img
            src={userProfile.profile_pic}
            alt={`${userProfile.username}'s profile`}
            style={styles.profilePic}
          />
        </div>
      )}

      <div style={styles.profileDetails}>
        <div style={styles.label}>Username:</div>
        <div style={styles.value}>{userProfile.username}</div>

        <div style={styles.label}>Email:</div>
        <div style={styles.value}>{userProfile.email}</div>

        <div style={styles.label}>Full Name:</div>
        <div style={styles.value}>{userProfile.name || "Not provided"}</div>

        <div style={styles.label}>Role:</div>
        <div style={styles.value}>{userProfile.role}</div>

        <div style={styles.label}>Phone:</div>
        <div style={styles.value}>{userProfile.phone || "Not provided"}</div>

        <div style={styles.label}>Account Status:</div>
        <div style={styles.value}>
          {userProfile.is_active ? "Active" : "Inactive"}
        </div>

        <div style={styles.label}>Joined On:</div>
        <div style={styles.value}>
          {userProfile.created_at
            ? new Date(userProfile.created_at).toLocaleDateString()
            : "N/A"}
        </div>

        <div style={styles.label}>Last Updated:</div>
        <div style={styles.value}>
          {userProfile.updated_at
            ? new Date(userProfile.updated_at).toLocaleDateString()
            : "N/A"}
        </div>
      </div>

      <div style={styles.buttonGroup}>
        <button
          onClick={handleEditProfile}
          style={{ ...styles.button, ...styles.buttonPrimary }}
        >
          Edit Profile
        </button>
        <button
          onClick={handleChangePassword}
          style={{ ...styles.button, ...styles.buttonSecondary }}
        >
          Change Password
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;