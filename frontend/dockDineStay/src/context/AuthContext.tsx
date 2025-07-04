import type { ReactNode } from 'react';
import React, { createContext, useContext, useEffect, useState } from 'react';
// import api from '../api'; // Your Axios instance
import { jwtDecode } from 'jwt-decode'; // For decoding JWTs (install this too)

// Define the shape of the user payload from the JWT
interface DecodedToken {
  sub: string; // username
  user_id: string;
  role: string;
  exp: number; // expiration timestamp
}

// Define the shape of the AuthContext state
interface AuthContextType {
  isAuthenticated: boolean;
  user: {
    id: string;
    username: string;
    role: string;
  } | null;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean; // To indicate if auth state is being loaded
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<{ id: string; username: string; role: string } | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Initial loading state

  // Function to decode and set user from token
  const decodeAndSetUser = (token: string) => {
    try {
      const decoded: DecodedToken = jwtDecode(token);
      // Check if token is expired
      if (decoded.exp * 1000 < Date.now()) {
        console.warn('Token expired. Logging out.');
        logout();
        return null;
      }
      return {
        id: decoded.user_id,
        username: decoded.sub,
        role: decoded.role,
      };
    } catch (error) {
      console.error('Failed to decode token:', error);
      logout(); // Invalidate token if decoding fails
      return null;
    }
  };

  // On initial load, check for an existing token
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const decodedUser = decodeAndSetUser(token);
      if (decodedUser) {
        setIsAuthenticated(true);
        setUser(decodedUser);
      }
    }
    setLoading(false); // Auth state loaded
  }, []);

  const login = (token: string) => {
    localStorage.setItem('accessToken', token);
    const decodedUser = decodeAndSetUser(token);
    if (decodedUser) {
      setIsAuthenticated(true);
      setUser(decodedUser);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    setIsAuthenticated(false);
    setUser(null);
    // Redirect to login page after logout
    window.location.href = '/login'; 
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};