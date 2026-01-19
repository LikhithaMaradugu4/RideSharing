import React, { createContext, useContext, useEffect, useState } from "react";
import { attachSessionInterceptor } from "../api/axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  const isAuthenticated = !!sessionId && !!user;

  // Attach axios interceptor
  useEffect(() => {
    attachSessionInterceptor(() => sessionId);
  }, [sessionId]);

  // Restore session from localStorage
  useEffect(() => {
    const s = localStorage.getItem("session_id");
    const u = localStorage.getItem("user");

    if (s && u) {
      setSessionId(s);
      setUser(JSON.parse(u));
    }

    // VERY IMPORTANT
    setAuthChecked(true);
  }, []);

  const login = ({ session_id, user }) => {
    setSessionId(session_id);
    setUser(user);

    localStorage.setItem("session_id", session_id);
    localStorage.setItem("user", JSON.stringify(user));
  };

  const logout = () => {
    setSessionId(null);
    setUser(null);
    localStorage.clear();
  };

  return (
    <AuthContext.Provider
      value={{
        sessionId,
        user,
        isAuthenticated,
        authChecked,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
