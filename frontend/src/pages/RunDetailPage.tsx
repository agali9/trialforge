import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getExperiment } from "../api/experiments";
import { getMetrics } from "../api/metrics";
import { getRun, updateRun } from "../api/runs";
import MetricChart from "../components/MetricChart";

export default function RunDetailPage() {
  const { id = "" } = useParams();
  const run = useQuery({ queryKey: ["run", id], queryFn: () => getRun(id) });
  const metrics = useQuery({ queryKey: ["metrics", id], queryFn: () => getMetrics(id, true) });
  const experiment = useQuery({
    queryKey: ["experiment", run.data?.experiment_id],
    queryFn: () => getExperiment(run.data.experiment_id),
    enabled: !!run.data?.experiment_id,
  });
  const [live, setLive] = useState(false);

  useEffect(() => {
    if (!id || run.data?.status !== "running") return;
    const token = localStorage.getItem("token");
    if (!token) return;
    const apiBase = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.host}/api`;
    const wsBase = apiBase.replace(/^http/, "ws").replace(/\/api\/?$/, "");
    const ws = new WebSocket(`${wsBase}/ws/runs/${id}?token=${token}`);
    ws.onopen = () => setLive(true);
    ws.onclose = () => setLive(false);
    return () => ws.close();
  }, [id, run.data?.status]);

  return (
    <div className="grid grid-cols-[280px_1fr] gap-4">
      <aside className="bg-[var(--color-surface)] border border-[var(--color-border)] p-3">
        <div className="mb-3 text-sm text-[var(--color-muted)]">
          <Link to="/experiments" className="text-[var(--color-accent)] hover:underline">
            Experiments
          </Link>
          {" > "}
          <span>{experiment.data?.name || "..."}</span>
          {" > "}
          <span>{run.data?.name || "..."}</span>
        </div>
        <h2 className="text-xl">{run.data?.name}</h2>
        <div className="my-2">Status: {run.data?.status} {live && <span className="text-green-400">LIVE</span>}</div>
        <div className="mb-3">
          <h3 className="mb-1 text-sm font-semibold">Hyperparameters</h3>
          {Object.entries(run.data?.hyperparameters || {}).length === 0 ? (
            <p className="text-sm text-[var(--color-muted)]">No hyperparameters</p>
          ) : (
            <div className="space-y-1 text-sm">
              {Object.entries(run.data?.hyperparameters || {}).map(([key, value]) => (
                <div key={key} className="flex justify-between gap-2 border-b border-[var(--color-border)] pb-1">
                  <span className="text-[var(--color-muted)]">{key}</span>
                  <span>{String(value)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <textarea
          className="w-full bg-transparent border border-[var(--color-border)] p-2"
          defaultValue={run.data?.notes || ""}
          onChange={(e) => {
            const val = e.target.value;
            setTimeout(() => updateRun(id, { notes: val }), 500);
          }}
        />
      </aside>
      <main>
        {(run.isLoading || metrics.isLoading) && (
          <div className="mb-4 flex items-center gap-2 text-sm text-[var(--color-muted)]">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-muted)] border-t-transparent" />
            Loading run details...
          </div>
        )}
        {(metrics.data || []).map((m: any) => (
          <div key={m.metric_name} className="mb-4 bg-[var(--color-surface)] p-3 border border-[var(--color-border)]">
            <MetricChart metricName={m.metric_name} data={[m.points.map((p: any) => p.step), m.points.map((p: any) => p.value)]} />
          </div>
        ))}
      </main>
    </div>
  );
}
