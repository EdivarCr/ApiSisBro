from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

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

    async def get_object_field(self, field: str, value: object) -> ModelType | None:
        if not hasattr(self.model, field):
            raise AttributeError(f"{self.model.__name__} não possui o campo '{field}'")

        column = getattr(self.model, field)
        return await self.session.scalar(select(self.model).where(column == value))

    async def get_by_name(self, name: str, field: str = 'name') -> ModelType | None:
        return await self.get_object_field(field=field, value=name)

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

    async def get_all_by_filter(
        self,
        filters: Mapping[str, Any],
        *,
        like_fields: set[str] | None = None,
        limit: int = 10,
        offset: int = 0,
        data_inicio=None,
        data_fim=None,
        **kwargs,
    ) -> Sequence[ModelType]:
        query = select(self.model)
        like_fields = like_fields or set()

        if data_inicio:
            query = query.where(self.model.data_venda >= data_inicio)
        if data_fim:
            query = query.where(self.model.data_venda <= data_fim)

        for field, value in filters.items():
            if value is None:
                continue
            if not hasattr(self.model, field):
                raise AttributeError(
                    f"{self.model.__name__} não possui o campo '{field}'"
                )

            column = getattr(self.model, field)
            if field in like_fields and isinstance(value, str):
                query = query.where(column.ilike(f'%{value}%'))
            else:
                query = query.where(column == value)

        result = await self.session.scalars(query.offset(offset).limit(limit))
        return result.all()
