"""Add user and log_message tables

Revision ID: a2b0341eb5af
Revises: 
Create Date: 2021-11-28 11:20:51.235996

"""
from alembic import op
import sqlalchemy as sa
import fastapi_utils

# revision identifiers, used by Alembic.
revision = 'a2b0341eb5af'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', fastapi_utils.guid_type.GUID(),
                              nullable=False),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('log_messages',
                    sa.Column('id', fastapi_utils.guid_type.GUID(),
                              nullable=False),
                    sa.Column(
                        'user_id', fastapi_utils.guid_type.GUID(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('log_message', sa.String(
                        length=256), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_log_messages_id'),
                    'log_messages', ['id'], unique=False)
    op.create_index(op.f('ix_log_messages_user_id'),
                    'log_messages', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_log_messages_user_id'), table_name='log_messages')
    op.drop_index(op.f('ix_log_messages_id'), table_name='log_messages')
    op.drop_table('log_messages')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###