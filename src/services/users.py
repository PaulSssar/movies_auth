import datetime
import logging
import uuid

from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus

from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash

from db.cache import Cache
from db.postgres import get_session
from db.redis.redis_cache import RedisCache
from models.user import User, UserLogin

from core.config import settings

from models.refresh_token import RefreshToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@dataclass
class UserService:
    pg_session: AsyncSession
    redis: Cache

    async def check_user(self, user_data) -> ORJSONResponse:
        result = await self.pg_session.execute(
            select(User).options(selectinload(User.roles)).filter_by(
                login=user_data.login
            )
        )
        user = None
        if result:
            user = result.scalars().first()

        if user and check_password_hash(
                user.password,
                user_data.password
        ):
            self.pg_session.add(UserLogin(user_id=user.id))
            await self.pg_session.commit()
            token_pair = await self.get_token_pair(user)
            return token_pair

    async def save_refresh_token(self, token: str, user) -> None:
        refresh_token = RefreshToken(
            token=token,
            user_id=user.id,
            expires_at=(datetime.datetime.now()
                        + datetime.timedelta(
                        minutes=settings.refresh_token_lifetime
                    )))
        self.pg_session.add(refresh_token)

    async def login_history(
            self, login: str, page_number: int, page_size: int
    ) -> list[UserLogin]:
        result = await self.pg_session.execute(
            select(User).filter_by(login=login)
        )
        if not result:
            return []
        user = result.scalars().first()
        result = await self.pg_session.execute(
            select(UserLogin).filter_by(user_id=user.id).order_by(
                desc(UserLogin.login_at)
            ).offset((page_number - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all())

    async def logout(self, token: str) -> ORJSONResponse:
        try:
            payload = await self.decode_token_jwt(token)
            jti = payload.get('jti')

            await self.redis.put(f'token:{jti}', token, settings.access_token_lifetime)

            return ORJSONResponse({'logout': 'Successfully!'}, status_code=HTTPStatus.OK)

        except Exception as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    async def decode_access_token(self, token: str) -> ORJSONResponse:
        data = await self.decode_token_jwt(token)
        return ORJSONResponse(data, status_code=HTTPStatus.OK)

    async def decode_refresh_token(self, refresh_token: str) -> ORJSONResponse:
        data = await self.decode_token_jwt(refresh_token)
        user = data.get('user')

        if user:
            token_pair = await self.get_token_pair(user)
            return token_pair

    async def get_token_pair(self, user):
        data = {
            'user': user.login,
            'roles': user.roles,
            'jti': str(uuid.uuid4())
        }
        access_token = self._get_token(
            data,
            settings.access_token_lifetime
        )
        refresh_token = self._get_token(
            data,
            settings.refresh_token_lifetime
        )

        await self.save_refresh_token(refresh_token, user)

        return ORJSONResponse({
            'token': access_token,
            'refresh_token': refresh_token,
        }, HTTPStatus.OK)

    async def decode_token_jwt(self, token: str):
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
            expire = datetime.datetime.strptime(payload.get('expire'), "%Y-%m-%d %H:%M:%S.%f")
            token_in_storage = await self.redis.get(f'token:{payload.get("jti")}')

            if datetime.datetime.now() > expire or token_in_storage:
                logging.debug(
                    f'TOKEN EXPIRED: current time: {datetime.datetime.now()},'
                    f' expired: {expire}'
                )
                return {'data': 'token expired!'}

            result = await self.pg_session.execute(
                select(User).filter_by(login=payload.get('user')).options(selectinload(User.roles)))
            user = result.scalars().first()

            return {
                'user': payload.get('user'),
                'expire': payload.get('expire'),
                'id': str(user.id),
                'email': user.login,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'roles': [role.name for role in user.roles],
                'jti': payload.get('jti')
            }

        except JWTError:
            HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid token!')

    @staticmethod
    def _get_token(data, lifetime):
        expire = datetime.datetime.now() + datetime.timedelta(
            seconds=lifetime
        )
        data['expire'] = str(expire)

        token = jwt.encode(
            data,
            settings.secret_key,
            settings.algorithm
        )

        return token


@lru_cache()
def get_user_service(
        pg_session: AsyncSession = Depends(get_session),
        redis: RedisCache = Depends(RedisCache)
) -> UserService:
    return UserService(pg_session, redis)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session),
        user_service = Depends(get_user_service)
) -> User:
    try:
        data = await user_service.decode_token_jwt(token)

        user_login = data.get('user')
        if user_login is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        result = await session.execute(select(User).filter_by(login=user_login))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
