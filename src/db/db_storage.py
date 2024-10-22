from typing import Optional

from db.films_storage import FilmsStorage

storage: Optional[FilmsStorage] = None


async def get_storage() -> FilmsStorage:
    return storage