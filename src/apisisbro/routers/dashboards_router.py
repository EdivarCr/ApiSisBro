from fastapi import APIRouter, Query
from datetime import date

from apisisbro.core.dependecies import VendaServiceDep

from apisisbro.schemas.venda_schema import (
    DashboardGeralResponse,
    DashboardLucratividadeResponse
)

router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards & Analytics"]
)

@router.get("/geral", response_model=DashboardGeralResponse)
async def obter_dashboard_geral(
    service: VendaServiceDep,
    data_inicio: date | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: date | None = Query(None, description="Data final (YYYY-MM-DD)")
):
    return await service.get_dashboard_geral(data_inicio=data_inicio, data_fim=data_fim)


@router.get("/lucratividade", response_model=DashboardLucratividadeResponse)
async def obter_dashboard_lucratividade(
    service: VendaServiceDep,
    data_inicio: date | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: date | None = Query(None, description="Data final (YYYY-MM-DD)")
):
    return await service.get_dashboard_lucratividade(data_inicio=data_inicio, data_fim=data_fim)