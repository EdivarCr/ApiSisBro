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
    name: str | None = Field(
        ...,
        default=None,
        max_length=120)
    tipo: TipoCliente | None = None
    identificador: str | None = Field(
        ...,
        default=None,
        description='CPF ou CNPJ apenas números')
    telefone: str | None = None
    email: EmailStr | None = None
    endereco: str | None = None


class ClienteResponse(BaseModel):
    id: int
    name: str
    tipo: TipoCliente
    identificador: str
    telefone: str
    email: str
    endereco: str
    total_compras: Decimal
    quantidade_compras: int
    ultima_compra: date | None

    model_config = ConfigDict(from_attributes=True)
