/**
 * Authentication context provider for React components.
 *
 * Provides authentication state and methods throughout the application.
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useMemo,
} from 'react';
import type { ReactNode } from 'react';
import {
  User,
  login as authLogin,
  logout as authLogout,
  register as authRegister,
  verifyToken,
  getStoredUser,
  isAuthenticated as checkIsAuthenticated,
} from '../services/auth';

/**
 * Authentication context state.
 */
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<User>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Props for AuthProvider component.
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication provider component.
 *
 * Wraps the application to provide authentication state and methods.
 */
export function AuthProvider({ children }: AuthProviderProps): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    async function initAuth() {
      setIsLoading(true);
      try {
        // Try to get stored user first for immediate UI
        const storedUser = getStoredUser();
        if (storedUser) {
          setUser(storedUser);
        }

        // Verify token with server
        if (checkIsAuthenticated()) {
          const verifiedUser = await verifyToken();
          setUser(verifiedUser);
        }
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<User> => {
    const loggedInUser = await authLogin({ email, password });
    setUser(loggedInUser);
    return loggedInUser;
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    await authLogout();
    setUser(null);
  }, []);

  const register = useCallback(
    async (email: string, password: string, displayName?: string): Promise<User> => {
      const newUser = await authRegister({
        email,
        password,
        display_name: displayName,
      });
      setUser(newUser);
      return newUser;
    },
    []
  );

  const refreshUser = useCallback(async (): Promise<void> => {
    const verifiedUser = await verifyToken();
    setUser(verifiedUser);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      register,
      refreshUser,
    }),
    [user, isLoading, login, logout, register, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context.
 *
 * @returns Authentication context
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
