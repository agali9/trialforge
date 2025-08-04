# TrialForge — self-hosted ML experiment tracking

TrialForge is a self-hosted platform for tracking ML runs, metrics, and artifacts.

## Quickstart

```bash
git clone <your-repo-url>
cd trialforge
docker compose up --build
# Open http://localhost
```

## Python client

```python
import trialforge as tf
run = tf.init(base_url="http://localhost:8000", token="...", experiment_id="...")
run.log({"loss": 0.42, "acc": 0.91}, step=1)
run.log_artifact("model.pt")
run.finish()
```

## Architecture

Client -> FastAPI -> TimescaleDB / Redis / MinIO <- React Dashboard

## TestPyPI

See [TestPyPI docs](https://test.pypi.org/) for token and install instructions.
