import asyncio
from typing import Dict, Any
from sqlalchemy import select
import structlog

from app.core.database import AsyncSessionLocal
from app.db.models.problem import Problem, ProblemTag
from app.services.codeforces.client import CodeforcesClient

logger = structlog.get_logger()
_archive_sync_lock = asyncio.Lock()


async def sync_problem_archive_task() -> Dict[str, Any]:
    """Asynchronous background task to synchronize full Codeforces problem archive safely and efficiently."""
    async with _archive_sync_lock:
        logger.info("Starting background problem archive sync task")
        cf_client = CodeforcesClient()
        result = await cf_client.get_problemset_problems()
        
        problems_list = result.get("problems", [])
        logger.info("Fetched problemset archive from Codeforces", total_problems=len(problems_list))

        async with AsyncSessionLocal() as db:
            # Query existing problem IDs in bulk for O(1) existence lookup
            existing_ids_res = await db.execute(select(Problem.id))
            existing_ids = set(existing_ids_res.scalars().all())

            new_problems_count = 0
            for pdata in problems_list:
                contest_id = pdata.get("contestId")
                index = pdata.get("index")
                if not contest_id or not index:
                    continue

                problem_id = f"{contest_id}_{index}"
                if problem_id in existing_ids:
                    continue

                problem = Problem(
                    id=problem_id,
                    contest_id=contest_id,
                    index=index,
                    name=pdata.get("name", "Unknown Problem"),
                    rating=pdata.get("rating"),
                    points=pdata.get("points"),
                )
                db.add(problem)
                existing_ids.add(problem_id)
                new_problems_count += 1

                tags = pdata.get("tags", [])
                for tag_name in tags:
                    tag_obj = ProblemTag(problem_id=problem_id, tag=tag_name)
                    db.add(tag_obj)

            await db.commit()
            logger.info("Completed problemset archive sync task", new_added=new_problems_count)
            return {"status": "success", "count": len(problems_list), "new_added": new_problems_count}
