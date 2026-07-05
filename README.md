# ApiSisBro

API RESTful desenvolvida para o gerenciamento de uma plataforma de vendas de pimentas, com controle de produtos, insumos, produção, clientes, pontos de venda e vendas.

O projeto foi desenvolvido para a disciplina de **Projeto Integrado de Software II**, utilizando **Python**, **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **Poetry**, **Docker** e integração com **Supabase** para autenticação e armazenamento de arquivos.

---

## Sobre o projeto

O **ApiSisBro** é uma API backend criada para apoiar a gestão de uma operação comercial de produtos à base de pimenta.

A aplicação permite controlar desde o cadastro dos produtos e insumos até o processo de produção, controle de lotes, cadastro de clientes, pontos de venda e registro de vendas.

Além dos cadastros básicos, o projeto também possui regras de negócio relacionadas a:

* controle de estoque de insumos;
* produção de lotes;
* cálculo de custo de produção;
* validação de estoque disponível;
* registro de vendas;
* cálculo de subtotal, desconto e valor total;
* atualização do histórico de compras dos clientes;
* upload de imagens de produtos.

---

## Funcionalidades

### Autenticação e usuários

* Cadastro de usuários.
* Login por e-mail e senha.
* Login com Google via Supabase Auth.
* Recuperação e redefinição de senha.
* Autenticação por token de acesso.
* Rota para obter dados do usuário autenticado.

### Produtos

* Cadastro de produtos.
* Listagem, busca, atualização e remoção.
* Definição de preço de varejo e atacado.
* Controle de nível de picância.
* Cadastro de informações como alérgenos, validade, peso, estoque mínimo e tipo do produto.
* Upload de imagem do produto.

### Insumos

* Cadastro de insumos.
* Controle de tipo de insumo.
* Controle de unidade de medida.
* Controle de quantidade em estoque.
* Definição de estoque mínimo e custo unitário.

### Entrada de insumos

* Registro de compras/entradas de insumos.
* Atualização do estoque após entrada.
* Controle de quantidade comprada e valor pago.

### Produção

* Registro de produção de lotes.
* Associação entre produto e insumos necessários.
* Geração de código de lote.
* Validação de estoque suficiente para produção.
* Baixa automática dos insumos utilizados.
* Cálculo de custo total e custo unitário do lote.
* Controle de validade e status do lote.

### Clientes

* Cadastro de clientes.
* Controle de tipo de cliente.
* Registro de dados de contato e endereço.
* Histórico de compras.
* Total comprado, quantidade de compras e última compra.

### Pontos de venda

* Cadastro de pontos de venda associados a clientes.
* Controle de endereço, telefone, Instagram e localização.
* Organização por zona.
* Controle de status ativo/inativo.

### Vendas

* Registro de vendas.
* Associação com cliente e ponto de venda.
* Venda no varejo ou atacado.
* Cálculo automático de subtotal, desconto e valor total.
* Validação de estoque disponível por lote.
* Baixa automática dos produtos vendidos.
* Controle de forma e status de pagamento.
* Atualização dos dados de compra do cliente.

---

## Tecnologias utilizadas

| Categoria                     | Tecnologias                                         |
| ----------------------------- | --------------------------------------------------- |
| Linguagem                     | Python 3.12+                                        |
| Framework                     | FastAPI                                             |
| Banco de dados                | PostgreSQL                                          |
| ORM                           | SQLAlchemy                                          |
| Migrações                     | Alembic                                             |
| Gerenciamento de dependências | Poetry                                              |
| Autenticação                  | Supabase Auth                                       |
| Storage                       | Supabase Storage                                    |
| Testes                        | Pytest, Pytest-asyncio, Factory Boy, Testcontainers |
| Qualidade de código           | Ruff                                                |
| Ambiente                      | Docker e Docker Compose                             |

---

## Estrutura do projeto

```text
ApiSisBro/
├── src/
│   └── apisisbro/
│       ├── core/          # Configurações, autenticação e conexão com banco
│       ├── migrations/    # Migrações do Alembic
│       ├── models/        # Modelos do banco de dados
│       ├── repository/    # Camada de acesso aos dados
│       ├── routers/       # Rotas da API
│       ├── schemas/       # Schemas de entrada e saída
│       ├── services/      # Regras de negócio
│       └── app.py         # Arquivo principal da aplicação
├── tests/                 # Testes automatizados
├── compose.yaml           # Configuração Docker Compose
├── dockerfile             # Configuração da imagem Docker
├── pyproject.toml         # Dependências e comandos do projeto
├── alembic.ini            # Configuração do Alembic
└── README.md
```

---

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

* Python 3.12 ou superior;
* Poetry;
* Docker;
* Docker Compose;
* Git.

Para instalar o Poetry:

```bash
pip install poetry
```

---

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/EdivarCr/ApiSisBro.git
cd ApiSisBro
```

### 2. Instalar as dependências

```bash
poetry install
```

### 3. Configurar as variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp env.example .env
```

