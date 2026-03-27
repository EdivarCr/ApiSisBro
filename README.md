🚀 Guia de Desenvolvimento - ApiSisBro
Este documento orienta a configuração do ambiente para que todos os membros do grupo trabalhem com as mesmas versões de bibliotecas e ferramentas.

1. Pré-requisitos
Antes de começar, instale:

Python 3.12+

Poetry (Gerenciador de pacotes)

Docker & Docker Compose

2. Configuração Inicial
Clonar e Instalar
Bash
git clone https://github.com/EdivarCr/ApiSisBro.git
cd ApiSisBro
poetry install
O comando poetry install instalará todas as dependências do projeto (FastAPI, SQLAlchemy, etc.) e as ferramentas de desenvolvimento (Pytest, Ruff, Taskipy) em um ambiente virtual isolado.

Variáveis de Ambiente
Crie o arquivo .env para que o sistema reconheça as configurações do banco de dados e do Supabase:

Bash
cp env.example .env
Edite o .env com as chaves do Supabase se necessário.

3. Executando o Projeto
Passo 1: Subir o Banco de Dados (Docker)
Para rodar o PostgreSQL e o Adminer (interface para o banco), utilize:

Bash
docker compose up -d db adminer
O banco estará disponível em localhost:5433.

O Adminer estará em localhost:8080.

Passo 2: Rodar a API
Utilize o comando pré-configurado via taskipy:

Bash
poetry run task run
Acesse a documentação interativa em: http://localhost:8000/docs.

4. Comandos de Desenvolvimento (Taskipy)
Para facilitar o dia a dia, use os seguintes comandos através do poetry run task:

task run: Inicia o servidor FastAPI em modo de desenvolvimento.

task migrate: Aplica todas as migrações pendentes ao banco de dados.

task makemigrations: Cria uma nova revisão do banco (Alembic) após você alterar os modelos.

task test: Executa a suíte de testes com relatório de cobertura.

task lint: Verifica erros de estilo no código usando o Ruff.

task format: Corrige automaticamente a formatação do código.

💡 Boas Práticas para o Grupo
Dependências: Se precisar instalar uma biblioteca nova, use poetry add nome-da-lib. Não use pip.

Ambiente: O projeto utiliza Python 3.12. Garanta que seu Poetry esteja usando esta versão.

Migrações: Sempre que alterar um arquivo em models/, lembre-se de rodar o task makemigrations e commitar o arquivo gerado na pasta versions/.
