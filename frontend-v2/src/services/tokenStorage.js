/**
 * Centralized Token Storage Abstraction
 * 
 * Environment-aware storage:
 * - DEV: sessionStorage (tab-isolated for testing multiple users)
 * - PROD: localStorage (single user per browser)
 * 
 * All token reads/writes MUST go through this utility.
 * No component should directly access localStorage or sessionStorage.
 */

const isDev = import.meta.env.DEV || import.meta.env.MODE === 'development';

// Select storage based on environment
const storage = isDev ? sessionStorage : localStorage;

const tokenStorage = {
  /**
   * Get a value from token storage
   * @param {string} key - The key to retrieve
   * @returns {string|null} - The stored value or null
   */
  get: (key) => {
    return storage.getItem(key);
  },

  /**
   * Set a value in token storage
   * @param {string} key - The key to store
   * @param {string} value - The value to store
   */
  set: (key, value) => {
    storage.setItem(key, value);
  },

  /**
   * Remove a value from token storage
   * @param {string} key - The key to remove
   */
  remove: (key) => {
    storage.removeItem(key);
  }
};

export default tokenStorage;
