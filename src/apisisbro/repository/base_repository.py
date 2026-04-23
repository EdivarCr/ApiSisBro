from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[ModelType](ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @property  # para ser usado como atributo dentro da class
    @abstractmethod
    def model(self) -> type[ModelType]: ...

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.scalar(select(self.model).where(self.model.id == id))

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[ModelType]:
        result = await self.session.scalars(
            select(self.model).limit(limit).offset(offset)
        )
        return result.all()

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        await self.session.delete(entity)
