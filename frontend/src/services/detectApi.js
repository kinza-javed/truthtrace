import axios from "axios";

const API = "http://127.0.0.1:8000";

const detectImage = async (file) => {
  const user = JSON.parse(localStorage.getItem("user"));

  const settings = JSON.parse(localStorage.getItem("detectionSettings")) || {
    allowMultipleFaces: true,
    enableReportGeneration: true,
  };

  const formData = new FormData();
  formData.append("file", file);

  if (user?.id) {
    formData.append("user_id", user.id);
  }

  formData.append("allow_multiple_faces", settings.allowMultipleFaces);
  formData.append("enable_report_generation", settings.enableReportGeneration);

  const res = await axios.post(`${API}/predict`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return res.data;
};

export default detectImage;