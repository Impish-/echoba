"""message column

Revision ID: 8f0588ea23fe
Revises: 1b1eec15414f
Create Date: 2016-01-11 16:44:00.393340

"""

# revision identifiers, used by Alembic.
revision = '8f0588ea23fe'
down_revision = '1b1eec15414f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'message_thread_fkey', 'message', type_='foreignkey')
    op.drop_column('message', 'thread')
    op.drop_constraint(u'thread_messages_fkey', 'thread', type_='foreignkey')
    op.drop_column('thread', 'messages')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('thread', sa.Column('messages', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'thread_messages_fkey', 'thread', 'message', ['messages'], ['id'])
    op.add_column('message', sa.Column('thread', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'message_thread_fkey', 'message', 'thread', ['thread'], ['id'])
    ### end Alembic commands ###