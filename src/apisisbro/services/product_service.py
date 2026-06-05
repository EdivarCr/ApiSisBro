from collections.abc import Sequence
from http import HTTPStatus

from fastapi import HTTPException, UploadFile

from apisisbro.models.models import Produto, User
from apisisbro.repository.product_repository import ProductRepository
from apisisbro.schemas.schema import FilterProduct, ProdutoCreate, ProdutoUpdate
from apisisbro.services.storage_service import StorageService


class ProductService:
    def __init__(self, repo: ProductRepository, storage_service: StorageService):
        self.repo = repo
        self.storage_service = storage_service

    async def create(self, product: ProdutoCreate, user: User) -> Produto:
        existing = await self.repo.get_product_by_name(product.nome)

        if existing is not None:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='already exists')

        try:
            return await self.repo.create_product_with_recipe(product, user.id)
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f'Erro ao salvar: {str(e)}'
            ) from e

    async def list(self, limit: int = 10, offset: int = 0) -> Sequence[Produto]:
        return await self.repo.get_all(limit, offset)

    async def list_by_filter(self, filter: FilterProduct) -> Sequence[Produto]:
        return await self.repo.get_product_by_filter(filter)

    async def update(
        self,
        produto_id: int,
        produto_patch: ProdutoUpdate,
    ) -> Produto:
        product = await self.repo.get_by_id(produto_id)

        if product is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        for field, value in produto_patch.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        return await self.repo.update(product)

    async def upload(self, produto_id: int, image: UploadFile):
        product = await self.repo.get_by_id(produto_id)

        if product is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        if image is None:
            return None

        try:
            uploaded = await self.storage_service.upload_product_image(
                file=image, product_id=product.id
            )
            updated_product = await self.repo.update_image(
                product=product,
                bucket=uploaded.bucket,
                path=uploaded.path,
            )

            return updated_product

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f'Erro ao fazer upload da imagem: {str(e)}',
            ) from e

    async def update_image(
        self,
        produto_id: int,
        image: UploadFile | None,
        remove_image: bool = False,
    ):
        product = await self.repo.get_by_id(produto_id)

        if product is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        if image is not None:
            old_bucket = product.imagem_bucket
            old_path = product.imagem_path

            uploaded = await self.storage_service.upload_product_image(
                file=image, product_id=product.id
            )

            product.imagem_bucket = uploaded.bucket
            product.imagem_path = uploaded.path

            if old_bucket and old_path:
                self.storage_service.remove_file(old_bucket, old_path)

        elif remove_image:
            if product.imagem_bucket and product.imagem_path:
                self.storage_service.remove_file(
                    product.imagem_bucket, product.imagem_path
                )

            product.imagem_path = None
            product.imagem_bucket = None

        return await self.repo.update(product)
