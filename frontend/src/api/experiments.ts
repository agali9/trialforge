import api from "./client";

export const listExperiments = async () => (await api.get("/experiments")).data;
export const createExperiment = async (payload: { name: string; description?: string }) => (await api.post("/experiments", payload)).data;
export const getExperiment = async (id: string) => (await api.get(`/experiments/${id}`)).data;
