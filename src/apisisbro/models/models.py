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


class StatusClientePvd(StrEnum):
    ATIVO = 'ATIVO'
    INATIVO = 'INATIVO'


class FormaPagamento(StrEnum):
    PIX = 'PIX'
    DINHEIRO = 'DINHEIRO'
    CARTAO_CREDITO = 'CARTAO_CREDITO'
    CARTAO_DEBITO = 'CARTAO_DEBITO'


class StatusPagamento(StrEnum):
    PAGO = 'PAGO'
    PENDENTE = 'PENDENTE'  # Para casos de venda "fiado" / a prazo


class TipoVenda(StrEnum):
    VAREJO = 'VAREJO'
    ATACADO = 'ATACADO'


class TipoCliente(StrEnum):
    PESSOA_FISICA = 'PESSOA_FISICA'
    RESTAURANTE = 'RESTAURANTE'
    COMERCIO = 'COMERCIO'


class TipoZona(StrEnum):
    ZONA_SUL = 'ZONA_SUL'
    ZONA_NORTE = 'ZONA_NORTE'
    ZONA_LESTE = 'ZONA_LESTE'
    ZONA_OESTE = 'ZONA_OESTE'


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
    criador_produto: Mapped['User'] = relationship(back_populates='produtos', init=False)

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

    itens_venda: Mapped[list['ItemVenda']] = relationship(
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

    data_entrada: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

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

    quantidade_necessaria: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    produto: Mapped['Produto'] = relationship(
        back_populates='formulas',
        init=False,
        repr=False,
    )

    insumo: Mapped['Insumo'] = relationship(init=False, repr=False)


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
    custo_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.00')
    )
    status: Mapped[StatusLote] = mapped_column(
        sqlEnum(StatusLote, name='status_lote_enum'),
        nullable=False,
        default=StatusLote.ATIVO,
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


@table_registry.mapped_as_dataclass
class Cliente:
    __tablename__ = 'cliente'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tipo: Mapped[TipoCliente] = mapped_column(
        sqlEnum(TipoCliente, name='tipo_cliente_enum'),
        nullable=False,
        index=True,
    )
    identificador: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    endereco: Mapped[str] = mapped_column(
        String(220),
        nullable=False,
    )
    total_compras: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), init=False, default=Decimal('0.00')
    )
    quantidade_compras: Mapped[int] = mapped_column(init=False, default=0)
    ultima_compra: Mapped[date | None] = mapped_column(
        default=None, init=False, nullable=True
    )
    criado_em: Mapped[date] = mapped_column(init=False, default=func.now())
    atualizado_em: Mapped[date] = mapped_column(
        init=False, default=func.now(), onupdate=func.now()
    )
    pvds: Mapped[list['PontoDeVenda']] = relationship(
        init=False, back_populates='cliente', cascade='all, delete-orphan'
    )
    vendas: Mapped[list['Venda']] = relationship(init=False, back_populates='cliente')


@table_registry.mapped_as_dataclass
class PontoDeVenda:
    __tablename__ = 'ponto_de_venda'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    id_cliente: Mapped[int] = mapped_column(ForeignKey('cliente.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_zona: Mapped[TipoZona] = mapped_column(
        sqlEnum(TipoZona, name='tipo_zona_enum'),
        nullable=False,
        index=True,
    )
    endereco: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        # preciso saber se o mesmo numero do cliente deve ser no ponto de venda
    )
    instagram: Mapped[str | None] = mapped_column(
        String(50), default=None, nullable=True, init=True
    )
    google_maps_url: Mapped[str | None] = mapped_column(
        String(500), default=None, nullable=True
    )
    latitude: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    longitude: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    ultima_reposicao: Mapped[date | None] = mapped_column(
        init=False, nullable=True, default=None
    )
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[date] = mapped_column(init=False, default=func.now())
    atualizado_em: Mapped[date] = mapped_column(
        init=False, default=func.now(), onupdate=func.now()
    )
    cliente: Mapped['Cliente'] = relationship(init=False, back_populates='pvds')
    vendas: Mapped['Venda'] = relationship(init=False, back_populates='pvd')


@table_registry.mapped_as_dataclass
class Venda:
    __tablename__ = 'vendas'

    # 1. Campos sem valor padrão (Obrigatórios) vêm primeiro:
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(String(30))
    status_pagamento: Mapped[StatusPagamento] = mapped_column(
        String(20), default=StatusPagamento.PAGO
    )

    # 2. Campos com valor padrão (Opcionais) vêm depois:
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey('cliente.id'), nullable=True, default=None
    )
    pvd_id: Mapped[int | None] = mapped_column(
        ForeignKey('ponto_de_venda.id'), nullable=True, default=None
    )
    tipo_venda: Mapped[TipoVenda] = mapped_column(String(20), default=TipoVenda.ATACADO)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    valor_subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.00')
    )
    valor_desconto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal('0.00')
    )

    data_venda: Mapped[date] = mapped_column(default=date.today)
    data_pagamento: Mapped[date | None] = mapped_column(nullable=True, default=None)
    deleted_at: Mapped[date | None] = mapped_column(nullable=True, default=None)

    # 3. Relacionamentos (Sempre com init=False para saírem do construtor da Dataclass):
    itens: Mapped[list['ItemVenda']] = relationship(
        'ItemVenda', back_populates='venda', cascade='all, delete-orphan', init=False
    )
    cliente: Mapped['Cliente'] = relationship(back_populates='vendas', init=False)
    pvd: Mapped['PontoDeVenda'] = relationship(back_populates='vendas', init=False)


@table_registry.mapped_as_dataclass
class ItemVenda:
    __tablename__ = 'itens_venda'

    # 1. Campos sem valor padrão (Obrigatórios) vêm primeiro:
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    venda_id: Mapped[int] = mapped_column(
        ForeignKey('vendas.id', ondelete='CASCADE'), init=False
    )
    produto_id: Mapped[int] = mapped_column(ForeignKey('produtos.id'))

    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # 2. Campos com valor padrão (Opcionais) vêm depois:
    quantidade: Mapped[int] = mapped_column(default=1)
    unidade_medida: Mapped[UnidadeMedida] = mapped_column(
        String(20), default=UnidadeMedida.UN
    )

    # 3. Relacionamentos (Sempre com init=False por último):
    venda: Mapped['Venda'] = relationship('Venda', back_populates='itens', init=False)
    produto: Mapped['Produto'] = relationship(
        'Produto', back_populates='itens_venda', init=False
    )
