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

    async def create(
            self, product: ProdutoCreate, user: User, image: UploadFile
            ) -> Produto:
        existing = await self.repo.get_product_by_name(product.nome)

        if existing is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='already exists'
            )

        db_product = Produto(**product.model_dump(), criador_id=user.id)
        created = await self.repo.create(db_product)

        if image is None:
            return created

        try:
            uploaded = await self.storage_service.upload_product_image(
                file=image,
                product_id=created.id
            )
            created = await self.repo.update_image(
                product=created,
                bucket=uploaded.bucket,
                path=uploaded.path,
            )

            return created

        except Exception:
            # Como a imagem é parte obrigatória da criação neste fluxo,
            # desfaz a criação do produto se o upload falhar.
            await self.repo.delete(created)
            raise

    async def list(self, limit: int = 10, offset: int = 0) -> Sequence[Produto]:
        return await self.repo.get_all(limit, offset)

    async def list_by_filter(self, filter: FilterProduct) -> Sequence[Produto]:
        return await self.repo.get_product_by_filter(filter)

    async def update(self, produto_id: int, produto_patch: ProdutoUpdate,
                     imagem: UploadFile | None) -> Produto:
        product = await self.repo.get_by_id(produto_id)

        if product is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        for field, value in produto_patch.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        if imagem is not None:
            old_bucket = product.imagem_bucket
            old_path = product.imagem_path

            uploaded = await self.storage_service.upload_product_image(
                file=imagem,
                product_id=product.id
            )

            product.imagem_bucket = uploaded.bucket
            product.imagem_path = uploaded.path

            if old_bucket and old_path:
                self.storage_service.remove_file(old_bucket, old_path)

        return await self.repo.update(product)
