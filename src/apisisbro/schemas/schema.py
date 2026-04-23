from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apisisbro.models.models import TipoProduto


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str = Field(min_length=1, max_length=300)
    tipo: TipoProduto = Field(description='Tipo do Produto')

    preco_varejo: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    preco_atacado: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    nivel_picancia: int = Field(ge=0, le=10)
    alergenicos: str = Field(default='', max_length=255)
    tem_carolina_reaper: bool = Field(default=False)

    imagem_path: str | None = Field(default=None, max_length=255)
    imagem_bucket: str | None = Field(default=None, max_length=50)

    estoque_minimo: int = Field(default=10, ge=0)
    validade_meses: int = Field(default=0, ge=0)
    unidades_por_caixa: int = Field(default=1, ge=1)

    peso_gramas: Decimal = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, min_length=1, max_length=300)
    tipo: TipoProduto

    preco_varejo: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    preco_atacado: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )

    nivel_picancia: int | None = Field(default=None, ge=0, le=10)

    alergenicos: str | None = Field(default=None, max_length=255)
    tem_carolina_reaper: bool | None = None

    imagem_path: str | None = Field(default=None, max_length=255)
    imagem_bucket: str | None = Field(default=None, max_length=50)

    estoque_minimo: int | None = Field(default=None, ge=0)
    validade_meses: int | None = Field(default=None, ge=0)
    unidades_por_caixa: int | None = Field(default=None, ge=1)

    peso_gramas: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    ativo: bool | None = None


class ProdutoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    tipo: TipoProduto

    preco_varejo: Decimal
    preco_atacado: Decimal

    nivel_picancia: int

    alergenicos: str
    tem_carolina_reaper: bool

    imagem_path: str | None

    validade_meses: int
    unidades_por_caixa: int
    peso_gramas: Decimal


class ProdutoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: TipoProduto
    preco_varejo: Decimal
    nivel_picancia: int
    tem_carolina_reaper: bool
    imagem_path: str | None
    url_imagem: str | None = None
    ativo: bool


class ProdutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    tipo: TipoProduto

    preco_varejo: Decimal
    preco_atacado: Decimal

    nivel_picancia: int
    scoville_aprox: int | None

    alergenicos: str
    tem_carolina_reaper: bool

    imagem_bucket: str | None
    imagem_path: str | None

    estoque_minimo: int
    validade_meses: int
    unidades_por_caixa: int
    peso_gramas: Decimal | None

    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterProduct(FilterPage):
    nome: str | None = Field(default=None, min_length=3)
    tipo: TipoProduto | None = Field(default=None)
    tem_carolina_reaper: bool | None = Field(default=None)
    nivel_picancia: int | None = Field(default=None)
    ativo: bool | None = Field(default=None)


class ProdutoListResponse(BaseModel):
    products: list[ProdutoListItem]
    offset: int = 0
    limit: int = 10
