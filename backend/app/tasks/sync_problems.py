import asyncio
from sqlalchemy import select
import structlog

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.db.models.problem import Problem, ProblemTag
from app.services.codeforces.client import CodeforcesClient

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.sync_problems.sync_problem_archive_task")
def sync_problem_archive_task():
    """Celery background task to synchronize full Codeforces problem archive."""
    return asyncio.run(_async_sync_problem_archive())


async def _async_sync_problem_archive():
    logger.info("Starting background problem archive sync task")
    cf_client = CodeforcesClient()
    result = await cf_client.get_problemset_problems()
    
    problems_list = result.get("problems", [])
    logger.info("Fetched problemset archive", total_problems=len(problems_list))

    async with AsyncSessionLocal() as db:
        for pdata in problems_list:
            contest_id = pdata.get("contestId")
            index = pdata.get("index")
            if not contest_id or not index:
                continue

            problem_id = f"{contest_id}_{index}"
            
            stmt = select(Problem).where(Problem.id == problem_id)
            res = await db.execute(stmt)
            problem = res.scalar_one_or_none()

            if not problem:
                problem = Problem(
                    id=problem_id,
                    contest_id=contest_id,
                    index=index,
                    name=pdata.get("name", "Unknown Problem"),
                    rating=pdata.get("rating"),
                    points=pdata.get("points"),
                )
                db.add(problem)
                await db.flush()

                tags = pdata.get("tags", [])
                for tag_name in tags:
                    tag_obj = ProblemTag(problem_id=problem_id, tag=tag_name)
                    db.add(tag_obj)

        await db.commit()
        logger.info("Completed problemset archive sync task")
        return {"status": "success", "count": len(problems_list)}
