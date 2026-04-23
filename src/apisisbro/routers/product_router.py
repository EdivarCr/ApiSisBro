from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.auth import get_curren_user
from apisisbro.core.database import get_session
from apisisbro.models.models import User
from apisisbro.repository.product_repository import ProductRepository
from apisisbro.schemas.schema import (
    FilterProduct,
    ProdutoCreate,
    ProdutoListResponse,
    ProdutoPublic,
    ProdutoUpdate,
)
from apisisbro.services.product_service import ProductService

router = APIRouter(prefix='/produtos', tags=['produtos'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_curren_user)]
Filter = Annotated[FilterProduct, Depends()]


def get_product_server(session: Session) -> ProductService:
    return ProductService(ProductRepository(session))


Product_Service = Annotated[ProductService, Depends(get_product_server)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProdutoPublic)
async def create_product(
    product: ProdutoCreate, service: Product_Service, user: Current_User
):
    return await service.create(product, user)


@router.get('/', status_code=HTTPStatus.OK, response_model=ProdutoListResponse)
async def list_products(
    service: Product_Service,
    limit: int = 10,
    offset: int = 0,
):
    products = await service.list(limit=limit, offset=offset)

    return {'products': list(products)}


@router.get('/pesquisa', status_code=HTTPStatus.OK, response_model=ProdutoListResponse)
async def search_products(service: Product_Service, filter: Filter):
    products = await service.list_by_filter(filter)
    return {'products': products}


@router.patch('/{id}', status_code=HTTPStatus.OK, response_model=ProdutoPublic)
async def patch_product(
    service: Product_Service, id: int, product_patch: ProdutoUpdate,
    user: Current_User
):
    return await service.update(id, product_patch)
