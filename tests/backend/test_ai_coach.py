import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ai_coach_review_endpoint_nonexistent_profile():
    # Attempting to review non-synced profile returns 404
    res = client.post("/api/v1/ai-coach/review/non_existent_cf_user_xyz_123")
    assert res.status_code == 404
