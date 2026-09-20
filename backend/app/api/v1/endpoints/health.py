from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import settings

router = APIRouter()


@router.get("", status_code=200)
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    health_status = {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "unknown",
        "redis": "disabled" if not settings.REDIS_URL else "unknown",
    }

    # Check Database
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            health_status["database"] = "connected"
        else:
            health_status["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis (if configured)
    if settings.REDIS_URL:
        try:
            r = await get_redis()
            if r and await r.ping():
                health_status["redis"] = "connected"
            else:
                health_status["redis"] = "unreachable"
        except Exception as e:
            health_status["redis"] = f"error: {str(e)}"

    return health_status
