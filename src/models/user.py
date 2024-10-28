# models/user.py
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean, text, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.role import user_roles_table


class Continent(str, enum.Enum):
    AFRICA = 'Africa'
    ASIA = 'Asia'
    EUROPE = 'Europe'
    NORTH_AMERICA = 'North America'
    OCEANIA = 'Oceania'
    SOUTH_AMERICA = 'South America'
    ANTARCTICA = 'Antarctica'


def create_partition(target, connection, **kwargs) -> None:
    for continent in Continent:
        connection.execute(
            text(
                f"""CREATE TABLE IF NOT EXISTS "users_{continent.replace(' ', '').lower()}" PARTITION OF "users" FOR VALUES IN ('{continent}')"""
            ))


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('login', 'continent'),
        {
            'postgresql_partition_by': 'LIST (continent)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_superuser = Column(Boolean, default=False)
    continent = Column(String(50), primary_key=True, nullable=False, server_default=Continent.EUROPE.value)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    roles = relationship(
        'Role', secondary=user_roles_table, back_populates='users'
    )
    user_logins = relationship('UserLogin', back_populates='user')
    user_id = Column(String(255), unique=True, nullable=True)
    user_email = Column(String(255), unique=True, nullable=True)

    def __init__(
            self, login: str, password: str, first_name: str, last_name: str,
            is_superuser: bool = False, user_id: str = None,
            user_email: str = None
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_superuser = is_superuser
        self.user_id = user_id
        self.user_email = user_email

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserLogin(Base):
    __tablename__ = 'users_logins'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    signin_data = Column(String(255))
    login_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    user = relationship('User', back_populates='user_logins')

    def __init__(
            self, user_id: uuid.UUID, signin_data=''
    ) -> None:
        self.user_id = user_id
        self.signin_data = signin_data

    def __repr__(self) -> str:
        return (f'<user:{self.user.login} login:{self.login_at} '
                f'user data:{self.signin_data}>')
