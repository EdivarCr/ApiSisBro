from decimal import Decimal
from http import HTTPStatus

from fastapi import HTTPException

from apisisbro.models.models import EntradaInsumo
from apisisbro.repository.entrada_insumo_repository import EntradaInsumoRepository
from apisisbro.repository.insumo_repository import InsumoRepository
from apisisbro.schemas.producao_schema import EntradaInsumoCreate


class EntradaInsumoService:
    def __init__(self, repo: EntradaInsumoRepository, repoInsumo: InsumoRepository):
        self.repo = repo
        self.repoInsumo = repoInsumo

    async def registrar_entrada(
        self, entradaInsumoCreate: EntradaInsumoCreate, usuario_id: int
    ):
        insumo = await self.repoInsumo.get_by_id(entradaInsumoCreate.insumo_id)

        if insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        quantidade = entradaInsumoCreate.quantidade_comprada
        valor_total = entradaInsumoCreate.valor_total_pago

        entrada = EntradaInsumo(
            insumo_id=insumo.id,
            criado_por_id=usuario_id,
            quantidade_comprada=quantidade,
            valor_total_pago=valor_total,
        )

        estoque_anterior = insumo.quantidade_estoque
        custo_anterior = insumo.custo_unitario

        novo_estoque = estoque_anterior + quantidade
        custo_medio = ((estoque_anterior * custo_anterior) + valor_total) / novo_estoque

        insumo.quantidade_estoque = novo_estoque
        insumo.custo_unitario = custo_medio

        await self.repo.create(entrada)
        await self.repo.update(insumo)

        return entrada

    async def get_all_entrada_insumo(self):
        return await self.repo.get_all()

    async def get_entrada_insumo_by_id(self, entrada_id: int):
        entrada_insumo = await self.repo.get_by_id(entrada_id)

        if entrada_insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        return entrada_insumo

    async def delete(self, entrada_id: int):
        entrada_insumo = await self.repo.get_by_id(entrada_id)

        if entrada_insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        insumo = await self.repoInsumo.get_by_id(entrada_insumo.insumo_id)

        novo_estoque = insumo.quantidade_estoque - entrada_insumo.quantidade_comprada

        if novo_estoque < 0:
            raise ValueError(
            "Não é possível cancelar esta entrada. Os insumos já foram consumidos "
            "em uma produção. O estoque ficaria negativo."
            )
        quantidade = insumo.quantidade_estoque
        custo_unitario = insumo.custo_unitario
        valor_da_entrada = entrada_insumo.valor_total_pago
        if novo_estoque > 0:
            valor_total_atual = quantidade * custo_unitario
            valor_restante = valor_total_atual - valor_da_entrada

            novo_custo = valor_restante / novo_estoque
            insumo.custo_unitario = max(Decimal('0.00'), novo_custo)
        else:
            insumo.custo_unitario = Decimal('0.00')

        insumo.quantidade_estoque = novo_estoque

        await self.repo.delete(entrada_insumo)
        await self.repo.update(insumo)

        return {"message": "Entrada estornada e estoque atualizado com sucesso"}
