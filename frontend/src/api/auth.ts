import api from "./client";

export const loginApi = async (email: string, password: string) => {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);
  const { data } = await api.post("/auth/token", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
};

export const registerApi = async (payload: { email: string; password: string; workspace_name: string; workspace_slug: string }) =>
  (await api.post("/auth/register", payload)).data;

export const getMeApi = async () => (await api.get("/auth/me")).data;
