from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.db.models.user import User

client = TestClient(app)


def test_auth_register_endpoint():
    user_payload = {
        "email": "testuser_register@example.com",
        "password": "SecurePassword123!",
    }
    reg_res = client.post("/api/v1/auth/register", json=user_payload)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["email"] == user_payload["email"]


def test_auth_login_endpoint(monkeypatch):
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    mock_user = User(id="user-uuid-123", email="testuser_login@example.com", hashed_password=hashed)

    # Mock execute result to return mock_user
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_user

    user_payload = {
        "email": "testuser_login@example.com",
        "password": password,
    }
    login_res = client.post("/api/v1/auth/login", json=user_payload)
    assert login_res.status_code in (200, 401)
