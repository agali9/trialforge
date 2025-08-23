import json
import os
import threading
import time
from datetime import datetime, timezone

import requests
from websocket import WebSocket

from trialforge.buffer import LocalBuffer


def _retry_request(method, url, **kwargs):
    delays = [1, 2, 4]
    last_error = None
    for delay in delays:
        try:
            resp = requests.request(method, url, timeout=20, **kwargs)
            if resp.ok:
                return resp
            last_error = RuntimeError(f"{resp.status_code}: {resp.text}")
        except Exception as exc:
            last_error = exc
        time.sleep(delay)
    raise last_error


def init(base_url: str, token: str, experiment_id: str, run_name: str = None, hyperparameters: dict = None) -> "Run":
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"experiment_id": experiment_id, "name": run_name or f"run-{int(time.time())}", "hyperparameters": hyperparameters or {}}
    resp = _retry_request("POST", f"{base_url}/runs", headers=headers, json=payload)
    run_id = resp.json()["id"]
    return Run(base_url=base_url, token=token, run_id=run_id)


class Run:
    def __init__(self, base_url: str, token: str, run_id: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.run_id = run_id
        self.headers = {"Authorization": f"Bearer {token}"}
        self.buffer = []
        self.step = 0
        self.local_buffer = LocalBuffer()
        self.last_flush = time.time()
        self.ws = None
        self._connect_ws()
        self._timer = threading.Timer(2, self._flush_periodic)
        self._timer.daemon = True
        self._timer.start()

    def _ws_url(self):
        no_proto = self.base_url.replace("http://", "").replace("https://", "")
        scheme = "wss" if self.base_url.startswith("https://") else "ws"
        return f"{scheme}://{no_proto}/ws/runs/{self.run_id}?token={self.token}"

    def _connect_ws(self):
        delay = 1
        while delay <= 30:
            try:
                self.ws = WebSocket()
                self.ws.connect(self._ws_url(), timeout=5)
                return
            except Exception:
                time.sleep(delay)
                delay = min(delay * 2, 30)

    def _flush_periodic(self):
        try:
            if self.buffer and (len(self.buffer) >= 50 or (time.time() - self.last_flush) >= 2):
                self._send_buffer()
        finally:
            self._timer = threading.Timer(2, self._flush_periodic)
            self._timer.daemon = True
            self._timer.start()

    def _send_buffer(self):
        batch = self.buffer[:]
        if not batch:
            return
        self.buffer = []
        self.last_flush = time.time()
        try:
            self.ws.send(json.dumps(batch, default=str))
        except Exception:
            payload = {"run_id": self.run_id, "metrics": batch}
            try:
                _retry_request("POST", f"{self.base_url}/metrics/batch", headers=self.headers, json=payload)
            except Exception:
                self.local_buffer.push(payload)
            self._connect_ws()

    def log(self, metrics: dict[str, float], step: int = None):
        if step is None:
            self.step += 1
            step = self.step
        now = datetime.now(timezone.utc).isoformat()
        for name, value in metrics.items():
            self.buffer.append({"name": name, "step": step, "value": float(value), "timestamp": now})
        if len(self.buffer) >= 50:
            self._send_buffer()

    def log_artifact(self, local_path: str, name: str = None):
        artifact_name = name or os.path.basename(local_path)
        size = os.path.getsize(local_path)
        presign = _retry_request(
            "POST",
            f"{self.base_url}/artifacts/presign",
            headers=self.headers,
            json={"run_id": self.run_id, "name": artifact_name, "size_bytes": size},
        ).json()
        with open(local_path, "rb") as f:
            requests.put(presign["url"], data=f, timeout=30)

    def finish(self, status: str = "completed"):
        self._send_buffer()
        _retry_request(
            "PATCH",
            f"{self.base_url}/runs/{self.run_id}",
            headers=self.headers,
            json={"status": status, "finished_at": datetime.now(timezone.utc).isoformat()},
        )


def main():
    print("Use `import trialforge as tf` in your code.")
