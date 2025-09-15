import math
import os
import random
import time

import trialforge as tf


BASE_URL = os.getenv("TRIALFORGE_BASE_URL", "https://trialforge.onrender.com")
TOKEN = os.environ["TRIALFORGE_TOKEN"]
EXPERIMENT_ID = os.environ["TRIALFORGE_EXPERIMENT_ID"]


def train_one_epoch(epoch: int) -> tuple[float, float]:
    loss = math.exp(-epoch / 8) + random.uniform(0.0, 0.03)
    accuracy = min(0.99, 0.55 + epoch * 0.035 + random.uniform(0.0, 0.02))
    time.sleep(0.25)
    return loss, accuracy


def main() -> None:
    run = tf.init(
        base_url=BASE_URL,
        token=TOKEN,
        experiment_id=EXPERIMENT_ID,
        run_name="example-training-run",
        hyperparameters={
            "learning_rate": 0.01,
            "batch_size": 32,
            "epochs": 12,
        },
    )

    try:
        for epoch in range(1, 13):
            loss, accuracy = train_one_epoch(epoch)
            run.log({"loss": loss, "accuracy": accuracy}, step=epoch)
            print(f"epoch={epoch:02d} loss={loss:.4f} accuracy={accuracy:.4f}")
        run.finish("completed")
    except Exception:
        run.finish("failed")
        raise

    print(f"Created TrialForge run: {run.run_id}")


if __name__ == "__main__":
    main()
