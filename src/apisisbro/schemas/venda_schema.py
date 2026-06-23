from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apisisbro.models.models import (
    FormaPagamento,
    StatusPagamento,
    TipoVenda,
    UnidadeMedida,
)


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int
    unidade_medida: UnidadeMedida = UnidadeMedida.UN


class VendaCreate(BaseModel):
    cliente_id: int
    pvd_id: int | None = None
    forma_pagamento: FormaPagamento | None = None
    status_pagamento: StatusPagamento
    tipo_venda: TipoVenda
    desconto: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    data_venda: date
    data_pagamento: date | None = None
    itens: list[ItemVendaCreate] = Field(..., min_length=1)


class VendaResponse(BaseModel):
    id: int
    cliente_id: int
    pvd_id: int | None = None
    forma_pagamento: FormaPagamento | None = None
    status_pagamento: StatusPagamento
    tipo_venda: TipoVenda
    valor_total: Decimal
    valor_subtotal: Decimal
    valor_desconto: Decimal = Field(default=Decimal('0.00'), ge=0)
    data_venda: date
    data_pagamento: date | None = None

    model_config = ConfigDict(from_attributes=True)


class ItemVendaResponse(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    valor_unitario: Decimal


class ListVendaResponse(BaseModel):
    itens: list[VendaResponse] = []
    limit: int = 10
    offset: int = 0


class ListItemVendaResponse(VendaResponse):
    itens: list[ItemVendaResponse] = []


class VendaUpdate(BaseModel):
    forma_pagamento: FormaPagamento | None = None
    status_pagamento: StatusPagamento | None = None
    desconto: Decimal | None = Field(default=None, ge=0, le=100)
    data_pagamento: date | None = None
    cliente_id: int | None = None
    pvd_id: int | None = None
    tipo_venda: TipoVenda | None = None


class ItemVendaUpdate(BaseModel):
    produto_id: int | None = None
    quantidade: int | None = None
    valor_unitario: Decimal | None = None


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterVenda(FilterPage):
    data_inicio: date | None = None
    data_fim: date | None = None
    status_pagamento: StatusPagamento | None = None
    pvd_id: int | None = None
    cliente_id: int | None = None
    forma_pagamento: FormaPagamento | None = None
    tipo_venda: TipoVenda | None = None
