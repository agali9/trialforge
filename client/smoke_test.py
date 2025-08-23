import random
import time

import requests
import trialforge as tf

BASE_URL = "http://localhost:8000"
EMAIL = f"smoke{int(time.time())}@example.com"
PASSWORD = "Password123!"


def main():
    reg = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "workspace_name": "Smoke Workspace", "workspace_slug": f"smoke-{int(time.time())}"},
        timeout=20,
    )
    reg.raise_for_status()

    token_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": EMAIL, "password": PASSWORD}, timeout=20)
    token_resp.raise_for_status()
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    exp = requests.post(f"{BASE_URL}/experiments", headers=headers, json={"name": "Smoke Experiment", "description": "smoke"}, timeout=20)
    exp.raise_for_status()
    exp_id = exp.json()["id"]

    run = tf.init(base_url=BASE_URL, token=token, experiment_id=exp_id, run_name="smoke-run", hyperparameters={"lr": 0.01})
    for i in range(1, 101):
        run.log({"loss": 1 / (i + 1) + random.random() * 0.01, "acc": min(0.99, 0.5 + i * 0.005)}, step=i)
    run.finish()
    print("Smoke test passed")


if __name__ == "__main__":
    main()
