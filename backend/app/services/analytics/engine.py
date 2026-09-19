import math
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.cf_profile import CFProfile
from app.db.models.contest import Contest, UserContestStat
from app.db.models.problem import Problem
from app.db.models.submission import Submission
from app.db.models.analytics import UserTopicStat
from app.schemas.analytics import (
    ProfileOverviewResponse,
    ContestAnalyticsResponse,
    ContestStatItem,
    TopicAnalyticsResponse,
    TagStatItem,
)


class AnalyticsEngine:
    """Core computational engine for profile performance, rating dynamics, and contest analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_overview(self, profile: CFProfile) -> ProfileOverviewResponse:
        # Fetch contest stats for volatility calculation
        c_stmt = select(UserContestStat).where(UserContestStat.cf_profile_id == profile.id)
        c_res = await self.db.execute(c_stmt)
        contest_stats = c_res.scalars().all()

        changes = [stat.rating_change for stat in contest_stats]
        volatility = 0.0
        if len(changes) > 1:
            mean = sum(changes) / len(changes)
            variance = sum((x - mean) ** 2 for x in changes) / (len(changes) - 1)
            volatility = round(math.sqrt(variance), 2)

        # Total solved distinct problems
        s_stmt = select(func.count(func.distinct(Submission.problem_id))).where(
            Submission.cf_profile_id == profile.id, Submission.verdict == "OK"
        )
        s_res = await self.db.execute(s_stmt)
        total_solved = s_res.scalar() or 0

        # Total submissions & overall accuracy
        sub_cnt_stmt = select(func.count(Submission.id)).where(Submission.cf_profile_id == profile.id)
        sub_cnt_res = await self.db.execute(sub_cnt_stmt)
        total_submissions = sub_cnt_res.scalar() or 0

        ok_cnt_stmt = select(func.count(Submission.id)).where(
            Submission.cf_profile_id == profile.id, Submission.verdict == "OK"
        )
        ok_cnt_res = await self.db.execute(ok_cnt_stmt)
        total_ok = ok_cnt_res.scalar() or 0

        overall_accuracy = (
            round((total_ok / total_submissions) * 100.0, 2) if total_submissions > 0 else 0.0
        )

        return ProfileOverviewResponse(
            handle=profile.handle,
            current_rating=profile.rating,
            max_rating=profile.max_rating,
            rank=profile.rank,
            max_rank=profile.max_rank,
            avatar=profile.avatar,
            volatility=volatility,
            contests_attended=len(contest_stats),
            total_solved=total_solved,
            total_submissions=total_submissions,
            overall_accuracy=overall_accuracy,
        )

    async def get_contest_analytics(self, profile: CFProfile) -> ContestAnalyticsResponse:
        stmt = (
            select(UserContestStat, Contest)
            .join(Contest, UserContestStat.contest_id == Contest.id)
            .where(UserContestStat.cf_profile_id == profile.id)
            .order_by(Contest.id.asc())
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        items: List[ContestStatItem] = []
        best_rank = None
        max_pos = 0
        max_neg = 0

        for stat, contest in rows:
            if best_rank is None or stat.rank < best_rank:
                best_rank = stat.rank

            if stat.rating_change > max_pos:
                max_pos = stat.rating_change
            if stat.rating_change < max_neg:
                max_neg = stat.rating_change

            items.append(
                ContestStatItem(
                    contest_id=contest.id,
                    name=contest.name,
                    rank=stat.rank,
                    old_rating=stat.old_rating,
                    new_rating=stat.new_rating,
                    rating_change=stat.rating_change,
                )
            )

        return ContestAnalyticsResponse(
            handle=profile.handle,
            total_contests=len(items),
            best_rank=best_rank,
            max_positive_delta=max_pos,
            max_negative_delta=max_neg,
            contests=items,
        )

    async def get_topic_analytics(self, profile: CFProfile) -> TopicAnalyticsResponse:
        # Difficulty distribution of solved problems
        diff_stmt = (
            select(Problem.rating, func.count(func.distinct(Problem.id)))
            .join(Submission, Submission.problem_id == Problem.id)
            .where(
                Submission.cf_profile_id == profile.id,
                Submission.verdict == "OK",
                Problem.rating.isnot(None),
            )
            .group_by(Problem.rating)
            .order_by(Problem.rating.asc())
        )
        diff_res = await self.db.execute(diff_stmt)
        diff_map = {rating: count for rating, count in diff_res.all()}

        # Topic stats
        t_stmt = (
            select(UserTopicStat)
            .where(UserTopicStat.cf_profile_id == profile.id)
            .order_by(UserTopicStat.solved_count.desc())
        )
        t_res = await self.db.execute(t_stmt)
        topic_rows = t_res.scalars().all()

        tags = [
            TagStatItem(
                tag=ts.tag,
                solved_count=ts.solved_count,
                attempted_count=ts.attempted_count,
                max_rating_solved=ts.max_rating_solved,
                accuracy=ts.accuracy,
            )
            for ts in topic_rows
        ]

        return TopicAnalyticsResponse(
            handle=profile.handle,
            difficulty_distribution=diff_map,
            tags=tags,
        )
