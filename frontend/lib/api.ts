import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("sb_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("sb_token");
      localStorage.removeItem("sb_user");
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  register: (data: object) => api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
  updateMe: (data: object) => api.put("/auth/me", data),
};

export const resumeApi = {
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/resume/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 60000,
    });
  },
  latest: () => api.get("/resume/latest"),
  history: () => api.get("/resume/history"),
  ragChat: (question: string) => api.post("/phase3/resume/rag-chat", { question }),
};

export const roadmapApi = {
  generate: (goal: string, current_skills?: string[]) =>
    api.post("/roadmap/generate", { goal, current_skills }),
  list: () => api.get("/roadmap/"),
  updateProgress: (id: string, node_id: string, completed: boolean) =>
    api.put(`/roadmap/${id}/progress`, { node_id, completed }),
};

export const projectsApi = {
  recommend: (data: object) => api.post("/projects/recommend", data),
};

export const githubApi = {
  analyze: (github_username: string) =>
    api.post("/github/analyze", { github_username }),
  history: () => api.get("/github/history"),
};

export const interviewApi = {
  getQuestion: (topic: string, difficulty?: string) =>
    api.post("/interview/question", { topic, difficulty }),
  evaluate: (session_id: string, answer: string) =>
    api.post("/interview/evaluate", { session_id, answer }),
  history: () => api.get("/interview/history"),
};

export const trackerApi = {
  getAll: () => api.get("/tracker/"),
  add: (data: object) => api.post("/tracker/", data),
  update: (id: string, data: object) => api.put(`/tracker/${id}`, data),
};

export const jobsApi = {
  match: (data: object) => api.post("/jobs/match", data),
};

export const phase3Api = {
  reviewPortfolio: (portfolio_url: string) =>
    api.post("/phase3/portfolio/review", { portfolio_url }),
  generateCoverLetter: (data: { target_role: string; company_name: string; job_description?: string }) =>
    api.post("/phase3/tools/cover-letter", data),
  generateLinkedInPost: (data: { project_title: string; tech_stack: string[]; key_features?: string }) =>
    api.post("/phase3/tools/linkedin-post", data),
};

export const streamChat = async (
  content: string,
  session_id: string | null,
  onChunk: (chunk: string) => void,
  onDone: (sid: string) => void
) => {
  const token = localStorage.getItem("sb_token");
  const res = await fetch(`${API_URL}/chat/send`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content, session_id }),
  });

  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sid = session_id || "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "chunk") onChunk(data.content);
          else if (data.type === "session_id") sid = data.session_id;
          else if (data.type === "done") onDone(sid);
        } catch {}
      }
    }
  }
};
