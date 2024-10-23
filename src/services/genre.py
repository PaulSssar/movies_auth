from functools import lru_cache

from fastapi import Depends

from core.config import settings
from db.cache import Cache
from db.storage import Storage
from db.db_cache import get_cache
from db.db_storage import get_storage
from services.base import BaseService


class GenreService(BaseService):
    def __init__(self, cache: Cache, storage: Storage):
        super().__init__(cache, storage, index_name=settings.genre_index)


@lru_cache()
def get_genre_service(
    cache: Cache = Depends(get_cache),
    storage: Storage = Depends(get_storage)
) -> GenreService:
    return GenreService(cache, storage)
