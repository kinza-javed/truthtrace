import axios from "axios";

const API = "http://127.0.0.1:8000";

export const getUserHistory = async (userId) => {
  const res = await axios.get(`${API}/api/history/${userId}`);
  return res.data;
};