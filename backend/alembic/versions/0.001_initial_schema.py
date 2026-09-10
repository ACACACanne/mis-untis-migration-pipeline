"""initial_schema

Revision ID: 0001
Revises: 
Create Date: 2026-09-10 21:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Bi-Directional Identity Registry
    op.create_table(
        'key_registry',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False, index=True), # teacher, room, subject, class, student
        sa.Column('untis_id', sa.String(length=100), nullable=False, index=True),
        sa.Column('arbor_id', sa.String(length=100), nullable=True, index=True),
        sa.Column('bromcom_id', sa.String(length=100), nullable=True, index=True),
        sa.Column('short_code', sa.String(length=50), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('entity_type', 'untis_id', name='uq_entity_untis_id')
    )

    # 2. Quarantine & Anomaly Ledger
    op.create_table(
        'quarantine_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sync_direction', sa.String(length=20), nullable=False, default='UNTIS_TO_MIS'),
        sa.Column('lesson_id', sa.String(length=100), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('error_type', sa.String(length=100), nullable=False), # COLLISION, UNASSIGNED_ROOM, UNMAPPED_STUDENT
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='PENDING'), # PENDING, RESOLVED, IGNORED
        sa.Column('resolved_override', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # 3. Timetable Diff & Staging Ledger
    op.create_table(
        'timetable_diff',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('target_mis', sa.String(length=20), nullable=False), # ARBOR or BROMCOM
        sa.Column('untis_lesson_id', sa.String(length=100), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('period_number', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(length=30), nullable=False), # CREATE, UPDATE, DELETE, UNCHANGED
        sa.Column('staged_slot_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='STAGED'), # STAGED, COMMITTED, FAILED
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # 4. Sync Audit & Execution History
    op.create_table(
        'sync_audit',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sync_direction', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False), # RUNNING, COMPLETED, FAILED
        sa.Column('total_records', sa.Integer(), default=0),
        sa.Column('staged_records', sa.Integer(), default=0),
        sa.Column('quarantined_records', sa.Integer(), default=0),
        sa.Column('committed_records', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('sync_audit')
    op.drop_table('timetable_diff')
    op.drop_table('quarantine_items')
    op.drop_table('key_registry')