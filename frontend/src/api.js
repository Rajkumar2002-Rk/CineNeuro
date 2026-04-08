import axios from "axios";

const baseURL = process.env.NODE_ENV === "production" ? "" : "http://localhost:8000";
const API = axios.create({ baseURL });

export async function uploadTrailer(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await API.post("/api/v1/analyze", formData);
  return response.data;
}

export async function getJobStatus(jobId) {
  const response = await API.get(`/api/v1/status/${jobId}`);
  return response.data;
}

export async function getJobResult(jobId) {
  const response = await API.get(`/api/v1/result/${jobId}`);
  return response.data;
}

export async function getDemos() {
  const response = await API.get("/api/v1/demos");
  return response.data;
}

export async function getDemoResult(trailerName) {
  const response = await API.get(`/api/v1/demo/${trailerName}`);
  return response.data;
}
