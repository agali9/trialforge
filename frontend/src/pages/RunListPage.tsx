import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createExperiment, listExperiments } from "../api/experiments";
import { listRuns } from "../api/runs";
import { useAuth } from "../auth/AuthContext";

export default function RunListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [selectedExperiment, setSelectedExperiment] = useState("");
  const [filter, setFilter] = useState("");
  const [selectedRuns, setSelectedRuns] = useState<string[]>([]);
  const [showNewExperiment, setShowNewExperiment] = useState(false);
  const [newExperimentName, setNewExperimentName] = useState("");
  const experiments = useQuery({ queryKey: ["experiments"], queryFn: listExperiments });
  const runs = useQuery({ queryKey: ["runs", selectedExperiment], queryFn: () => listRuns(selectedExperiment), enabled: !!selectedExperiment });
  const createExperimentMutation = useMutation({
    mutationFn: (name: string) => createExperiment({ name }),
    onSuccess: async (created) => {
      await queryClient.invalidateQueries({ queryKey: ["experiments"] });
      setSelectedExperiment(created.id);
      setShowNewExperiment(false);
      setNewExperimentName("");
    },
  });

  const filtered = useMemo(
    () => (runs.data || []).filter((r: any) => r.name.toLowerCase().includes(filter.toLowerCase())),
    [runs.data, filter],
  );
  const statusClass = (status: string) => {
    if (status === "running") return "bg-teal-500";
    if (status === "completed") return "bg-green-600";
    if (status === "failed") return "bg-red-600";
    return "bg-gray-600";
  };

  return (
    <div>
      <p className="text-sm text-[var(--color-muted)] mb-2">Workspace: {user?.workspace_name || "Unknown Workspace"}</p>
      <h1 className="text-2xl mb-3">Runs</h1>

      <div className="mb-4 flex items-center gap-2">
        <button className="rounded bg-[var(--color-accent)] px-3 py-2 text-sm font-medium text-white" onClick={() => setShowNewExperiment((v) => !v)}>
          New Experiment
        </button>
      </div>
      {showNewExperiment && (
        <form
          className="mb-4 flex max-w-md items-center gap-2 rounded border border-[var(--color-border)] bg-[var(--color-surface)] p-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (!newExperimentName.trim()) return;
            createExperimentMutation.mutate(newExperimentName.trim());
          }}
        >
          <input
            className="w-full rounded border border-[var(--color-border)] bg-transparent p-2"
            placeholder="Experiment name"
            value={newExperimentName}
            onChange={(e) => setNewExperimentName(e.target.value)}
          />
          <button className="rounded bg-[var(--color-accent)] px-3 py-2 text-sm text-white">Create</button>
        </form>
      )}

      <select value={selectedExperiment} onChange={(e) => setSelectedExperiment(e.target.value)} className="mb-4 p-2 bg-[var(--color-surface)] border border-[var(--color-border)]">
        <option value="">Select experiment</option>
        {(experiments.data || []).map((e: any) => (
          <option key={e.id} value={e.id}>
            {e.name}
          </option>
        ))}
      </select>
      <input className="ml-2 p-2 bg-[var(--color-surface)] border border-[var(--color-border)]" placeholder="Filter run name" value={filter} onChange={(e) => setFilter(e.target.value)} />

      {experiments.isLoading && (
        <div className="mt-4 flex items-center gap-2 text-sm text-[var(--color-muted)]">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-muted)] border-t-transparent" />
          Loading experiments...
        </div>
      )}
      {!experiments.isLoading && (experiments.data || []).length === 0 && (
        <p className="mt-4 text-[var(--color-muted)]">No experiments yet — create one above</p>
      )}

      <table className="w-full mt-4 table-fixed border-collapse">
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            <th className="w-12" />
            <th className="w-[36%] text-left py-2">Name</th>
            <th className="w-[12%] text-left py-2">Status</th>
            <th className="w-[20%] text-left py-2">Started At</th>
            <th className="w-[32%] text-left py-2">Hyperparameters</th>
          </tr>
        </thead>
        <tbody>
          {runs.isLoading && selectedExperiment && (
            <tr>
              <td colSpan={5} className="py-8">
                <div className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-muted)] border-t-transparent" />
                  Loading runs...
                </div>
              </td>
            </tr>
          )}
          {!runs.isLoading && selectedExperiment && filtered.length === 0 && (
            <tr>
              <td colSpan={5} className="py-8 text-[var(--color-muted)]">
                No runs yet for this experiment.
              </td>
            </tr>
          )}
          {filtered.map((run: any) => (
            <tr key={run.id} className="border-b border-[var(--color-border)] hover:bg-[var(--color-surface)] cursor-pointer" onClick={() => navigate(`/runs/${run.id}`)}>
              <td onClick={(e) => e.stopPropagation()}>
                <input
                  type="checkbox"
                  checked={selectedRuns.includes(run.id)}
                  onChange={(e) =>
                    setSelectedRuns((prev) => (e.target.checked ? [...prev, run.id] : prev.filter((id) => id !== run.id)))
                  }
                />
              </td>
              <td className="truncate pr-3">{run.name}</td>
              <td>
                <span className={`inline-block rounded px-2 py-1 text-xs font-medium text-white ${statusClass(run.status)}`}>{run.status}</span>
              </td>
              <td className="font-mono">{new Date(run.started_at).toLocaleString()}</td>
              <td>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(run.hyperparameters || {}).map(([key, value]) => (
                    <span key={key} className="rounded-full border border-[var(--color-border)] px-2 py-1 text-xs text-[var(--color-text)]">
                      {key}: {String(value)}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedRuns.length >= 2 && (
        <div className="sticky bottom-0 mt-4 p-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">
          <button className="bg-[var(--color-accent)] text-white px-4 py-2 rounded" onClick={() => navigate(`/compare?runs=${selectedRuns.join(",")}`)}>
            Compare {selectedRuns.length} runs →
          </button>
        </div>
      )}
    </div>
  );
}
