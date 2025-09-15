export default function HowItWorksPage() {
  return (
    <div className="max-w-4xl">
      <p className="mb-2 text-sm text-[var(--color-muted)]">Workspace-scoped experiment tracking</p>
      <h1 className="mb-6 text-2xl font-semibold">How TrialForge Works</h1>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Run Creation Flow</h2>
        <ol className="space-y-3 text-sm leading-6 text-[var(--color-text)]">
          <li className="border-l-2 border-[var(--color-accent)] pl-3">
            Log in on the website. Registration creates an account, a workspace, and a JWT. The token stores your user id and workspace id.
          </li>
          <li className="border-l-2 border-[var(--color-border)] pl-3">
            Create an experiment in the UI. That experiment is stored under your workspace.
          </li>
          <li className="border-l-2 border-[var(--color-border)] pl-3">
            Copy the experiment id and your token into a training script.
          </li>
          <li className="border-l-2 border-[var(--color-border)] pl-3">
            The script calls <code className="rounded bg-black/30 px-1">tf.init(...)</code>, which sends <code className="rounded bg-black/30 px-1">POST /runs</code> with the token and experiment id.
          </li>
          <li className="border-l-2 border-[var(--color-border)] pl-3">
            The backend verifies that the experiment belongs to the workspace in the token, then inserts the run.
          </li>
          <li className="border-l-2 border-[var(--color-border)] pl-3">
            The website lists runs with <code className="rounded bg-black/30 px-1">GET /runs/experiment/:id</code>, filtered to your workspace.
          </li>
        </ol>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Ownership Model</h2>
        <p className="mb-3 text-sm leading-6 text-[var(--color-text)]">
          Runs do not store a user id directly. Ownership is chained through the workspace.
        </p>
        <pre className="overflow-x-auto rounded border border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-sm">
{`user.workspace_id
  -> experiment.workspace_id
    -> run.experiment_id`}
        </pre>
        <p className="mt-3 text-sm leading-6 text-[var(--color-muted)]">
          Each registration creates one workspace and an owner user. Because there is no invite flow, each account effectively sees only the experiments and runs created with that account's token.
        </p>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Training Script Setup</h2>
        <div className="space-y-3 text-sm leading-6 text-[var(--color-text)]">
          <p>Copy your token from the login response and copy the experiment id from the experiment you created.</p>
          <pre className="overflow-x-auto rounded border border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-sm">
{`set TRIALFORGE_TOKEN=your-token
set TRIALFORGE_EXPERIMENT_ID=your-experiment-id
python examples/train_with_trialforge.py`}
          </pre>
          <p className="text-[var(--color-muted)]">There is no background detector. Your script creates the run intentionally when it calls the client.</p>
        </div>
      </section>
    </div>
  );
}
