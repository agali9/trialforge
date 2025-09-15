# TrialForge

TrialForge tracks ML training runs, metrics, and artifacts. Use the deployed app, then log runs from a Python training script with your account token and an experiment id.

**Live app:** https://trialforge.agali9.workers.dev/

Runs are not detected automatically. A run appears only after your script calls the client.

## Using the website

Open the live app. Unauthenticated visits go to the login page.

1. **Register or sign in.** Registration creates an account and a workspace. The nav bar shows your email and workspace name.
2. **Create an experiment.** On the Runs page, click **New Experiment**, enter a name, and create it. Select that experiment from the dropdown. The experiment id is what the training script must use.
3. **Log a run from code.** Copy your JWT (stored in the browser as `token` after login) and the experiment id into the script. See [Logging a run](#logging-a-run).
4. **Open a run.** After the script creates it, refresh the Runs page, select the experiment, and click the row. The detail page shows status, hyperparameters, notes, and metric charts. A **LIVE** badge appears while the run status is `running`.
5. **Compare runs.** Check two or more rows, then click **Compare**. Differing hyperparameters are highlighted, and metrics are overlaid on the same charts.
6. **How it works.** The nav link explains how a token, workspace, experiment, and run are connected.

Logout is in the top right. **TrialForge** in the nav returns to the Runs page.

## Logging a run

Install the client from this repo, then point it at the deployed API:

```bash
pip install -e client
```

```python
import trialforge as tf

run = tf.init(
    base_url="https://trialforge.onrender.com",
    token="...",
    experiment_id="...",
    hyperparameters={"learning_rate": 0.01},
)
run.log({"loss": 0.42, "accuracy": 0.91}, step=1)
run.finish()
```

`tf.init` creates the run under that experiment if the experiment belongs to the workspace in the token. Later `log` calls attach metrics to that run. `finish` marks it completed.

An example script is in `client/examples/train_with_trialforge.py`:

```bash
set TRIALFORGE_TOKEN=your-token
set TRIALFORGE_EXPERIMENT_ID=your-experiment-id
python client/examples/train_with_trialforge.py
```

## Run locally

Not required to use the deployed app. Use this only if you want to run the stack yourself.

```bash
docker compose up --build
```

Then open http://localhost. The local API is `http://localhost:8000`.
