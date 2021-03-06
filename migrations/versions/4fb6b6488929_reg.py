"""reg

Revision ID: 4fb6b6488929
Revises: ca9bd5131d40
Create Date: 2016-01-26 09:22:30.424213

"""

# revision identifiers, used by Alembic.
revision = '4fb6b6488929'
down_revision = 'ca9bd5131d40'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('registerrequest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.String(length=60), nullable=False),
    sa.Column('staff_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'staff', sa.Column('active', sa.BOOLEAN(), nullable=True))
    ### end Alembic commands ###

    conn = op.get_bind()
    conn.execute(text("""UPDATE staff SET active=True"""))


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'staff', 'active')
    op.drop_table('registerrequest')
    ### end Alembic commands ###
