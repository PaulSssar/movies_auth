from abc import ABC, abstractmethod
from typing import Optional

from models.film import Film
from models.genre import Genre
from models.person import Person


class FilmsStorage(ABC):

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_film(self, film_id: str) -> Optional[Film]:
        pass

    @abstractmethod
    async def get_genre(self, genre_id: str) -> Optional[Genre]:
        pass

    @abstractmethod
    async def get_person(self, person_id: str) -> Optional[Person]:
        pass

    @abstractmethod
    async def get_films(
            self,
            page_num: int,
            page_size: int,
            sort: str = None,
            order: str = None,
            query: str = None
    ) -> Optional[list[Film]]:
        pass

    @abstractmethod
    async def get_genres(
            self,
            page_num: int,
            page_size: int,
            sort: str = None,
            order: str = None
    ) -> Optional[list[Genre]]:
        pass

    @abstractmethod
    async def get_persons(
            self,
            page_num: int,
            page_size: int,
            sort: str = None,
            order: str = None
    ) -> Optional[list[Person]]:
        pass
