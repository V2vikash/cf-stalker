from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.v1.endpoints.cf_profile.sync_user_profile_task")
def test_cf_profile_sync_trigger_and_status_polling(mock_sync_task):
    mock_sync_task.return_value = {"status": "success", "handle": "tourist"}
    handle = "tourist"
    
    # Trigger profile sync
    sync_res = client.post(f"/api/v1/cf/profile/{handle}")
    assert sync_res.status_code == 200
    sync_data = sync_res.json()
    assert sync_data["handle"] == handle
    assert "sync_job_id" in sync_data
    assert sync_data["status"] in ("PENDING", "RUNNING", "COMPLETED")

    job_id = sync_data["sync_job_id"]

    # Poll status
    status_res = client.get(f"/api/v1/cf/sync-status/{job_id}")
    assert status_res.status_code in (200, 404)
