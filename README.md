# 🚀 ApiSisBro

API desenvolvida para a disciplina de **Projeto Integrado de Software II**.  
Utiliza **FastAPI**, **SQLAlchemy** e **Poetry**.

---

## 📖 Sobre o Projeto

API RESTful com autenticação JWT, integração com Supabase Storage e boas práticas de desenvolvimento.

### Funcionalidades

- ✅ CRUD completo de usuários
- ✅ Autenticação JWT
- ✅ Upload de arquivos (Supabase Storage)
- ✅ Documentação interativa (Swagger/ReDoc)

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologias |
|-----------|-------------|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy, Alembic |
| **Autenticação** | JWT (python-jose), bcrypt |
| **Storage** | Supabase Storage |
| **DevOps** | Docker, Docker Compose, Poetry |

---

## 📋 Pré-requisitos

- Python 3.12+
- Poetry
- (Instale o poetry com pip install poetry)
- Docker e Docker Compose
- Git

---

## 📦 Configuração do Ambiente

```bash
# Clonar repositório
git clone https://github.com/EdivarCr/ApiSisBro.git
cd ApiSisBro

# Instalar dependências
poetry install

# Configurar variáveis de ambiente
cp env.example .env
```

Edite o `.env`:

```env
DATABASE_URL=postgresql://pimenta:pimenta123@localhost:5433/apisisbro
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-secreta
SECRET_KEY=sua-chave-jwt
```

---

## 🐳 Execução com Docker

```bash
# Subir banco e adminer
docker compose up -d db adminer
```

| Serviço | Porta | Credenciais |
|---------|-------|-------------|
| PostgreSQL | 5433 | `pimenta` / `pimenta123` |
| Adminer | 8080 | http://localhost:8080 |

---

## 🏃 Servidor de Desenvolvimento

```bash
# Aplicar migrações
poetry run task migrate

# Iniciar servidor
poetry run task run
```

- **API:** http://localhost:8000
- **Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📜 Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `poetry run task run` | Inicia a API |
| `poetry run task migrate` | Aplica migrações |
| `poetry run task makemigrations` | Cria nova migração |
| `poetry run task test` | Executa testes |
| `poetry run task lint` | Verifica código |
| `poetry run task format` | Formata código |
