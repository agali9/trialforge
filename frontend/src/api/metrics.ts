import api from "./client";

export const getMetrics = async (runId: string, downsample = true) => (await api.get(`/metrics/${runId}`, { params: { downsample } })).data;
export const getMetricNames = async (runId: string) => (await api.get(`/metrics/${runId}/names`)).data;
