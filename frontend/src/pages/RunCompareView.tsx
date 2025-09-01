import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useQueries } from "@tanstack/react-query";
import { getMetrics } from "../api/metrics";
import { getRun } from "../api/runs";
import MetricChart from "../components/MetricChart";

export default function RunCompareView() {
  const [params] = useSearchParams();
  const runIds = (params.get("runs") || "").split(",").filter(Boolean);
  const runQueries = useQueries({ queries: runIds.map((id) => ({ queryKey: ["run", id], queryFn: () => getRun(id) })) });
  const metricQueries = useQueries({ queries: runIds.map((id) => ({ queryKey: ["metrics", id], queryFn: () => getMetrics(id, true) })) });

  const metricNames = useMemo(() => {
    const set = new Set<string>();
    metricQueries.forEach((q) => (q.data || []).forEach((m: any) => set.add(m.metric_name)));
    return [...set];
  }, [metricQueries]);
  const runs = runQueries.map((q) => q.data).filter(Boolean) as any[];
  const hyperparameterKeys = useMemo(() => {
    const allKeys = new Set<string>();
    runs.forEach((run) => Object.keys(run.hyperparameters || {}).forEach((key) => allKeys.add(key)));
    return [...allKeys].sort();
  }, [runs]);
  const hasLoading = [...runQueries, ...metricQueries].some((q) => q.isLoading);

  return (
    <div>
      <h1 className="text-2xl mb-4">Compare Runs</h1>
      {hasLoading && (
        <div className="mb-4 flex items-center gap-2 text-sm text-[var(--color-muted)]">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-muted)] border-t-transparent" />
          Loading compare data...
        </div>
      )}
      {runs.length > 0 && (
        <div className="mb-5 overflow-x-auto rounded border border-[var(--color-border)] bg-[var(--color-surface)]">
          <table className="w-full table-auto border-collapse">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                <th className="px-3 py-2 text-left">Hyperparameter</th>
                {runs.map((run) => (
                  <th key={run.id} className="px-3 py-2 text-left">
                    {run.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {hyperparameterKeys.map((key) => {
                const values = runs.map((run) => run.hyperparameters?.[key] ?? "-");
                const baseline = String(values[0]);
                const differs = values.some((value) => String(value) !== baseline);
                return (
                  <tr key={key} className="border-b border-[var(--color-border)]">
                    <td className="px-3 py-2 text-sm text-[var(--color-muted)]">{key}</td>
                    {values.map((value, idx) => (
                      <td key={`${key}-${runs[idx].id}`} className={`px-3 py-2 text-sm ${differs ? "bg-amber-500/20" : ""}`}>
                        {String(value)}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {metricNames.map((metric) => {
        const series = metricQueries
          .map((q, i) => ({ run: runQueries[i].data, data: (q.data || []).find((m: any) => m.metric_name === metric) }))
          .filter((x) => x.data);
        if (!series.length) return null;
        return (
          <div key={metric} className="mb-4 border border-[var(--color-border)] p-3 bg-[var(--color-surface)]">
            <h2>{metric}</h2>
            <MetricChart
              metricName={metric}
              data={[
                series[0].data.points.map((p: any) => p.step),
                ...series.map((s) => s.data.points.map((p: any) => p.value)),
              ]}
            />
          </div>
        );
      })}
    </div>
  );
}
