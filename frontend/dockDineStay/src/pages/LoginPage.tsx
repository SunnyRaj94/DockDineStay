// src/pages/LoginPage.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); // Clear previous errors BEFORE making the request

    try {
      const formData = new URLSearchParams();
      formData.append('grant_type', 'password');
      formData.append('username', username);
      formData.append('password', password);

      console.log("Sending login request..."); // Log 1

      const response = await api.post('/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log("Login response received:", response); // Log 2: Check the full response object
      console.log("Response data:", response.data); // Log 3: Check the data part of the response

      const { access_token } = response.data;
      
      if (!access_token) {
          console.error("Access token not found in response data!"); // Log 4: If token is missing
          setError("Login failed: Missing access token from server.");
          return; // Stop execution if no token
      }

      console.log("Access token extracted:", access_token); // Log 5

      login(access_token); // Use the login function from AuthContext
      
      console.log("Login function in AuthContext called. Navigating to dashboard..."); // Log 6
      navigate('/dashboard'); // Redirect to dashboard after successful login

    } catch (err: any) {
      console.error('Login error (frontend catch block):', err); // Log 7: Catch any errors here
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
            setError(err.response.data.detail[0].msg || "Login failed: Server error.");
        } else if (typeof err.response.data.detail === 'string') {
            setError(err.response.data.detail);
        } else {
            setError("Login failed: Unknown server response error.");
        }
      } else {
        setError('Login failed. Please check your credentials and try again.');
      }
    }
  };

  return (
    // ... rest of your LoginPage component (no changes here)
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        {error && <p style={{ color: 'red', marginBottom: '15px' }}>{error}</p>}
        <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Login</button>
      </form>
    </div>
  );
};

export default LoginPage;