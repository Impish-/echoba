"""empty message

Revision ID: 1333dda789bf
Revises: 
Create Date: 2016-01-15 15:52:00.867691

"""

# revision identifiers, used by Alembic.
import sqlalchemy_utils

revision = '1333dda789bf'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('board',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('dir', sa.String(), nullable=False),
    sa.Column('threads_on_page', sa.Integer(), nullable=True),
    sa.Column('default_name', sa.String(), nullable=False),
    sa.Column('max_pages', sa.Integer(), nullable=True),
    sa.Column('thread_bumplimit', sa.Integer(), nullable=True),
    sa.Column('thread_tail', sa.Integer(), nullable=True),
    sa.Column('captcha', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dir'),
    sa.UniqueConstraint('dir'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.create_table('staff',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('password', sqlalchemy_utils.types.password.PasswordType(), nullable=False),
    sa.Column('role', sqlalchemy_utils.types.choice.ChoiceType([('adm', u'Admin'),
                                  ('mod', u'Moderator'),
                                ]), nullable=False),
    sa.Column('all_boards', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.create_table('association',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('staff_id', sa.Integer(), nullable=True),
    sa.Column('board_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['board.id'], ),
    sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('thread',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sticky', sa.BOOLEAN(), nullable=False),
    sa.Column('closed', sa.BOOLEAN(), nullable=False),
    sa.Column('board_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['board_id'], ['board.id'], ),
    sa.PrimaryKeyConstraint('id',)
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('poster_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('header', sa.String(), nullable=True),
    sa.Column('message', sa.UnicodeText(), nullable=False),
    sa.Column('password', sqlalchemy_utils.types.password.PasswordType(), nullable=True),
    sa.Column('thread_id', sa.Integer(), nullable=False),
    sa.Column('ip_address', sqlalchemy_utils.types.ip_address.IPAddressType(length=50), nullable=True),
    sa.ForeignKeyConstraint(['thread_id'], ['thread.id'], ),
    sa.PrimaryKeyConstraint('id',)
    )
    op.create_table('images',
    sa.Column('width', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('mimetype', sa.String(length=255), nullable=False),
    sa.Column('original', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.PrimaryKeyConstraint('width', 'height', 'message_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    op.drop_table('message')
    op.drop_table('thread')
    op.drop_table('association')
    op.drop_table('staff')
    op.drop_table('board')
    ### end Alembic commands ###
