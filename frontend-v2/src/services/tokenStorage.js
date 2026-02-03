/**
 * Centralized Token Storage
 *
 * DEV  -> sessionStorage (separate login per tab, great for testing drivers)
 * PROD -> localStorage   (persistent login for real users)
 *
 * IMPORTANT:
 * Always use ONE static key (ex: "jwt_token")
 * Never use dynamic keys or prefixes.
 */

const storage =
  import.meta.env.DEV ? sessionStorage : localStorage;

const tokenStorage = {
  /**
   * Get value
   */
  get(key) {
    return storage.getItem(key);
  },

  /**
   * Set value
   */
  set(key, value) {
    storage.setItem(key, value);
  },

  /**
   * Remove value
   */
  remove(key) {
    storage.removeItem(key);
  },

  /**
   * Clear all auth (optional helper)
   */
  clear() {
    storage.clear();
  }
};

export default tokenStorage;
