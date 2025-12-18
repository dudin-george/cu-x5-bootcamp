"""add candidate fields and interview feedback

Revision ID: abc123def456
Revises: eaa7a0c6db30
Create Date: 2025-12-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = 'eaa7a0c6db30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to candidates table
    op.add_column('candidates', sa.Column('university', sa.String(length=255), nullable=True, comment='Название университета'))
    op.add_column('candidates', sa.Column('course', sa.Integer(), nullable=True, comment='Курс обучения (1-6)'))
    op.add_column('candidates', sa.Column('achievements', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]', comment='Достижения кандидата (олимпиады, проекты, etc.)'))
    op.add_column('candidates', sa.Column('domains', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]', comment='Области интересов/доменов (ML, Web, Mobile, etc.)'))

    # Create interview_feedbacks table
    op.create_table('interview_feedbacks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Уникальный UUID фидбека'),
        sa.Column('pool_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Ссылка на запись в candidate pool'),
        sa.Column('feedback_text', sa.Text(), nullable=False, comment='Комментарий HM после интервью'),
        sa.Column('decision', sa.String(length=50), nullable=False, comment='Решение: reject_globally, reject_team, freeze, to_finalist'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='Когда фидбек был создан'),
        sa.ForeignKeyConstraint(['pool_id'], ['candidate_pools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pool_id')
    )
    op.create_index(op.f('ix_interview_feedbacks_id'), 'interview_feedbacks', ['id'], unique=True)
    op.create_index(op.f('ix_interview_feedbacks_pool_id'), 'interview_feedbacks', ['pool_id'], unique=False)


def downgrade() -> None:
    # Drop interview_feedbacks table
    op.drop_index(op.f('ix_interview_feedbacks_pool_id'), table_name='interview_feedbacks')
    op.drop_index(op.f('ix_interview_feedbacks_id'), table_name='interview_feedbacks')
    op.drop_table('interview_feedbacks')

    # Remove columns from candidates table
    op.drop_column('candidates', 'domains')
    op.drop_column('candidates', 'achievements')
    op.drop_column('candidates', 'course')
    op.drop_column('candidates', 'university')
