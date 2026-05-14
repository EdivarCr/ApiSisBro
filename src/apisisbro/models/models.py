from datetime import date, datetime
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


class UnidadeMedida(StrEnum):
    KG = 'kg'
    G = 'g'
    L = 'l'
    ML = 'ml'
    UN = 'un'


class TipoInsumo(StrEnum):
    MATERIA_PRIMA = 'materia_prima'
    EMBALAGEM = 'embalagem'


class StatusLote(StrEnum):
    ATIVO = 'ATIVO'
    ESGOTADO = 'ESGOTADO'
    VENCIDO = 'VENCIDO'
    CANCELADO = 'CANCELADO'


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

    producoes: Mapped[list['Producao']] = relationship(
        back_populates='produto', init=False
    )

    formulas: Mapped[list['ProdutoInsumo']] = relationship(
        back_populates='produto', init=False
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


@table_registry.mapped_as_dataclass
class Insumo:
    __tablename__ = 'insumo'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tipo: Mapped[TipoInsumo] = mapped_column(
        sqlEnum(TipoInsumo, name='tipo_insumo_enum'), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    unidade_de_medida: Mapped[UnidadeMedida] = mapped_column(
        sqlEnum(UnidadeMedida, name='unidade_medida_enum'),
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quantidade_estoque: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), default=Decimal('0.000')
    )
    estoque_minimo: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), default=Decimal('0.000')
    )
    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.000')
    )

    entradas: Mapped[list['EntradaInsumo']] = relationship(
        back_populates='insumo', init=False
    )


@table_registry.mapped_as_dataclass
class EntradaInsumo:
    __tablename__ = 'entrada_insumo'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    insumo_id: Mapped[int] = mapped_column(
        ForeignKey('insumo.id', ondelete='RESTRICT'), nullable=False
    )
    criado_por_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    quantidade_comprada: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    valor_total_pago: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    data_entrada: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    insumo: Mapped['Insumo'] = relationship(back_populates='entradas', init=False)


@table_registry.mapped_as_dataclass
class ProdutoInsumo:
    __tablename__ = 'produto_insumo'

    produto_id: Mapped[int] = mapped_column(
        ForeignKey('produtos.id', ondelete='CASCADE'), primary_key=True
    )
    insumo_id: Mapped[int] = mapped_column(
        ForeignKey('insumo.id', ondelete='RESTRICT'), primary_key=True
    )

    quantidade_necessaria: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False
    )

    produto: Mapped['Produto'] = relationship(back_populates='formulas', init=False)

    insumo: Mapped['Insumo'] = relationship(init=False)


@table_registry.mapped_as_dataclass
class Producao:
    __tablename__ = 'lote_producao'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    codigo_lote: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    produto_id: Mapped[int] = mapped_column(
        ForeignKey('produtos.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    criado_por_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    validade: Mapped[date] = mapped_column(nullable=False)
    quantidade: Mapped[int] = mapped_column(default=0)

    fabricacao: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    custo_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.00')
    )
    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.00')
    )
    status: Mapped[StatusLote] = mapped_column(
        sqlEnum(StatusLote, name='status_lote_enum'),
        nullable=False,
        default=StatusLote.ATIVO
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    produto: Mapped['Produto'] = relationship(
        back_populates='producoes',
        init=False,
    )
