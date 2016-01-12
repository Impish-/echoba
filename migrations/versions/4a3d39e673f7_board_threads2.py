"""board-threads2

Revision ID: 4a3d39e673f7
Revises: dfcf62aaa482
Create Date: 2016-01-11 16:57:52.734102

"""

# revision identifiers, used by Alembic.
revision = '4a3d39e673f7'
down_revision = 'dfcf62aaa482'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'thread_board_id_fkey', 'thread', type_='foreignkey')
    op.drop_column('thread', 'board_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('thread', sa.Column('board_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key(u'thread_board_id_fkey', 'thread', 'board', ['board_id'], ['id'])
    ### end Alembic commands ###