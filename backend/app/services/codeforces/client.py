import asyncio
import httpx
from typing import Dict, Any, List, Optional
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class CodeforcesAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class CodeforcesClient:
    """Async client for interacting with official Codeforces REST API with built-in rate limiting."""

    def __init__(self, base_url: str = None, rate_limit_delay: float = None):
        self.base_url = base_url or settings.CF_API_BASE_URL
        self.rate_limit_delay = (
            rate_limit_delay
            if rate_limit_delay is not None
            else settings.CF_API_RATE_LIMIT_DELAY
        )
        self._last_request_time = 0.0

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        
        # Enforce rate limit (1 request per rate_limit_delay seconds)
        await asyncio.sleep(self.rate_limit_delay)

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise CodeforcesAPIError(
                        f"Codeforces API error HTTP {response.status_code}",
                        status_code=response.status_code,
                    )
                data = response.json()
                if data.get("status") != "OK":
                    comment = data.get("comment", "Unknown Codeforces API Error")
                    raise CodeforcesAPIError(f"Codeforces API error: {comment}")
                return data.get("result")
            except httpx.RequestError as exc:
                logger.error("HTTP request error connecting to Codeforces API", error=str(exc))
                raise CodeforcesAPIError(f"Network error connecting to Codeforces: {str(exc)}")

    async def get_user_info(self, handle: str) -> Dict[str, Any]:
        """Fetch basic profile metadata for a Codeforces handle."""
        result = await self._make_request("user.info", {"handles": handle})
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        raise CodeforcesAPIError(f"User profile for handle '{handle}' not found.")

    async def get_user_rating_history(self, handle: str) -> List[Dict[str, Any]]:
        """Fetch contest rating history for a handle."""
        return await self._make_request("user.rating", {"handle": handle})

    async def get_user_submissions(self, handle: str, from_index: int = 1, count: int = 10000) -> List[Dict[str, Any]]:
        """Fetch submission history for a handle."""
        return await self._make_request(
            "user.status", {"handle": handle, "from": from_index, "count": count}
        )

    async def get_problemset_problems(self) -> Dict[str, Any]:
        """Fetch complete problem archive and problem statistics."""
        return await self._make_request("problemset.problems")
