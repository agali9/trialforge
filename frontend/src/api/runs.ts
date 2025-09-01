import api from "./client";

export const listRuns = async (experimentId: string) => (await api.get(`/runs/experiment/${experimentId}`)).data;
export const createRun = async (payload: { experiment_id: string; name: string; hyperparameters?: Record<string, unknown> }) =>
  (await api.post("/runs", payload)).data;
export const updateRun = async (id: string, payload: Record<string, unknown>) => (await api.patch(`/runs/${id}`, payload)).data;
export const getRun = async (id: string) => (await api.get(`/runs/${id}`)).data;
