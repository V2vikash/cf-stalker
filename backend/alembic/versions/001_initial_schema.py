"""Initial schema setup

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # CF Profiles
    op.create_table(
        'cf_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('handle', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('max_rating', sa.Integer(), nullable=True),
        sa.Column('rank', sa.String(length=100), nullable=True),
        sa.Column('max_rank', sa.String(length=100), nullable=True),
        sa.Column('avatar', sa.String(length=500), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cf_profiles_handle'), 'cf_profiles', ['handle'], unique=True)

    # Contests
    op.create_table(
        'contests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('phase', sa.String(length=50), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('start_time_seconds', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # User Contest Stats
    op.create_table(
        'user_contest_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contest_id', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('old_rating', sa.Integer(), nullable=False),
        sa.Column('new_rating', sa.Integer(), nullable=False),
        sa.Column('rating_change', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contest_id'], ['contests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_contest_profile_id', 'user_contest_stats', ['cf_profile_id'])

    # Problems
    op.create_table(
        'problems',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('contest_id', sa.Integer(), nullable=True),
        sa.Column('index', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('points', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problems_contest_id'), 'problems', ['contest_id'])
    op.create_index(op.f('ix_problems_rating'), 'problems', ['rating'])

    # Problem Tags
    op.create_table(
        'problem_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', sa.String(length=100), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_problem_tag_lookup', 'problem_tags', ['tag', 'problem_id'])

    # Submissions
    op.create_table(
        'submissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', sa.String(length=100), nullable=False),
        sa.Column('creation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verdict', sa.String(length=50), nullable=False),
        sa.Column('pass_test_count', sa.Integer(), nullable=True),
        sa.Column('time_consumed_ms', sa.Integer(), nullable=True),
        sa.Column('memory_consumed_bytes', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_submission_profile_time', 'submissions', ['cf_profile_id', 'creation_time'])
    op.create_index('idx_submission_verdict', 'submissions', ['cf_profile_id', 'verdict'])

    # User Topic Stats
    op.create_table(
        'user_topic_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.Column('solved_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attempted_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_rating_solved', sa.Integer(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_topic_profile_tag', 'user_topic_stats', ['cf_profile_id', 'tag'], unique=True)

    # User Skill Gaps
    op.create_table(
        'user_skill_gaps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.Column('user_rating', sa.Integer(), nullable=False),
        sa.Column('tag_effective_rating', sa.Integer(), nullable=False),
        sa.Column('gap_delta', sa.Integer(), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_skill_gap_profile_tag', 'user_skill_gaps', ['cf_profile_id', 'tag'], unique=True)

    # Recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', sa.String(length=100), nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # AI Insights
    op.create_table(
        'ai_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=False),
        sa.Column('content_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Sync Jobs
    op.create_table(
        'sync_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cf_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cf_profile_id'], ['cf_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_job_profile_status', 'sync_jobs', ['cf_profile_id', 'status'])


def downgrade() -> None:
    op.drop_table('sync_jobs')
    op.drop_table('ai_insights')
    op.drop_table('recommendations')
    op.drop_table('user_skill_gaps')
    op.drop_table('user_topic_stats')
    op.drop_table('submissions')
    op.drop_table('problem_tags')
    op.drop_table('problems')
    op.drop_table('user_contest_stats')
    op.drop_table('contests')
    op.drop_table('cf_profiles')
    op.drop_table('users')
