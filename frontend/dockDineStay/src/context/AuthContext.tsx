import { jwtDecode } from "jwt-decode"; // For decoding JWTs
import type { ReactNode } from "react";
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react"; // Added useCallback

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
  token: string | null; // <--- ADD THIS LINE
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<{
    id: string;
    username: string;
    role: string;
  } | null>(null);
  const [token, setToken] = useState<string | null>(null); // <--- ADD THIS STATE
  const [loading, setLoading] = useState<boolean>(true);

  // Function to decode and set user from token (wrapped in useCallback for stability)
  const decodeAndSetUser = useCallback((t: string | null) => {
    // Modified to accept null
    if (!t) {
      return null;
    }
    try {
      const decoded: DecodedToken = jwtDecode(t);
      // Check if token is expired
      if (decoded.exp * 1000 < Date.now()) {
        console.warn("Token expired during decode. Clearing token.");
        localStorage.removeItem("accessToken"); // Clear expired token from storage
        setToken(null); // Clear token state
        setIsAuthenticated(false);
        setUser(null);
        return null;
      }
      return {
        id: decoded.user_id,
        username: decoded.sub,
        role: decoded.role,
      };
    } catch (error) {
      console.error("Failed to decode token. It might be invalid:", error);
      localStorage.removeItem("accessToken"); // Clear invalid token
      setToken(null); // Clear token state
      setIsAuthenticated(false);
      setUser(null);
      return null;
    }
  }, []); // No dependencies for decodeAndSetUser itself

  // On initial load, check for an existing token
  useEffect(() => {
    // console.log("AuthContext: Running initial useEffect to check token...");
    const storedToken = localStorage.getItem("accessToken");
    if (storedToken) {
      const decodedUser = decodeAndSetUser(storedToken);
      if (decodedUser) {
        setToken(storedToken); // <--- SET TOKEN STATE HERE
        setIsAuthenticated(true);
        setUser(decodedUser);
        // console.log("AuthContext: Token found and valid, user set.");
      } else {
        // decodeAndSetUser would have already cleared local storage if invalid/expired
        console.log(
          "AuthContext: Stored token found but invalid/expired. Cleared."
        );
      }
    } else {
      console.log("AuthContext: No token found in localStorage.");
    }
    setLoading(false); // Auth state loaded regardless of token presence
  }, [decodeAndSetUser]); // Dependency: decodeAndSetUser is stable because of useCallback

  const login = (newToken: string) => {
    localStorage.setItem("accessToken", newToken);
    setToken(newToken); // <--- SET TOKEN STATE HERE
    const decodedUser = decodeAndSetUser(newToken);
    if (decodedUser) {
      setIsAuthenticated(true);
      setUser(decodedUser);
      console.log("AuthContext: Login successful, user set.");
    } else {
      // This case means a token was provided but it was immediately invalid/expired
      console.error(
        "AuthContext: Login attempted with an invalid/expired token."
      );
      // decodeAndSetUser would have already handled clearing state/storage
    }
  };

  const logout = () => {
    console.log("AuthContext: Logging out.");
    localStorage.removeItem("accessToken");
    setToken(null); // <--- CLEAR TOKEN STATE HERE
    setIsAuthenticated(false);
    setUser(null);
    // Redirect to login page after logout
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, token, login, logout, loading }}
    >
      {" "}
      {/* <--- ADD TOKEN HERE */}
      {loading ? ( // You might want a loading spinner here while auth state initializes
        <div>Loading authentication...</div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
