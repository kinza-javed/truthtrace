import axios from "axios";

const API = "http://127.0.0.1:8000";

// 🔐 SIGNUP
export const signupUser = async (userData) => {
  const res = await axios.post(`${API}/auth/signup`, userData);
  return res.data;
};

// 🔐 LOGIN
export const loginUser = async (userData) => {
  const res = await axios.post(`${API}/auth/login`, userData);
  return res.data;
};

// 🔐 FORGOT PASSWORD
export const forgotPassword = async (data) => {
  const res = await axios.post(`${API}/auth/forgot-password`, data);
  return res.data;
};

// 🔐 RESET PASSWORD
export const resetPassword = async (data) => {
  const res = await axios.post(`${API}/auth/reset-password`, data);
  return res.data;
};

// 🔐 VERIFY EMAIL
export const verifyEmail = async (token) => {
  const res = await axios.get(`${API}/auth/verify-email?token=${token}`);
  return res.data;
};