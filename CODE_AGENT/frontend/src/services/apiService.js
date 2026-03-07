import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const pipelineService = {
  run: async (userInput, experienceLevel) => {
    try {
      const response = await api.post("/pipeline/run", {
        user_input: userInput,
        experience_level: experienceLevel,
      });
      return response.data;
    } catch (error) {
      if (error.response && error.response.data) {
        return error.response.data;
      }
      throw error;
    }
  },

  generate: async (userInput, level) => {
    const response = await api.post("/generate", {
      user_input: userInput,
      experience_level: level,
    });
    return response.data;
  },

  debug: async (code) => {
    const response = await api.post("/debug", { code_to_debug: code });
    return response.data;
  },

  score: async (code) => {
    const response = await api.post("/score", { code_to_score: code });
    return response.data;
  },

  mermaid: async (code) => {
    const response = await api.post("/mermaid", { code_for_diagram: code });
    return response.data;
  },
};

export default api;
