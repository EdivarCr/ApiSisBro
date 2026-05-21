from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apisisbro.models.models import TipoProduto


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class ProdutoInsumoCreate(BaseModel):
    insumo_id: int
    quantidade_necessaria: Decimal = Field(gt=0, max_digits=10, decimal_places=3)


class ProdutoInsumoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insumo_id: int
    quantidade_necessaria: Decimal


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str = Field(min_length=1, max_length=300)
    tipo: TipoProduto = Field(description='Tipo do Produto')

    preco_varejo: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    preco_atacado: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    nivel_picancia: int = Field(ge=0, le=10)
    alergenicos: str = Field(default='', max_length=255)
    tem_carolina_reaper: bool = Field(default=False)

    estoque_minimo: int = Field(default=10, ge=0)
    validade_meses: int = Field(default=0, ge=0)
    unidades_por_caixa: int = Field(default=1, ge=1)

    peso_gramas: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )


class ProdutoCreate(ProdutoBase):
    formulas: list[ProdutoInsumoCreate] = Field(min_length=1)


class ProdutoUpdate(BaseModel):
    # 1. Declarar os atributos do modelo como opcionais
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, min_length=1, max_length=300)
    tipo: str | None = None  # Se estiver usando o Enum TipoProduto, coloque aqui
    preco_varejo: Decimal | None = Field(default=None, gt=0)
    preco_atacado: Decimal | None = Field(default=None, gt=0)
    nivel_picancia: int | None = Field(default=None, ge=0, le=10)
    alergenicos: str | None = Field(default=None, max_length=255)
    tem_carolina_reaper: bool | None = None
    estoque_minimo: int | None = Field(default=None, ge=0)
    validade_meses: int | None = Field(default=None, ge=0)
    unidades_por_caixa: int | None = Field(default=None, ge=1)
    peso_gramas: Decimal | None = Field(default=None, gt=0)
    ativo: bool | None = None

    formulas: list[ProdutoInsumoCreate] | None = None


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
    peso_gramas: Decimal | None


class ProdutoListItemAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    tipo: TipoProduto
    preco_varejo: Decimal
    preco_atacado: Decimal
    nivel_picancia: int
    tem_carolina_reaper: bool
    imagem_path: str | None
    imagem_bucket: str | None = None
    alergenicos: str | None = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    validade_meses: int
    unidades_por_caixa: int
    peso_gramas: Decimal | None
    estoque_minimo: int | None = None
    formulas: list[ProdutoInsumoResponse] = Field(default_factory=list)


class ProdutoListItemPublic(BaseModel):
    nome: str
    tipo: TipoProduto
    preco_varejo: Decimal
    preco_atacado: Decimal
    nivel_picancia: int
    tem_carolina_reaper: bool
    imagem_url: str | None = None


class ProdutoOut(ProdutoBase):
    id: int
    imagem_path: str | None = None
    imagem_bucket: str | None = None
    imagem_url: str | None = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {'from_attributes': True}


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterProduct(FilterPage):
    nome: str | None = Field(default=None, min_length=3)
    tipo: TipoProduto | None = Field(default=None)
    tem_carolina_reaper: bool | None = Field(default=None)
    nivel_picancia: int | None = Field(default=None)
    ativo: bool | None = Field(default=None)


class ProdutoListResponseAdmin(BaseModel):
    products: list[ProdutoListItemAdmin]
    offset: int = 0
    limit: int = 10


class ProdutoListResponsePublic(BaseModel):
    products: list[ProdutoListItemPublic]
    offset: int = 0
    limit: int = 10


class UploadedImage(BaseModel):
    bucket: str
    path: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    redirect_url: str = 'http://localhost:5173/reset-password'


class ResetPasswordRequest(BaseModel):
    access_token: str
    refresh_token: str
    new_password: str
