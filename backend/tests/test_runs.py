import pytest

pytestmark = pytest.mark.asyncio


async def test_create_run(async_client, test_user):
    headers = {"Authorization": f"Bearer {test_user}"}
    exp = await async_client.post("/experiments", headers=headers, json={"name": "Exp"})
    run = await async_client.post("/runs", headers=headers, json={"experiment_id": exp.json()["id"], "name": "Run 1"})
    assert run.status_code == 200


async def test_update_run_status(async_client, test_user):
    headers = {"Authorization": f"Bearer {test_user}"}
    exp = await async_client.post("/experiments", headers=headers, json={"name": "Exp2"})
    run = await async_client.post("/runs", headers=headers, json={"experiment_id": exp.json()["id"], "name": "Run 2"})
    updated = await async_client.patch(f"/runs/{run.json()['id']}", headers=headers, json={"status": "completed"})
    assert updated.status_code == 200