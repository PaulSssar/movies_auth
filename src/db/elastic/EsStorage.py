import json
import pkgutil
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

from core.config import settings

from db.films_storage import FilmsStorage
from models.film import Film
from models.genre import Genre
from models.person import Person


class EsStorage(FilmsStorage):

    def __init__(self):
        self.es: Optional[AsyncElasticsearch] = None

    async def open(self):
        self.es = AsyncElasticsearch(
            hosts=[
                f'{settings.elastic_schema}{settings.elastic_host}:'
                f'{settings.elastic_port}'
            ]
        )
        for index, fpath in ((settings.film_index, './films_mapping.json'),
                             (settings.genre_index, './genres_mapping.json'),
                             (settings.person_index, './persons_mapping.json')):
            mapping: dict = json.loads(
                pkgutil.get_data('db.elastic', fpath).decode()
            )
            await self.__create_index__(index, mapping)

    async def close(self):
        if self.es:
            await self.es.close()

    async def get_film(self, film_id: str) -> Optional[Film]:
        return await self.__get_item__(film_id, settings.film_index, Film)

    async def get_genre(self, genre_id: str) -> Optional[Genre]:
        return await self.__get_item__(genre_id, settings.genre_index, Genre)

    async def get_person(self, person_id: str) -> Optional[Person]:
        return await self.__get_item__(person_id, settings.person_index, Person)

    async def get_films(
            self,
            page_number: int,
            page_size: int,
            sort: str = None,
            order: str = None,
            query: str = None
    ) -> Optional[list[Film]]:
        return await self.__get_items__(
            page_number, page_size, settings.film_index, Film, sort, order, query
        )

    async def get_genres(
            self,
            page_num: int,
            page_size: int,
            sort: str = None,
            order: str = None,
            query: str = None
    ) -> Optional[list[Genre]]:
        return await self.__get_items__(
            page_num, page_size, settings.genre_index, Genre, sort, order, query
        )

    async def get_persons(
            self,
            page_num: int,
            page_size: int,
            sort: str = None,
            order: str = None,
            query: str = None
    ) -> Optional[list[Person]]:
        return await self.__get_items__(
            page_num, page_size, settings.person_index, Person, sort, order, query
        )

    async def __get_item__(
            self,
            item_id: str,
            item_index: str,
            item_class: type[Film, Genre, Person]
    ) -> Optional[Film|Genre|Person]:
        try:
            doc = await self.es.get(index=item_index, id=item_id)
        except NotFoundError:
            return None
        return item_class(**doc['_source'])

    @staticmethod
    def __get_params__(
            page_num: int, page_size: int, sort: str = None, order: str = None
    ) -> dict:
        params = {'from': page_num * page_size, 'size': page_size}
        if sort:
            params['sort'] = [{sort: {'order': 'asc'}}]
            if order and order == ('asc' or 'desc'):
                params['sort'][0][sort]['order'] = order
        return params

    @staticmethod
    def __get_body__(query: str = None) -> Optional[dict]:
        return {
           'query':    {
               'query_string': {
                   'query': query
               }
           }
        } if query else None

    async def __get_items__(
            self,
            page_number: int,
            page_size: int,
            item_index: str,
            item_class: type[Film, Genre, Person],
            sort: str = None,
            order: str = None,
            query: str = None
    ) -> Optional[list[Film|Genre|Person]]:
        data = await self.es.search(
            index=item_index,
            params=EsStorage.__get_params__(page_number, page_size, sort, order),
            body=EsStorage.__get_body__(query)
        )
        if not data:
            return None
        return [item_class(**item.get('_source'))
                for item in data['hits']['hits']]

    async def __create_index__(self, index_name: str, index_mapping: dict):
        index_exists = await self.es.indices.exists(index=index_name)

        if index_exists:
            return

        await self.es.indices.create(index=index_name, body=index_mapping)
