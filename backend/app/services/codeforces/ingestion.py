from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import structlog

from app.db.models.cf_profile import CFProfile
from app.db.models.contest import Contest, UserContestStat
from app.db.models.problem import Problem, ProblemTag
from app.db.models.submission import Submission
from app.db.models.analytics import UserTopicStat, UserSkillGap
from app.services.codeforces.client import CodeforcesClient

logger = structlog.get_logger()


class IngestionService:
    """Service for ingesting and processing raw Codeforces API data into PostgreSQL models."""

    def __init__(self, db: AsyncSession, cf_client: CodeforcesClient = None):
        self.db = db
        self.cf_client = cf_client or CodeforcesClient()

    async def sync_cf_profile(self, handle: str) -> CFProfile:
        """Fetch and update profile metadata for handle."""
        user_info = await self.cf_client.get_user_info(handle)
        
        stmt = select(CFProfile).where(CFProfile.handle == handle)
        result = await self.db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            profile = CFProfile(handle=handle)
            self.db.add(profile)

        profile.rating = user_info.get("rating")
        profile.max_rating = user_info.get("maxRating")
        profile.rank = user_info.get("rank")
        profile.max_rank = user_info.get("maxRank")
        profile.avatar = user_info.get("titlePhoto") or user_info.get("avatar")
        profile.last_synced_at = datetime.utcnow()

        await self.db.flush()
        return profile

    async def sync_user_contests(self, profile: CFProfile) -> None:
        """Fetch and ingest contest rating history for profile."""
        ratings = await self.cf_client.get_user_rating_history(profile.handle)

        for item in ratings:
            contest_id = item["contestId"]
            contest_name = item.get("contestName", f"Contest {contest_id}")

            # Upsert Contest
            c_stmt = select(Contest).where(Contest.id == contest_id)
            c_res = await self.db.execute(c_stmt)
            contest = c_res.scalar_one_or_none()
            if not contest:
                contest = Contest(id=contest_id, name=contest_name)
                self.db.add(contest)
                await self.db.flush()

            # Upsert UserContestStat
            ucs_stmt = select(UserContestStat).where(
                UserContestStat.cf_profile_id == profile.id,
                UserContestStat.contest_id == contest_id,
            )
            ucs_res = await self.db.execute(ucs_stmt)
            stat = ucs_res.scalar_one_or_none()

            old_r = item.get("oldRating", 0)
            new_r = item.get("newRating", 0)
            if not stat:
                stat = UserContestStat(
                    cf_profile_id=profile.id,
                    contest_id=contest_id,
                    rank=item.get("rank", 0),
                    old_rating=old_r,
                    new_rating=new_r,
                    rating_change=new_r - old_r,
                )
                self.db.add(stat)

        await self.db.flush()

    async def sync_user_submissions(self, profile: CFProfile) -> None:
        """Fetch and ingest user submissions and update topic stats."""
        raw_submissions = await self.cf_client.get_user_submissions(profile.handle)

        for sub_data in raw_submissions:
            sub_id = sub_data["id"]
            prob_data = sub_data.get("problem", {})
            contest_id = prob_data.get("contestId")
            index = prob_data.get("index")

            if not contest_id or not index:
                continue

            problem_id = f"{contest_id}_{index}"

            # Upsert Problem
            p_stmt = select(Problem).where(Problem.id == problem_id)
            p_res = await self.db.execute(p_stmt)
            problem = p_res.scalar_one_or_none()

            if not problem:
                problem = Problem(
                    id=problem_id,
                    contest_id=contest_id,
                    index=index,
                    name=prob_data.get("name", "Unknown Problem"),
                    rating=prob_data.get("rating"),
                    points=prob_data.get("points"),
                )
                self.db.add(problem)
                await self.db.flush()

                # Add Tags
                tags = prob_data.get("tags", [])
                for tag_name in tags:
                    tag_obj = ProblemTag(problem_id=problem_id, tag=tag_name)
                    self.db.add(tag_obj)

            # Check if submission exists
            s_stmt = select(Submission).where(Submission.id == sub_id)
            s_res = await self.db.execute(s_stmt)
            existing_sub = s_res.scalar_one_or_none()

            creation_dt = datetime.utcfromtimestamp(sub_data.get("creationTimeSeconds", 0))

            if not existing_sub:
                sub = Submission(
                    id=sub_id,
                    cf_profile_id=profile.id,
                    problem_id=problem_id,
                    creation_time=creation_dt,
                    verdict=sub_data.get("verdict", "UNKNOWN"),
                    pass_test_count=sub_data.get("passTestCount"),
                    time_consumed_ms=sub_data.get("timeConsumedMillis"),
                    memory_consumed_bytes=sub_data.get("memoryConsumedBytes"),
                )
                self.db.add(sub)

        await self.db.flush()

    async def compute_topic_aggregations(self, profile: CFProfile) -> None:
        """Pre-compute topic-wise solved counts, max rating, and accuracy for user."""
        # Query solved submissions join problem and problem_tags
        stmt = (
            select(Submission, Problem, ProblemTag)
            .join(Problem, Submission.problem_id == Problem.id)
            .join(ProblemTag, Problem.id == ProblemTag.problem_id)
            .where(Submission.cf_profile_id == profile.id)
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        tag_map: Dict[str, Dict[str, Any]] = {}

        for sub, prob, ptag in rows:
            tag = ptag.tag
            if tag not in tag_map:
                tag_map[tag] = {
                    "solved_problems": set(),
                    "attempted_submissions": 0,
                    "accepted_submissions": 0,
                    "max_rating": 0,
                }

            tag_map[tag]["attempted_submissions"] += 1
            if sub.verdict == "OK":
                tag_map[tag]["accepted_submissions"] += 1
                tag_map[tag]["solved_problems"].add(prob.id)
                if prob.rating and prob.rating > tag_map[tag]["max_rating"]:
                    tag_map[tag]["max_rating"] = prob.rating

        # Delete existing topic stats for this profile
        await self.db.execute(
            delete(UserTopicStat).where(UserTopicStat.cf_profile_id == profile.id)
        )

        user_rating = profile.rating or 1200

        for tag, stats in tag_map.items():
            solved_cnt = len(stats["solved_problems"])
            attempted_cnt = stats["attempted_submissions"]
            acc = (
                (stats["accepted_submissions"] / attempted_cnt) * 100.0
                if attempted_cnt > 0
                else 0.0
            )
            max_r = stats["max_rating"] if stats["max_rating"] > 0 else None

            topic_stat = UserTopicStat(
                cf_profile_id=profile.id,
                tag=tag,
                solved_count=solved_cnt,
                attempted_count=attempted_cnt,
                max_rating_solved=max_r,
                accuracy=round(acc, 2),
                updated_at=datetime.utcnow(),
            )
            self.db.add(topic_stat)

            # Also compute skill gap classification
            effective_rating = max_r if max_r else 800
            gap_delta = user_rating - effective_rating
            if gap_delta > 200:
                classification = "WEAKNESS"
            elif gap_delta < -100:
                classification = "STRENGTH"
            else:
                classification = "BALANCED"

            # Delete old skill gap record if exists
            await self.db.execute(
                delete(UserSkillGap).where(
                    UserSkillGap.cf_profile_id == profile.id, UserSkillGap.tag == tag
                )
            )

            skill_gap = UserSkillGap(
                cf_profile_id=profile.id,
                tag=tag,
                user_rating=user_rating,
                tag_effective_rating=effective_rating,
                gap_delta=gap_delta,
                classification=classification,
                updated_at=datetime.utcnow(),
            )
            self.db.add(skill_gap)

        await self.db.commit()
