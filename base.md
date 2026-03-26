pimenta-drbroa-api/ ├
── src/pimenta_drbroa/
│
├
── __init__.py
│
├
── app.py                      # FastAPI app + lifespan
│   │
│
├
── core/                       # Núcleo da aplicação
│   │
├
── __init__.py
│   │
├
── config.py               # Pydantic Settings
│   │
├
── database.py             # SQLAlchemy async engine + session
│   │   └── security.py             # JWT + Argon2 hashing
│   │
│
├
── models/                     # SQLAlchemy Models
│   │
├
── __init__.py             # Base + todos os models
│   │   └── (enums, relacionamentos, indexes)
│   │
│
├
── schemas/                    # Pydantic Schemas
│   │
├
── __init__.py             # Create, Update, Response schemas
│   │   └── (validações, campos calculados)
│   │
│
├
── routers/                    # Endpoints da API
│   │
├
── __init__.py
│   │
├
── auth.py                 # Login, logout, refresh, register
│   │
├
── produtos.py             # CRUD + catálogo público
│   │
├
── clientes.py             # CRUD + histórico
│   │
├
── vendas.py               # CRUD + baixa estoque
│   │
├
── lotes.py                # Registro de produção
│   │
├
── estoque.py              # Consultas + alertas
│   │
├
── pdvs.py                 # CRUD PDVs
│   │
├
── dashboard.py            # Indicadores
│   │   └── relatorios.py           # Relatórios gerenciais
│   │
│
├
── services/                   # Lógica de negócio
│   │
├
── __init__.py
│   │
├
── estoque_service.py      # FIFO, alertas, saldo
│   │   └── venda_service.py        # Processamento de vendas
│   │
│   └── utils/                      # Utilitários
│
├
── __init__.py
│       └── storage.py              # Supabase Storage client
│ ├
── migrations/                     # Alembic migrations
│
├
── env.py                      # Config async
│
├
── script.py.mako              # Template
│   └── versions/                   # Migration files
│ ├
── tests/                          # Pytest + pytest-asyncio
│
├
── conftest.py                 # Fixtures (session, client, auth)
│
├
── test_app.py
│
├
── test_auth.py
│
├
── test_produtos.py
│   └── ...
│ ├
── scripts/
│   └── init-db.sql                 # Seed inicial
│ ├
── .github/workflows/
│
├
── ci.yml                      # Lint, test, build, deploy
│   └── supabase-keepalive.yml      # Ping 12h
│ ├
── pyproject.toml                  # Poetry + Ruff + Pytest + Taskipy ├
── alembic.ini                     # Config Alembic ├
── Dockerfile                      # Multi-stage (dev/prod) ├
── docker-compose.yml              # API + DB + Frontend + Redis ├
── .env.example ├
── .gitignore
└── README.md