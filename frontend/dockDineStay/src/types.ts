
/**
 * Defines the roles a user can have in the application.
 * This should match the enum or choices defined in your backend.
 */
export enum UserRole {
  ADMIN = "admin",
  FRONT_DESK = "front-desk",
  BACK_DESK = "back-desk",
  CUSTOMER = "customer",
}

/**
 * Defines the structure of a User object throughout the frontend.
 * This interface should closely mirror your backend's User model (Pydantic model).
 */
export interface User {
  id: string; // The MongoDB ObjectId converted to a string on the backend
  username: string;
  email: string;
  password?: string; // Optional: Only sent during creation or password change, not typically retrieved
  name?: string; // Optional: Full name of the user
  role: UserRole; // User's role, using the UserRole enum
  phone?: string; // Optional: User's phone number. While required for creation, it might be optional in some contexts or if existing data is incomplete.
  profile_pic?: string; // Optional: URL to user's profile picture
  is_active?: boolean; // Optional: Account active status
  created_at?: string; // Optional: ISO 8601 string for creation timestamp
  updated_at?: string; // Optional: ISO 8601 string for last update timestamp
}

// You can add other interfaces and types here as your application grows,
// such as for bookings, docks, restaurants, etc.
/*
export interface Booking {
  id: string;
  userId: string;
  dockId?: string;
  restaurantId?: string;
  stayId?: string;
  startDate: string;
  endDate: string;
  status: 'pending' | 'confirmed' | 'cancelled';
  // ... other booking details
}
*/