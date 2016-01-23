"""rename

Revision ID: ca9bd5131d40
Revises: 34478a7af411
Create Date: 2016-01-23 05:31:14.509001

"""

# revision identifiers, used by Alembic.
revision = 'ca9bd5131d40'
down_revision = '34478a7af411'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('board', sa.Column('available_until', sa.String(), nullable=True))
    op.drop_column('board', 'available_unlil')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('board', sa.Column('available_unlil', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('board', 'available_until')
    ### end Alembic commands ###
