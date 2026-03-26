# ApiSisBro

API para a cadeira de Projeto Integrado de Software 2.

---

## 🚀 Como rodar a aplicação (passo a passo)

### 1. Pré-requisitos

Certifique-se de ter instalado:

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/downloads/)  
- [pip](https://pip.pypa.io/en/stable/)

### 2. Clone o repositório

Abra o terminal e execute:

```bash
git clone https://github.com/EdivarCr/ApiSisBro.git
cd ApiSisBro
```

### 3. Crie e ative o ambiente virtual

No terminal digite:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows**
  ```bash
  venv\Scripts\activate
  ```
- **Linux/Mac**
  ```bash
  source venv/bin/activate
  ```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure variáveis de ambiente

Se existir um arquivo `.env.example`, copie para `.env` e ajuste as variáveis conforme necessário:

```bash
cp .env.example .env
# edite .env com suas configurações, se necessário
```

> Caso não tenha `.env.example`, pergunte ao responsável do grupo as variáveis necessárias.

### 6. Execute as migrações (se aplicável)

Se o projeto usar banco de dados/migrações (exemplo com Alembic):

```bash
alembic upgrade head
```
*Apenas se o projeto pedir. Se não usar migrations, pule esse passo.*

### 7. Rode o sistema

O comando pode variar, mas geralmente:

```bash
python main.py
```
ou (se for FastAPI/Uvicorn):

```bash
uvicorn main:app --reload
```

Acesse no navegador ou via Postman:
```
http://localhost:8000
```
ou conforme porta que aparece no seu terminal.

### 8. Testando a API

Se houver documentação automática, acesse:
```
http://localhost:8000/docs
```
ou
```
http://localhost:8000/redoc
```

---

## 💡 Dicas

- Ative o ambiente virtual sempre que for trabalhar no projeto!
- Se der erro de módulo, confira se as dependências estão instaladas no ambiente virtual.
- Combine com o grupo antes de mexer na branch principal (`main`).

---

## 🛠️ Scripts Úteis

- `pip install -r requirements.txt` — Instala dependências
- `uvicorn main:app --reload` — Sobe servidor em modo desenvolvimento (se usar FastAPI)
- `pytest` — Executa os testes automatizados (se houver)

---

## 📄 Licença

MIT — Sinta-se livre para usar e aprimorar!

---

Qualquer dúvida, chame no grupo ou abra uma issue no GitHub!