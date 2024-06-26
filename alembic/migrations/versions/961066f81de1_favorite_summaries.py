"""favorite summaries

Revision ID: 961066f81de1
Revises: f295829871a6
Create Date: 2024-04-12 15:57:38.109980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '961066f81de1'
down_revision: Union[str, None] = 'f295829871a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('summary_users',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('summary_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['summary_id'], ['summary.id'], name=op.f('fk_summary_users_summary_id_summary'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_summary_users_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'summary_id', name=op.f('pk_summary_users'))
    )
    op.alter_column('favorite_notes', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('favorite_notes', 'note_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('favorite_notes', 'note_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('favorite_notes', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_table('summary_users')
    # ### end Alembic commands ###
