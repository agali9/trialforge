import pytest

pytestmark = pytest.mark.asyncio


async def test_batch_ingest_writes_metrics(async_client, test_user):
    headers = {"Authorization": f"Bearer {test_user}"}
    exp = await async_client.post("/experiments", headers=headers, json={"name": "Exp3"})
    run = await async_client.post("/runs", headers=headers, json={"experiment_id": exp.json()["id"], "name": "Run 3"})
    payload = {"run_id": run.json()["id"], "metrics": [{"name": "loss", "step": 1, "value": 0.5}]}
    resp = await async_client.post("/metrics/batch", headers=headers, json=payload)
    assert resp.status_code == 200