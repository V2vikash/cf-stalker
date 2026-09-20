import uuid
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.core.database import get_db


@pytest.fixture(autouse=True)
def override_db_dependency():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.flush = AsyncMock()
    
    async def mock_refresh(instance):
        if not getattr(instance, "id", None):
            instance.id = str(uuid.uuid4())
        if hasattr(instance, "is_active") and getattr(instance, "is_active", None) is None:
            instance.is_active = True
        if hasattr(instance, "created_at") and getattr(instance, "created_at", None) is None:
            instance.created_at = datetime.utcnow()
        return None
        
    mock_session.refresh = AsyncMock(side_effect=mock_refresh)

    # Default execute mock return
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalars.return_value.first.return_value = None
    mock_result.first.return_value = None
    mock_result.scalar.return_value = 1
    mock_session.execute.return_value = mock_result

    async def _get_test_db():
        yield mock_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()
