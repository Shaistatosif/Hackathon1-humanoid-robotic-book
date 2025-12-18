/**
 * API client service with fetch wrapper.
 *
 * Provides a typed HTTP client for communicating with the backend API.
 */

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 5000; // 5 second timeout

/**
 * HTTP error response from the API.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Timeout error when API doesn't respond.
 */
export class TimeoutError extends Error {
  constructor(message = 'Request timed out - backend may be unavailable') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Options for API requests.
 */
interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

/**
 * Get the stored authentication token.
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Make an API request with automatic JSON handling and auth headers.
 *
 * @param endpoint - API endpoint path (e.g., '/api/auth/login')
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws ApiError on non-2xx responses
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, headers: customHeaders, ...restOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(customHeaders as Record<string, string>),
  };

  // Add auth token if available
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  const config: RequestInit = {
    ...restOptions,
    headers,
    signal: controller.signal,
  };

  if (body !== undefined) {
    config.body = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, config);
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new TimeoutError();
    }
    throw new TimeoutError('Network error - backend may be unavailable');
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    let errorMessage: string;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || response.statusText;
    } catch {
      errorMessage = response.statusText;
    }
    throw new ApiError(response.status, response.statusText, errorMessage);
  }

  // Handle empty responses
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }

  return {} as T;
}

/**
 * GET request helper.
 */
export function get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  return apiRequest<T>(endpoint, { ...options, method: 'GET' });
}

/**
 * POST request helper.
 */
export function post<T>(
  endpoint: string,
  body?: unknown,
  options?: RequestOptions
): Promise<T> {
  return apiRequest<T>(endpoint, { ...options, method: 'POST', body });
}

/**
 * PUT request helper.
 */
export function put<T>(
  endpoint: string,
  body?: unknown,
  options?: RequestOptions
): Promise<T> {
  return apiRequest<T>(endpoint, { ...options, method: 'PUT', body });
}

/**
 * DELETE request helper.
 */
export function del<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  return apiRequest<T>(endpoint, { ...options, method: 'DELETE' });
}

/**
 * PATCH request helper.
 */
export function patch<T>(
  endpoint: string,
  body?: unknown,
  options?: RequestOptions
): Promise<T> {
  return apiRequest<T>(endpoint, { ...options, method: 'PATCH', body });
}

export default {
  get,
  post,
  put,
  del,
  patch,
  request: apiRequest,
};
