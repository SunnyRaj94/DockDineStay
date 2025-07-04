// src/pages/AdminHotelRoomsPage.tsx
import axios from "axios";
import { format } from "date-fns"; // For better date formatting
import React, { useCallback, useEffect, useState } from "react";
import LoadingSpinner from "../components/LoadingSpinner";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";
import styles from "./AdminHotelRoomsPage.module.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Define the HotelRoom type based on your backend Pydantic model
interface HotelRoom {
  id: string;
  room_number: string;
  type: string;
  price: number;
  status: "available" | "booked" | "maintenance";
  features: string[];
  image_url?: string;
  created_at: string;
  updated_at: string;
}

// Define the shape of data for creating/updating a room (FOR FORM STATE)
interface HotelRoomFormData {
  room_number: string;
  type: string;
  price: number;
  status: "available" | "booked" | "maintenance";
  features: string; // THIS IS A STRING FOR THE TEXTAREA BINDING
  image_url?: string;
}

const AdminHotelRoomsPage: React.FC = () => {
  const { token, isAuthenticated, user } = useAuth();
  const [rooms, setRooms] = useState<HotelRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentRoom, setCurrentRoom] = useState<HotelRoom | null>(null);

  const [formData, setFormData] = useState<HotelRoomFormData>({
    room_number: "",
    type: "Standard", // Default value
    price: 0,
    status: "available",
    features: "",
    image_url: "",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const fetchRooms = useCallback(async () => {
    setLoading(true);
    setError(null);
    setFormSuccess(null); // Clear previous success messages

    // console.log("--- Fetching Rooms Debug ---");
    // console.log("Current isAuthenticated:", isAuthenticated);
    // console.log("Current user role:", user?.role);
    // console.log("Token in fetchRooms:", token);
    // console.log("Token length:", token?.length);

    if (!token) {
      console.warn(
        "No token found when trying to fetch rooms. User might not be logged in or token not loaded yet."
      );
      setError(
        "You are not authenticated or your session has expired. Please log in."
      );
      setLoading(false);
      return; // Stop execution if no token
    }

    try {
      const response = await axios.get<HotelRoom[]>(`${API_BASE_URL}/rooms`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setRooms(response.data);
      // console.log("Rooms fetched successfully:", response.data);
    } catch (err: any) {
      console.error("Failed to fetch rooms:", err);
      if (axios.isAxiosError(err) && err.response) {
        // console.error('Error Response Status:', err.response.status);
        // console.error('Error Response Data:', err.response.data);
        if (err.response.data && err.response.data.detail) {
          setError(`Failed to load hotel rooms: ${err.response.data.detail}`);
        } else {
          setError(`Failed to load hotel rooms: ${err.response.status} ${err.response.statusText}`);
        }
      } else {
        setError("Failed to load hotel rooms. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, [token, isAuthenticated, user]); // Dependencies for useCallback

  // Call fetchRooms when token or isAuthenticated status changes
  useEffect(() => {
    // Only call fetchRooms if token exists and user is authenticated
    if (token && isAuthenticated) {
      fetchRooms();
    } else if (!isAuthenticated && !loading) { // Check !loading to prevent error from flashing while auth is loading
        setError("Please log in to view this page.");
    }
  }, [token, isAuthenticated, fetchRooms]); // Removed 'loading' from dependencies!


  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "price" ? parseFloat(value) : value,
    }));
  };

  const handleFeaturesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData((prev) => ({
      ...prev,
      features: e.target.value, // Directly store the string from the textarea
    }));
  };

  const handleCreateNew = () => {
    setIsEditing(false);
    setCurrentRoom(null); // Clear any previously loaded room
    setFormData({
      room_number: "",
      type: "Standard", // Default type
      price: 0,
      status: "available",
      features: "", // Empty string for new room
      image_url: "",
    });
    setFormError(null);
    setFormSuccess(null);
    setShowModal(true);
  };

  const handleEditRoom = (room: HotelRoom) => {
    setIsEditing(true);
    setCurrentRoom(room);
    setFormData({
      room_number: room.room_number,
      type: room.type,
      price: room.price,
      status: room.status,
      // Join the features array into a comma-separated string for the textarea
      features: room.features.join(", "),
      image_url: room.image_url || "",
    });
    setFormError(null);
    setFormSuccess(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    // Basic client-side validation
    if (!formData.room_number || !formData.type || formData.price <= 0) {
      setFormError("Room number, type, and a positive price are required.");
      return;
    }

    // --- Convert features string to array before sending to API ---
    const featuresArray = formData.features
      .split(',') // Split by comma
      .map(feature => feature.trim()) // Trim whitespace from each feature
      .filter(feature => feature !== ''); // Remove any empty strings (e.g., from ", ,")

    const dataToSend = {
      ...formData,
      features: featuresArray, // Override features with the cleaned array
    };
    // --- End conversion ---

    try {
      if (isEditing && currentRoom) {
        await axios.put(`${API_BASE_URL}/rooms/${currentRoom.id}`, dataToSend, { // Use dataToSend
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        setFormSuccess("Room updated successfully!");
      } else {
        await axios.post(`${API_BASE_URL}/rooms`, dataToSend, { // Use dataToSend
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        setFormSuccess("Room created successfully!");
      }
      fetchRooms(); // Refresh the list
      setTimeout(() => {
        setShowModal(false); // Close modal after success
        setFormSuccess(null); // Clear success message after modal closes
      }, 1500); // Give user a moment to see success message
    } catch (err: any) {
      console.error("Submission error:", err);
      if (axios.isAxiosError(err) && err.response && err.response.data && err.response.data.detail) {
        setFormError(err.response.data.detail);
      } else {
        setFormError("An unexpected error occurred. Please try again.");
      }
    }
  };

  const handleDeleteRoom = async (roomId: string) => {
    if (
      window.confirm(
        "Are you sure you want to delete this room? This action cannot be undone."
      )
    ) {
      setLoading(true); // Set loading for the delete operation
      setError(null);
      try {
        await axios.delete(`${API_BASE_URL}/rooms/${roomId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        alert("Room deleted successfully!"); // Use alert for immediate feedback
        fetchRooms(); // Refresh list
      } catch (err: any) {
        console.error("Failed to delete room:", err);
        if (axios.isAxiosError(err) && err.response && err.response.data && err.response.data.detail) {
          setError(`Failed to delete room: ${err.response.data.detail}`);
        } else {
          setError("Failed to delete room. Please try again.");
        }
      } finally {
        setLoading(false); // End loading regardless of success/failure
      }
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  // Ensure user is an admin before rendering content
  if (!isAuthenticated || user?.role !== 'admin') {
    return (
      <div className={styles.container}>
        <h2 className={styles.heading}>Access Denied</h2>
        <p className={styles.noRoomsMessage}>You do not have permission to manage hotel rooms.</p>
        <p className={styles.noRoomsMessage}>Please log in as an administrator.</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.heading}>Manage Hotel Rooms</h2>

      <button
        onClick={handleCreateNew}
        className={`${styles.button} ${styles.primaryButton}`}
      >
        Add New Room
      </button>

      {rooms.length === 0 ? (
        <p className={styles.noRoomsMessage}>
          No rooms found. Add a new room to get started!
        </p>
      ) : (
        <div className={styles.roomList}>
          {rooms.map((room) => (
            <div key={room.id} className={styles.roomCard}>
              <div className={styles.roomImageContainer}>
                {room.image_url ? (
                  <img
                    src={room.image_url}
                    alt={`Room ${room.room_number}`}
                    className={styles.roomImage}
                  />
                ) : (
                  <div className={styles.noImageIcon}>🏨</div>
                )}
              </div>
              <div className={styles.roomDetails}>
                <h3>Room Number: {room.room_number}</h3>
                <p>
                  <strong>Type:</strong> {room.type}
                </p>
                <p>
                  <strong>Price:</strong> ₹{room.price.toLocaleString("en-IN")}
                </p>
                <p>
                  <strong>Status:</strong>{" "}
                  <span
                    className={`${styles.statusBadge} ${styles[room.status]}`}
                  >
                    {room.status.replace("_", " ").toUpperCase()}
                  </span>
                </p>
                {room.features && room.features.length > 0 && (
                  <p>
                    <strong>Features:</strong> {room.features.join(", ")}
                  </p>
                )}
                <p className={styles.timestamp}>
                  Created:{" "}
                  {format(new Date(room.created_at), "MMM dd, yyyy HH:mm")}
                </p>
                <p className={styles.timestamp}>
                  Updated:{" "}
                  {format(new Date(room.updated_at), "MMM dd, yyyy HH:mm")}
                </p>
                <div className={styles.roomCardActions}>
                  <button
                    onClick={() => handleEditRoom(room)}
                    className={`${styles.button} ${styles.editButton}`}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteRoom(room.id)}
                    className={`${styles.button} ${styles.deleteButton}`}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        show={showModal}
        onClose={() => setShowModal(false)}
        title={isEditing ? "Edit Room" : "Add New Room"}
      >
        <form onSubmit={handleSubmit} className={styles.form}>
          {formError && <div className={styles.formError}>{formError}</div>}
          {formSuccess && (
            <div className={styles.formSuccess}>{formSuccess}</div>
          )}

          <div className={styles.formGroup}>
            <label htmlFor="room_number">Room Number:</label>
            <input
              type="text"
              id="room_number"
              name="room_number"
              value={formData.room_number}
              onChange={handleInputChange}
              required
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="type">Type:</label>
            <select
              id="type"
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              className={styles.select}
            >
              <option value="Standard">Standard</option>
              <option value="Delux">Delux</option>
              <option value="Suite">Suite</option>
              <option value="Single">Single</option>
              <option value="Double">Double</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="price">Price (₹):</label>
            <input
              type="number"
              id="price"
              name="price"
              value={formData.price}
              onChange={handleInputChange}
              required
              min="0.01"
              step="0.01"
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="status">Status:</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className={styles.select}
            >
              <option value="available">Available</option>
              <option value="booked">Booked</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="features">Features (comma-separated):</label>
            <textarea
              id="features"
              name="features"
              value={formData.features}
              onChange={handleFeaturesChange}
              className={styles.textarea}
              rows={3}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="image_url">Image URL (Optional):</label>
            <input
              type="text"
              id="image_url"
              name="image_url"
              value={formData.image_url}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>

          <div className={styles.formActions}>
            <button
              type="submit"
              className={`${styles.button} ${styles.primaryButton}`}
            >
              {isEditing ? "Update Room" : "Create Room"}
            </button>
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className={`${styles.button} ${styles.secondaryButton}`}
            >
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminHotelRoomsPage;