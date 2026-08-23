import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, UserRole } from '../types';
import { mockCurrentUser, mockUsersList } from '../data/mockData';

interface AuthContextType {
  user: UserProfile;
  setUserRole: (role: UserRole) => void;
  switchUser: (userId: string) => void;
  availableUsers: UserProfile[];
  isAuthenticated: boolean;
  login: (role: UserRole) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('labelsetu_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return mockCurrentUser;
      }
    }
    return mockCurrentUser;
  });

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return localStorage.getItem('labelsetu_auth') !== 'false';
  });

  useEffect(() => {
    localStorage.setItem('labelsetu_user', JSON.stringify(user));
    localStorage.setItem('labelsetu_auth', isAuthenticated ? 'true' : 'false');
  }, [user, isAuthenticated]);

  const setUserRole = (role: UserRole) => {
    const matching = mockUsersList.find(u => u.role === role) || {
      ...user,
      role,
    };
    setUser(matching);
  };

  const switchUser = (userId: string) => {
    const target = mockUsersList.find(u => u.id === userId);
    if (target) {
      setUser(target);
    }
  };

  const login = (role: UserRole) => {
    const matched = mockUsersList.find(u => u.role === role) || mockCurrentUser;
    setUser(matched);
    setIsAuthenticated(true);
  };

  const logout = () => {
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{
      user,
      setUserRole,
      switchUser,
      availableUsers: mockUsersList,
      isAuthenticated,
      login,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
