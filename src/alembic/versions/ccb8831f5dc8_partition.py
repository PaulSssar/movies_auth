"""partition

Revision ID: ccb8831f5dc8
Revises: 572ef79c6c75
Create Date: 2024-10-28 13:12:57.346393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, engine

from db.postgres import async_session
from models.user import Continent
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision: str = 'ccb8831f5dc8'
down_revision: Union[str, None] = '572ef79c6c75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for continent in Continent:
        op.execute(
            text(
                f"""CREATE TABLE IF NOT EXISTS "users_{continent.replace(' ', '').lower()}" PARTITION OF "users" FOR VALUES IN ('{continent}')"""
            ))


def downgrade() -> None:
    for continent in Continent:
        op.execute(
            text(
                f"""DROP TABLE "users_{continent.replace(' ', '').lower()}" PARTITION OF "users" FOR VALUES IN ('{continent}')"""
            ))
