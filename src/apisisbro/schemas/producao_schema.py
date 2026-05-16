from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from apisisbro.models.models import (
    TipoInsumo,
    UnidadeMedida,
)


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


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120, min_length=1)
    tipo: TipoInsumo | None = None
    unidade_de_medida: UnidadeMedida | None = None
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

    model_config = ConfigDict(from_attributes=True)
