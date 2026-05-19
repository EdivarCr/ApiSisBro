from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from apisisbro.models.models import StatusLote, TipoInsumo, UnidadeMedida


class InsumoBase(BaseModel):
    nome: str = Field(max_length=120, description='Nome do ingrediente ou embalagem')
    tipo: TipoInsumo = Field(description='Tipo do Produto')
    unidade_de_medida: UnidadeMedida
    estoque_minimo: Decimal = Field(
        default=Decimal('0.000'),
        ge=Decimal('0.000'),
        max_digits=10,
        decimal_places=3,
    )


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterInsumo(FilterPage):
    nome: str | None = Field(default=None, min_length=3)
    tipo: TipoInsumo | None = Field(default=None)
    ativo: bool | None = Field(default=None)


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120, min_length=1)
    tipo: TipoInsumo | None = None
    estoque_minimo: Decimal | None = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=3,
    )
    ativo: bool | None = None


class InsumoResponse(InsumoBase):
    id: int
    quantidade_estoque: Decimal = Field(max_digits=10, decimal_places=3)
    custo_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class InsumoListResponse(BaseModel):
    insumos: list[InsumoResponse]
    offset: int = 0
    limit: int = 10


class EntradaInsumoCreate(BaseModel):
    insumo_id: int
    quantidade_comprada: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    valor_total_pago: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class EntradaInsumoResponse(EntradaInsumoCreate):
    id: int
    criado_por_id: int
    data_entrada: datetime
    quantidade_comprada: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class EntradaInsumoListResponse(BaseModel):
    entradaInsumo: list[EntradaInsumoResponse]
    offset: int = 0
    limit: int = 10


class FilterEntradaInsumo(FilterPage):
    insumo_nome: str | None = Field(default=None, min_length=3)
    insumo_tipo: TipoInsumo | None = None
    insumo_ativo: bool | None = None
    data_entrada: date | None = None


class ProducaoBase(BaseModel):
    produto_id: int
    quantidade: int = Field(
        gt=0, description='Quantidade de unidades/frascos produzidos'
    )


class ProducaoCreate(ProducaoBase):
    pass


class ProducaoResponse(ProducaoCreate):
    id: int
    codigo_lote: str
    criado_por_id: int
    validade: date
    custo_total: Decimal
    custo_unitario: Decimal
    status: StatusLote
    fabricacao: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ProducaoListResponse(BaseModel):
    producao: list[ProducaoResponse]
    offset: int = 0
    limit: int = 10
