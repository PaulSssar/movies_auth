"""initial

Revision ID: 572ef79c6c75
Revises: 
Create Date: 2024-10-28 13:11:39.791483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '572ef79c6c75'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.String(length=500), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_table('users',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('login', sa.String(length=255), nullable=False),
                    sa.Column('password', sa.String(length=255), nullable=False),
                    sa.Column('first_name', sa.String(length=50), nullable=True),
                    sa.Column('last_name', sa.String(length=50), nullable=True),
                    sa.Column('is_superuser', sa.Boolean(), nullable=True),
                    sa.Column('continent', sa.String(length=50), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id', 'continent'),
                    sa.UniqueConstraint('id', 'continent'),
                    postgresql_partition_by='list(continent)'
                    )
    op.create_table('refresh_tokens',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('token', sa.String(length=255), nullable=False),
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('expires_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('user_roles',
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('role_id', sa.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'role_id')
                    )
    op.create_table('users_logins',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('signin_data', sa.String(length=255), nullable=True),
                    sa.Column('login_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_logins')
    op.drop_table('user_roles')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###