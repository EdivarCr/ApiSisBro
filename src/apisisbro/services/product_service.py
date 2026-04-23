from collections.abc import Sequence
from http import HTTPStatus

from fastapi import HTTPException

from apisisbro.models.models import Produto, User
from apisisbro.repository.product_repository import ProductRepository
from apisisbro.schemas.schema import FilterProduct, ProdutoCreate, ProdutoUpdate


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def create(self, product: ProdutoCreate, user: User) -> Produto:
        existing = await self.repo.get_product_by_name(product.nome)

        if existing is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='already exists'
            )

        db_product = Produto(**product.model_dump(), criador_id=user.id)

        created = await self.repo.create(db_product)

        return created

    async def list(self, limit: int = 10, offset: int = 0) -> Sequence[Produto]:
        return await self.repo.get_all(limit, offset)

    async def list_by_filter(self, filter: FilterProduct) -> Sequence[Produto]:
        return await self.repo.get_product_by_filter(filter)

    async def update(self, produto_id: int, produto_patch: ProdutoUpdate) -> Produto:
        product = await self.repo.get_by_id(produto_id)

        if product is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        for field, value in produto_patch.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        return await self.repo.update(product)
