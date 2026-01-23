import axios from "axios";

const authApi = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
});

export const loginApi = async (payload) => {
  const res = await authApi.post("/auth/login", payload);
  return res.data;
};
