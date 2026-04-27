from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.auth import get_curren_user
from apisisbro.core.database import get_session
from apisisbro.models.models import User
from apisisbro.repository.product_repository import ProductRepository
from apisisbro.schemas.schema import (
    FilterProduct,
    ProdutoCreate,
    ProdutoListResponseAdmin,
    ProdutoOut,
    ProdutoUpdate,
)
from apisisbro.services.product_service import ProductService
from apisisbro.services.storage_service import StorageService

router = APIRouter(prefix='/produtos', tags=['produtos'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_curren_user)]
Filter = Annotated[FilterProduct, Depends()]
Product_Create = Annotated[ProdutoCreate, Depends(ProdutoCreate.as_form)]


def get_product_server(session: Session) -> ProductService:
    return ProductService(ProductRepository(session), StorageService())


Product_Service = Annotated[ProductService, Depends(get_product_server)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProdutoOut)
async def create_product(
    product: Product_Create, service: Product_Service, user: Current_User,
    image: Annotated[UploadFile | None, File()] = None,
    ):
    return await service.create(product, user, image)


@router.get(
        '/dashboard_admin',
        status_code=HTTPStatus.OK,
        response_model=ProdutoListResponseAdmin)
async def list_products_admin(
    service: Product_Service,
    limit: int = 10,
    offset: int = 0,
):
    products = await service.list(limit=limit, offset=offset)

    return {'products': list(products)}


@router.get('/pesquisa', status_code=HTTPStatus.OK,
            response_model=ProdutoListResponseAdmin)
async def search_products(service: Product_Service, filter: Filter):
    products = await service.list_by_filter(filter)
    return {'products': products}


@router.patch('/{id}', status_code=HTTPStatus.OK, response_model=ProdutoOut)
async def patch_product(
    service: Product_Service, id: int, product_patch: ProdutoUpdate,
    user: Current_User, image: Annotated[UploadFile | None, File()] = None,
):
    return await service.update(id, product_patch, image)
