from typing import Optional

from elasticsearch import NotFoundError

from core.config import settings
from db.cache import Cache
from db.storage import Storage
from models.film import Film, Films
from models.genre import Genre, Genres
from models.person import Person, Persons


class BaseService:
    def __init__(self, cache: Cache, storage: Storage,
                 index_name: str):
        self.cache = cache
        self.storage = storage
        self.index_name = index_name

    def _get_class(self):
        return {'genres': Genre, 'persons': Person}.get(self.index_name, Film)

    def _get_items_class(self):
        return {'genres': Genres,
                'persons': Persons}.get(self.index_name, Films)

    def _get_page_key(self, params: dict, query: dict):
        return f"{self.index_name}:{params.get('sort', '')}:{params['from']}:{params['size']}:{query}"

    async def get_items(self, **kwargs) -> Optional[list[Film | Genre | Person]]:
        body = await self.get_body(kwargs)
        params = await self.get_params(kwargs)
        page_key = self._get_page_key(params, body)
        items = await self._page_from_cache(page_key)
        if not items:
            items: Optional[list[Film | Genre | Person]] = None
            if self.index_name == settings.film_index:
                items = await self.storage.get_films(**kwargs)
            elif self.index_name == settings.genre_index:
                items = await self.storage.get_genres(**kwargs)
            elif self.index_name == settings.person_index:
                items = await self.storage.get_persons(**kwargs)
            if not items:
                return None
            await self._put_page_to_cache(page_key, items)

        return items

    @staticmethod
    async def get_params(kwargs):
        page_size = kwargs.get('page_size')
        sort = kwargs.get('sort')
        order = kwargs.get('order')

        params = {
            'size': page_size,
            'from': kwargs.get('page_number') * page_size
        }
        if sort:
            params['sort'] = sort
            if order and order == ('asc' or 'desc'):
                params['sort'][sort]['order'] = order

        return params

    @staticmethod
    async def get_body(kwargs):
        query = kwargs.get('query')

        if query:
            body = {
                'query_string': {
                        'query': query,
                         }
                }

        else:
            body = {'match_all': {}}

        return body

    async def get_by_id(self, item_id: str) -> Optional[Film | Genre | Person]:
        item = await self._item_from_cache(item_id)
        if not item:
            item = await self._get_item_from_elastic(item_id)
            if not item:
                return None
            await self._put_item_to_cache(item)
        return item

    async def _get_item_from_elastic(self, item_id: str) -> Optional[
        Film | Genre | Person
    ]:
        try:
            doc: Optional[Film | Genre | Person] = None
            if self.index_name == settings.film_index:
                doc = await self.storage.get_film(item_id)
            elif self.index_name == settings.genre_index:
                doc = await self.storage.get_genre(item_id)
            elif self.index_name == settings.person_index:
                doc = await self.storage.get_person(item_id)
        except NotFoundError:
            return None
        return doc

    async def _item_from_cache(self, item_id: str) -> Optional[
        Film | Genre | Person]:
        data = await self.cache.get(f'{self.index_name}:{item_id}')
        if not data:
            return None

        return self._get_class().parse_raw(data)

    async def _put_item_to_cache(self, item: [Film | Genre | Person]):
        await self.cache.put(
            f'{self.index_name}:{item.id}',
            item.json(),
            settings.cache_expire_in_seconds
        )

    async def _page_from_cache(self, page_key: str) -> Optional[list[
        Film | Genre | Person]]:
        data = await self.cache.get(page_key)
        if not data:
            return None

        return self._get_items_class().parse_raw(data).items

    async def _put_page_to_cache(self, page_key: str,
                                 items_page: list[Film | Genre | Person]):
        items_list: Films | Genres | Persons = self._get_items_class()(
            items=items_page)
        await self.cache.put(page_key, items_list.json(),
                             settings.cache_expire_in_seconds)
