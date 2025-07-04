// src/pages/ProfilePage.tsx
import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import type { User } from "../types"; // Using type-only import
import classes from "./ProfilePage.module.css";

const ProfilePage: React.FC = () => {
  const { isAuthenticated, user: currentUser, refreshUser } = useAuth();
  const [userProfile, setUserProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // State for Edit Profile Form
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editName, setEditName] = useState("");
  const [editPhone, setEditPhone] = useState("");

  // State for Change Password Form
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");

  // Function to fetch user profile
  const fetchUserProfile = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null); // Clear messages on new fetch
    if (!isAuthenticated) {
      setError("You must be logged in to view your profile.");
      setLoading(false);
      return;
    }
    try {
      const response = await api.get<User>("/users/me");
      setUserProfile(response.data);
      // Initialize edit form states when profile is fetched
      setEditName(response.data.name || "");
      setEditPhone(response.data.phone || "");
    } catch (err: any) {
      console.error("Failed to fetch user profile:", err);
      let errorMessage = "Failed to fetch profile. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          const messages = err.response.data.detail.map((errorItem: any) => {
            const loc =
              Array.isArray(errorItem.loc) && errorItem.loc.length > 1
                ? errorItem.loc[errorItem.loc.length - 1]
                : "unknown_field";
            return `${loc}: ${errorItem.msg}`;
          });
          errorMessage = `Validation Error: ${messages.join("; ")}`;
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, [isAuthenticated]);

  // Handle Edit Profile Form Submission
  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    if (!userProfile) return;

    try {
      const updatePayload = {
        name: editName,
        phone: editPhone,
      };

      // --- CHANGE THIS LINE ---
      const response = await api.patch<User>( // Changed from api.put to api.patch
        `/users/${userProfile.id}`,
        updatePayload
      );
      setUserProfile(response.data); // Update local state with new data
      setSuccessMessage("Profile updated successfully!");
      setIsEditingProfile(false); // Exit edit mode
      refreshUser(); // Refresh the user context
    } catch (err: any) {
      console.error("Failed to update profile:", err);
      let errorMessage = "Failed to update profile. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          const messages = err.response.data.detail.map((errorItem: any) => {
            const loc =
              Array.isArray(errorItem.loc) && errorItem.loc.length > 1
                ? errorItem.loc[errorItem.loc.length - 1]
                : "unknown_field";
            return `${loc}: ${errorItem.msg}`;
          });
          errorMessage = `Validation Error: ${messages.join("; ")}`;
        }
      }
      setError(errorMessage);
    }
  };

  // Handle Change Password Form Submission
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (newPassword !== confirmNewPassword) {
      setError("New password and confirm password do not match.");
      return;
    }

    if (!userProfile?.id) {
      setError("User ID not available for password change.");
      return;
    }

    try {
      const passwordUpdatePayload = {
        password: newPassword, // Send only the new password
      };

      // --- CHANGE THIS LINE ---
      await api.patch<User>(`/users/${userProfile.id}`, passwordUpdatePayload); // Changed from api.put to api.patch

      setSuccessMessage("Password changed successfully!");
      setIsChangingPassword(false); // Exit password change mode
      setCurrentPassword("");
      setNewPassword("");
      setConfirmNewPassword("");
    } catch (err: any) {
      console.error("Failed to change password:", err);
      let errorMessage = "Failed to change password. Please try again.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          const messages = err.response.data.detail.map((errorItem: any) => {
            const loc =
              Array.isArray(errorItem.loc) && errorItem.loc.length > 1
                ? errorItem.loc[errorItem.loc.length - 1]
                : "unknown_field";
            return `${loc}: ${errorItem.msg}`;
          });
          errorMessage = `Validation Error: ${messages.join("; ")}`;
        }
      }
      setError(errorMessage);
    }
  };

  // ... (rest of the component JSX)
  if (loading) {
    return <div className={classes.loading}>Loading profile...</div>;
  }

  if (error && !successMessage) {
    return <div className={classes.error}>Error: {error}</div>;
  }

  if (!userProfile) {
    return <div className={classes.error}>User profile not found.</div>;
  }

  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>My Profile</h2>

      {successMessage && (
        <div className={classes.success}>{successMessage}</div>
      )}
      {error && !successMessage && <div className={classes.error}>{error}</div>}

      {userProfile.profile_pic && (
        <div className={classes.profilePicContainer}>
          <img
            src={userProfile.profile_pic}
            alt={`${userProfile.username}'s profile`}
            className={classes.profilePic}
          />
        </div>
      )}

      {/* Profile Details View Mode */}
      {!isEditingProfile && !isChangingPassword && (
        <>
          <div className={classes.profileDetails}>
            <div className={classes.label}>Username:</div>
            <div className={classes.value}>{userProfile.username}</div>

            <div className={classes.label}>Email:</div>
            <div className={classes.value}>{userProfile.email}</div>

            <div className={classes.label}>Full Name:</div>
            <div className={classes.value}>
              {userProfile.name || "Not provided"}
            </div>

            <div className={classes.label}>Role:</div>
            <div className={classes.value}>{userProfile.role}</div>

            <div className={classes.label}>Phone:</div>
            <div className={classes.value}>
              {userProfile.phone || "Not provided"}
            </div>

            <div className={classes.label}>Account Status:</div>
            <div className={classes.value}>
              {userProfile.is_active ? "Active" : "Inactive"}
            </div>

            <div className={classes.label}>Joined On:</div>
            <div className={classes.value}>
              {userProfile.created_at
                ? new Date(userProfile.created_at).toLocaleDateString()
                : "N/A"}
            </div>

            <div className={classes.label}>Last Updated:</div>
            <div className={classes.value}>
              {userProfile.updated_at
                ? new Date(userProfile.updated_at).toLocaleDateString()
                : "N/A"}
            </div>
          </div>

          <div className={classes.buttonGroup}>
            <button
              onClick={() => setIsEditingProfile(true)}
              className={`${classes.button} ${classes.buttonPrimary}`}
            >
              Edit Profile
            </button>
            <button
              onClick={() => setIsChangingPassword(true)}
              className={`${classes.button} ${classes.buttonSecondary}`}
            >
              Change Password
            </button>
          </div>
        </>
      )}

      {/* Edit Profile Form */}
      {isEditingProfile && (
        <div className={classes.formContainer}>
          <h3 className={classes.heading}>Edit Profile</h3>
          <form onSubmit={handleUpdateProfile}>
            <div className={classes.formGroup}>
              <label htmlFor="editName" className={classes.label}>
                Full Name:
              </label>
              <input
                type="text"
                id="editName"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className={classes.input}
              />
            </div>
            <div className={classes.formGroup}>
              <label htmlFor="editPhone" className={classes.label}>
                Phone:
              </label>
              <input
                type="text"
                id="editPhone"
                value={editPhone}
                onChange={(e) => setEditPhone(e.target.value)}
                required
                className={classes.input}
              />
            </div>
            <div className={classes.buttonGroup}>
              <button
                type="submit"
                className={`${classes.button} ${classes.buttonPrimary}`}
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsEditingProfile(false);
                  setError(null);
                  setSuccessMessage(null);
                  setEditName(userProfile.name || "");
                  setEditPhone(userProfile.phone || "");
                }}
                className={`${classes.button} ${classes.buttonSecondary}`}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Change Password Form */}
      {isChangingPassword && (
        <div className={classes.formContainer}>
          <h3 className={classes.heading}>Change Password</h3>
          <form onSubmit={handleChangePassword}>
            <div className={classes.formGroup}>
              <label htmlFor="currentPassword" className={classes.label}>
                Current Password (Not Verified by Backend in This Setup!):
              </label>
              <input
                type="password"
                id="currentPassword"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className={classes.input}
              />
            </div>
            <div className={classes.formGroup}>
              <label htmlFor="newPassword" className={classes.label}>
                New Password:
              </label>
              <input
                type="password"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                className={classes.input}
              />
            </div>
            <div className={classes.formGroup}>
              <label htmlFor="confirmNewPassword" className={classes.label}>
                Confirm New Password:
              </label>
              <input
                type="password"
                id="confirmNewPassword"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                required
                className={classes.input}
              />
            </div>
            <div className={classes.buttonGroup}>
              <button
                type="submit"
                className={`${classes.button} ${classes.buttonPrimary}`}
              >
                Change Password
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsChangingPassword(false);
                  setError(null);
                  setSuccessMessage(null);
                  setCurrentPassword("");
                  setNewPassword("");
                  setConfirmNewPassword("");
                }}
                className={`${classes.button} ${classes.buttonSecondary}`}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;