from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Form
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

    estoque_minimo: int = Field(default=10, ge=0)
    validade_meses: int = Field(default=0, ge=0)
    unidades_por_caixa: int = Field(default=1, ge=1)

    peso_gramas: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
        )


class ProdutoCreate(ProdutoBase):

    @classmethod
    def as_form(
        cls,
        nome: Annotated[str, Form(min_length=1, max_length=120)],
        descricao: Annotated[str, Form(min_length=1, max_length=300)],
        tipo: Annotated[TipoProduto, Form()],
        preco_varejo: Annotated[Decimal, Form(gt=0)],
        preco_atacado: Annotated[Decimal, Form(gt=0)],
        nivel_picancia: Annotated[int, Form(ge=0, le=10)],
        alergenicos: Annotated[str, Form(max_length=255)] = '',
        tem_carolina_reaper: Annotated[bool, Form()] = False,
        estoque_minimo: Annotated[int, Form(ge=0)] = 10,
        validade_meses: Annotated[int, Form(ge=0)] = 0,
        unidades_por_caixa: Annotated[int, Form(ge=1)] = 1,
        peso_gramas: Annotated[Decimal | None, Form(gt=0)] = None,
    ) -> 'ProdutoCreate':
        return cls(
            nome=nome,
            descricao=descricao,
            tipo=tipo,
            preco_varejo=preco_varejo,
            preco_atacado=preco_atacado,
            nivel_picancia=nivel_picancia,
            alergenicos=alergenicos,
            tem_carolina_reaper=tem_carolina_reaper,
            estoque_minimo=estoque_minimo,
            validade_meses=validade_meses,
            unidades_por_caixa=unidades_por_caixa,
            peso_gramas=peso_gramas,
        )


class ProdutoUpdate(BaseModel):
    # 1. Declarar os atributos do modelo como opcionais
    nome: str | None = None
    descricao: str | None = None
    tipo: str | None = None # Use seu TipoProduto aqui se for um Enum
    preco_varejo: Decimal | None = None
    preco_atacado: Decimal | None = None
    nivel_picancia: int | None = None
    alergenicos: str | None = None
    tem_carolina_reaper: bool | None = None
    estoque_minimo: int | None = None
    validade_meses: int | None = None
    unidades_por_caixa: int | None = None
    peso_gramas: Decimal | None = None

    @classmethod
    def as_form(
        cls,
        # 2. Todos os campos do Form() PRECISAM ter "= None" no final para não serem obrigatórios
        nome: Annotated[str | None, Form(min_length=1, max_length=120)] = None,
        descricao: Annotated[str | None, Form(min_length=1, max_length=300)] = None,
        tipo: Annotated[str | None, Form()] = None,
        preco_varejo: Annotated[Decimal | None, Form(gt=0)] = None,
        preco_atacado: Annotated[Decimal | None, Form(gt=0)] = None,
        nivel_picancia: Annotated[int | None, Form(ge=0, le=10)] = None,
        alergenicos: Annotated[str | None, Form(max_length=255)] = None,
        tem_carolina_reaper: Annotated[bool | None, Form()] = None,
        estoque_minimo: Annotated[int | None, Form(ge=0)] = None,
        validade_meses: Annotated[int | None, Form(ge=0)] = None,
        unidades_por_caixa: Annotated[int | None, Form(ge=1)] = None,
        peso_gramas: Annotated[Decimal | None, Form(gt=0)] = None,
    ) -> 'ProdutoUpdate':

        # 3. Coletamos tudo o que veio do formulário
        valores_recebidos = {
            "nome": nome,
            "descricao": descricao,
            "tipo": tipo,
            "preco_varejo": preco_varejo,
            "preco_atacado": preco_atacado,
            "nivel_picancia": nivel_picancia,
            "alergenicos": alergenicos,
            "tem_carolina_reaper": tem_carolina_reaper,
            "estoque_minimo": estoque_minimo,
            "validade_meses": validade_meses,
            "unidades_por_caixa": unidades_por_caixa,
            "peso_gramas": peso_gramas,
        }

        # 4. O GRANDE TRUQUE: Filtramos para manter APENAS o que o usuário preencheu de verdade
        # Isso garante que o exclude_unset=True na sua rota vai funcionar perfeitamente!
        valores_preenchidos = {key: value for key, value in valores_recebidos.items()
                            if value is not None}

        # Retorna o modelo preenchido apenas com as alterações
        return cls(**valores_preenchidos)


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
    tipo: TipoProduto
    preco_varejo: Decimal
    preco_atacado: Decimal
    nivel_picancia: int
    tem_carolina_reaper: bool
    imagem_path: str | None
    imagem_bucket: str | None = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


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
