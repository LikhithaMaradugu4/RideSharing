/**
 * Rating Service — API helpers for trip ratings and feedback.
 */
import authService from './auth.service';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const buildHeaders = (token) => ({
  'Content-Type': 'application/json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
});

const getValidToken = async () => {
  return await authService.getValidToken();
};

const handleResponse = async (response, defaultMessage) => {
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new Error('Invalid response from server');
  }
  if (!response.ok) {
    const message = data?.detail || defaultMessage || 'Request failed';
    const error = new Error(message);
    error.status = response.status;
    error.body = data;
    throw error;
  }
  return data;
};

const ratingService = {
  /**
   * Submit a rating for a trip.
   * @param {number} tripId
   * @param {number} rating  1–5
   * @param {string|null} feedback  optional text
   */
  submitRating: async (tripId, rating, feedback = null) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/rate`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ rating, feedback: feedback || null }),
    });
    return handleResponse(response, 'Failed to submit rating');
  },

  /**
   * Check if current user can rate a trip.
   * @param {number} tripId
   */
  getRatingStatus: async (tripId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/rating-status`, {
      method: 'GET',
      headers: buildHeaders(token),
    });
    return handleResponse(response, 'Failed to check rating status');
  },

  /**
   * Get rating summary for a user.
   * @param {number|string} userId  or "me"
   */
  getRatingSummary: async (userId = 'me') => {
    const token = await getValidToken();
    const url = userId === 'me'
      ? `${API_BASE_URL}/users/me/rating-summary`
      : `${API_BASE_URL}/users/${userId}/rating-summary`;
    const response = await fetch(url, {
      method: 'GET',
      headers: buildHeaders(token),
    });
    return handleResponse(response, 'Failed to fetch rating summary');
  },

  /**
   * Get paginated feedback list for a user.
   * @param {number|string} userId  or "me"
   * @param {number} page
   * @param {number} limit
   */
  getFeedbackList: async (userId = 'me', page = 1, limit = 10) => {
    const token = await getValidToken();
    const url = userId === 'me'
      ? `${API_BASE_URL}/users/me/feedback?page=${page}&limit=${limit}`
      : `${API_BASE_URL}/users/${userId}/feedback?page=${page}&limit=${limit}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: buildHeaders(token),
    });
    return handleResponse(response, 'Failed to fetch feedback');
  },
};

export default ratingService;
