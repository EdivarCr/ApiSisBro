from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, Numeric, String, func, text
from sqlalchemy import Enum as sqlEnum
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship, validates

table_registry = registry()


class TipoProduto(StrEnum):
    GELEIA = 'geleia'
    MOLHO = 'molho'
    CONSERVA = 'conserva'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=True)
    supabase_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    produtos: Mapped[list['Produto']] = relationship(
        back_populates='criador_produto', lazy='selectin', init=False
    )


@table_registry.mapped_as_dataclass
class Produto:
    __tablename__ = 'produtos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    criador_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    criador_produto: Mapped['User'] = relationship(
        back_populates='produtos', init=False
    )

    nome: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)

    tipo: Mapped[TipoProduto] = mapped_column(
        sqlEnum(TipoProduto, name='tipo_produto_enum'),
        nullable=False,
        index=True,
    )

    preco_varejo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_atacado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    nivel_picancia: Mapped[int] = mapped_column(nullable=False)

    alergenicos: Mapped[str] = mapped_column(String(255), nullable=False, default='')
    tem_carolina_reaper: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text('false'),
    )

    imagem_bucket: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None
    )
    imagem_path: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )

    estoque_minimo: Mapped[int] = mapped_column(
        nullable=False, default=0, server_default=text('0')
    )
    validade_meses: Mapped[int] = mapped_column(
        nullable=False, default=0, server_default=text('0')
    )
    unidades_por_caixa: Mapped[int] = mapped_column(
        nullable=False, default=1, server_default=text('1')
    )

    peso_gramas: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True, default=None
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text('true'),
        index=True,
    )

    criado_em: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @validates('estoque_minimo')
    def valida_estoque_minimo(self, key, value: int):
        number = 10
        if value < number:
            nome_produto = getattr(self, 'nome', 'Produto Desconhecido')
            raise ValueError(
                f"Erro no '{nome_produto}': O estoque mínimo não pode ser menor que 10."
                f'Valor recebido: {value}'
            )
        return value
