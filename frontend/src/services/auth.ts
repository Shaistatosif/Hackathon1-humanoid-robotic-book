/**
 * Authentication service for frontend.
 *
 * Provides methods for user authentication and token management.
 */

import { post, get, ApiError } from './api';

/**
 * User data from the API.
 */
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  language_pref: 'en' | 'ur';
  is_verified: boolean;
}

/**
 * Token response from the API.
 */
interface TokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Authentication response with user and token.
 */
interface AuthResponse {
  user: User;
  token: TokenResponse;
}

/**
 * Registration request data.
 */
interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

/**
 * Login request data.
 */
interface LoginRequest {
  email: string;
  password: string;
}

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

/**
 * Store authentication data in localStorage.
 */
function storeAuthData(token: string, user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Clear authentication data from localStorage.
 */
function clearAuthData(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Get stored user data.
 */
export function getStoredUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userData = localStorage.getItem(USER_KEY);
  if (!userData) return null;
  try {
    return JSON.parse(userData);
  } catch {
    return null;
  }
}

/**
 * Get stored authentication token.
 */
export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return !!getStoredToken();
}

/**
 * Register a new user account.
 *
 * @param data - Registration data
 * @returns User data
 */
export async function register(data: RegisterRequest): Promise<User> {
  const response = await post<AuthResponse>('/api/auth/register', data);
  storeAuthData(response.token.access_token, response.user);
  return response.user;
}

/**
 * Login with email and password.
 *
 * @param data - Login credentials
 * @returns User data
 */
export async function login(data: LoginRequest): Promise<User> {
  const response = await post<AuthResponse>('/api/auth/login', data);
  storeAuthData(response.token.access_token, response.user);
  return response.user;
}

/**
 * Logout the current user.
 */
export async function logout(): Promise<void> {
  try {
    await post('/api/auth/logout');
  } catch {
    // Logout on client even if server call fails
  }
  clearAuthData();
}

/**
 * Verify the current token and get user data.
 *
 * @returns User data if token is valid, null otherwise
 */
export async function verifyToken(): Promise<User | null> {
  if (!getStoredToken()) return null;

  try {
    const user = await get<User>('/api/auth/verify');
    // Update stored user data
    const token = getStoredToken();
    if (token) {
      storeAuthData(token, user);
    }
    return user;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      clearAuthData();
    }
    return null;
  }
}

/**
 * Get current user profile.
 *
 * @returns User data
 */
export async function getMe(): Promise<User> {
  return get<User>('/api/auth/me');
}

export default {
  register,
  login,
  logout,
  verifyToken,
  getMe,
  getStoredUser,
  getStoredToken,
  isAuthenticated,
};
