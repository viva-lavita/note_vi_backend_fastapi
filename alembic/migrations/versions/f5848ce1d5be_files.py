"""files

Revision ID: f5848ce1d5be
Revises: 018d2a34ee3f
Create Date: 2024-03-29 06:21:54.262965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5848ce1d5be'
down_revision: Union[str, None] = '018d2a34ee3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_file_user_id_user', 'file', type_='foreignkey')
    op.create_foreign_key(op.f('fk_file_user_id_user'), 'file', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_file_user_id_user'), 'file', type_='foreignkey')
    op.create_foreign_key('fk_file_user_id_user', 'file', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###