import axios from "axios";

const API = "http://127.0.0.1:8000";

export const getReviewCase = async (analysisId, reviewerUserId) => {
  const response = await axios.get(`${API}/api/reviews/${analysisId}`, {
    params: { reviewer_user_id: reviewerUserId },
  });
  return response.data;
};

export const investigateReviewCase = async (analysisId, payload) => {
  const response = await axios.post(
    `${API}/api/reviews/${analysisId}/investigate`,
    payload
  );
  return response.data;
};

export const recordReviewVerdict = async (analysisId, payload) => {
  const response = await axios.post(
    `${API}/api/reviews/${analysisId}/verdict`,
    payload
  );
  return response.data;
};

export const markReviewHighImpact = async (analysisId, payload) => {
  const response = await axios.post(
    `${API}/api/reviews/${analysisId}/high-impact`,
    payload
  );
  return response.data;
};
