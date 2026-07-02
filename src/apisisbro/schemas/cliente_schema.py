from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apisisbro.models.models import TipoCliente


class ClienteCreate(BaseModel):
    name: str = Field(..., max_length=120)
    tipo: TipoCliente
    identificador: str = Field(..., description='CPF ou CNPJ apenas números')
    telefone: str
    email: EmailStr
    endereco: str


class ClienteUpdate(ClienteCreate):
    name: str | None = Field(default=None, max_length=120)
    tipo: TipoCliente | None = None
    identificador: str | None = Field(
        default=None, description='CPF ou CNPJ apenas números'
    )
    telefone: str | None = None
    email: EmailStr | None = None
    endereco: str | None = None

class ClienteVendaResponse(BaseModel):
    id: int
    valor_total: Decimal
    data_venda: date
    status_pagamento: str
    tipo_venda: str
    
    model_config = ConfigDict(from_attributes=True)

class ClienteResponse(BaseModel):
    id: int
    name: str
    tipo: TipoCliente
    identificador: str
    telefone: str
    email: str
    endereco: str
    total_compras: Decimal = Field(default=Decimal('0.00'), examples=[Decimal('0.00')])
    quantidade_compras: int = Field(default=0)
    ultima_compra: date | None = Field(default=None, examples=[None])

    model_config = ConfigDict(from_attributes=True)

class ClienteDetailResponse(ClienteResponse):
    vendas: list[ClienteVendaResponse] = []

class ClientePaginationResponse(BaseModel):
    costumers: list[ClienteResponse]
    offset: int
    limit: int


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterClienteResponse(FilterPage):
    name: str | None = Field(default=None, min_length=3)
    tipo: TipoCliente | None = None
    identificador: str | None = Field(default=None, min_length=3)
    endereco: str | None = Field(default=None, min_length=3)
