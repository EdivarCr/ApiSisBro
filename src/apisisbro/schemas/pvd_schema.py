from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from apisisbro.models.models import TipoZona


class PontoDeVendaCreate(BaseModel):
    id_cliente: int
    name: str = Field(..., max_length=120)
    tipo_zona: TipoZona
    endereco: str
    telefone: str | None = None
    instagram: str | None = None
    google_maps_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class PontoDeVendaUpdate(BaseModel):
    name: str | None = None
    tipo_zona: TipoZona | None = None
    endereco: str | None = None
    telefone: str | None = None
    instagram: str | None = None
    google_maps_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class PontoDeVendaResponse(BaseModel):
    id: int
    id_cliente: int
    name: str
    tipo_zona: TipoZona
    endereco: str
    telefone: str | None
    instagram: str | None
    google_maps_url: str | None
    ultima_reposicao: date | None
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
