import axios from "axios";

// Backend exposes routes directly (no /api/v1 prefix)
const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
});

let interceptorId = null;

export const attachSessionInterceptor = (getSessionId) => {
  // Remove previous interceptor if exists
  if (interceptorId !== null) {
    api.interceptors.request.eject(interceptorId);
  }
  
  // Add new interceptor
  interceptorId = api.interceptors.request.use((config) => {
    const sessionId = getSessionId();
    if (sessionId) {
      config.headers["X-Session-ID"] = sessionId;
    }
    return config;
  });
};

export default api;