Depois, configure as variáveis necessárias:

```env
DATABASE_URL="postgresql+psycopg://usuario:senha@localhost:5433/pimenta_drbroa"

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

SUPABASE_URL="https://seu-projeto.supabase.co"
SUPABASE_KEY="sua-chave-do-supabase"
SUPABASE_JWT_SECRET="seu-jwt-secret-do-supabase"

STORAGE_BUCKET_PRODUTOS="produtos"
STORAGE_BUCKET_COMPROVANTES="comprovantes"

MAX_UPLOAD_SIZE_MB=8
```

> Observação: os valores acima são exemplos. Use as credenciais corretas do seu ambiente local ou do seu projeto no Supabase.

---

## Executando com Docker

Para subir o banco de dados, a API e o Adminer:

```bash
docker compose up --build
```

Serviços disponíveis:

| Serviço    | Endereço                    |
| ---------- | --------------------------- |
| API        | http://localhost:8000       |
| Swagger    | http://localhost:8000/docs  |
| ReDoc      | http://localhost:8000/redoc |
| Adminer    | http://localhost:8080       |
| PostgreSQL | localhost:5433              |

Para executar em segundo plano:

```bash
docker compose up -d --build
```

Para parar os containers:

```bash
docker compose down
```

---

## Executando em ambiente de desenvolvimento

Caso prefira rodar a API localmente com Poetry:

### 1. Subir apenas o banco e o Adminer

```bash
docker compose up -d db adminer
```

### 2. Aplicar as migrações

```bash
poetry run task migrate
```

### 3. Iniciar o servidor

```bash
poetry run task run
```

A API ficará disponível em:

```text
http://localhost:8000
```

Documentação interativa:

```text
http://localhost:8000/docs
```

---

## Comandos úteis

| Comando                                     | Descrição                            |
| ------------------------------------------- | ------------------------------------ |
| `poetry run task run`                       | Inicia a API em modo desenvolvimento |
| `poetry run task migrate`                   | Aplica as migrações do banco         |
| `poetry run task makemigrations "mensagem"` | Cria uma nova migração               |
| `poetry run task test`                      | Executa os testes                    |
| `poetry run task lint`                      | Verifica problemas de lint           |
| `poetry run task format`                    | Formata o código                     |

---

## Testes

O projeto utiliza **pytest** para testes automatizados.

Para executar os testes:

```bash
poetry run task test
```

Ao executar esse comando, também é feita a verificação de lint antes dos testes.

---

## Documentação da API

A documentação interativa é gerada automaticamente pelo FastAPI.

Após iniciar o servidor, acesse:

```text
Swagger: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

---

## Principais entidades do sistema

O sistema possui as seguintes entidades principais:

* **User**: usuário da aplicação.
* **Produto**: produto vendido pela plataforma.
* **Insumo**: matéria-prima ou embalagem usada na produção.
* **EntradaInsumo**: registro de compra ou entrada de insumos.
* **ProdutoInsumo**: relação entre produto e seus insumos necessários.
* **Producao**: lote de produção de um produto.
* **Cliente**: cliente comprador.
* **PontoDeVenda**: local de venda associado a um cliente.
* **Venda**: registro de venda.
* **ItemVenda**: item vendido dentro de uma venda.

---

## Regras de negócio implementadas

Algumas das principais regras de negócio presentes na API:

* Um produto possui preço de varejo e preço de atacado.
* Um produto pode ter estoque mínimo, validade, peso e imagem.
* Um insumo possui quantidade em estoque, custo unitário e unidade de medida.
* Ao registrar uma produção, o sistema verifica se há insumos suficientes.
* Ao produzir um lote, o sistema abate os insumos utilizados.
* O custo total e o custo unitário do lote são calculados automaticamente.
* Ao registrar uma venda, o sistema verifica se há estoque disponível.
* A venda pode ser feita no varejo ou atacado.
* O sistema calcula subtotal, desconto e valor total da venda.
* Após a venda, os dados de compra do cliente são atualizados.

---

## Status do projeto

Projeto em desenvolvimento acadêmico.

Funcionalidades principais já implementadas:

* autenticação;
* usuários;
* produtos;
* insumos;
* entrada de insumos;
* produção;
* clientes;
* pontos de venda;
* vendas;
* upload de imagens;
* testes automatizados.

---

## Possíveis melhorias futuras

* Adicionar documentação detalhada dos endpoints.
* Criar exemplos de requisições e respostas.
* Adicionar seed para popular o banco com dados iniciais.
* Melhorar padronização de mensagens de erro.
* Adicionar paginação e filtros em mais rotas.
* Criar pipeline de CI/CD.
* Publicar a API em ambiente de produção.
* Adicionar diagrama do banco de dados.
* Adicionar prints da documentação Swagger no README.

---

## Licença

Este projeto está sob a licença MIT.
