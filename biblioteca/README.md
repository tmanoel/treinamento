# Biblioteca Pessoal

API REST + frontend simples para cadastrar e consultar livros pessoais. Permite marcar livros como lidos, filtrar por campos e editar/remover.

Construído como exercício de **Spec-Driven Development**: toda decisão sai da especificação em [docs/](docs/). Comece por [00-constitution.md](docs/00-constitution.md) e [01-overview.md](docs/01-overview.md).

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + SQLite (arquivo `biblioteca.db` criado automaticamente)
- Pydantic v2 para validação de entrada
- HTML/CSS/JavaScript vanilla para o frontend

## Instalação

```bash
git clone <url-do-repo>
cd biblioteca

python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Executar a API

```bash
uvicorn app.main:app --reload
```

A aplicação sobe em `http://127.0.0.1:8000`.

- Frontend: abra `http://127.0.0.1:8000/` no navegador.
- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`.
- Health check: `GET http://127.0.0.1:8000/api/health`.

O arquivo `biblioteca.db` é criado na raiz na primeira chamada e persiste entre execuções. Para começar do zero, pare o servidor e apague o arquivo.

## Frontend

Em `http://127.0.0.1:8000/` você encontra:

- **Cadastrar livro** — formulário com `titulo`, `autor`, `editora`, `ano_publicacao` e checkbox "Já li este livro".
- **Filtros** — busca por substring (título/autor/editora), igualdade (ano) e select (lido).
- **Tabela de livros cadastrados** — checkbox "Lido" dispara atualização direto; botão **Editar** abre edição inline na própria linha; **Remover** pede confirmação.

Todas as mensagens são em português e retornadas pela API.

## Exemplos de uso

Base URL: `http://127.0.0.1:8000/api`.

### Health

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok"}
```

### Cadastrar livro

```bash
curl -X POST http://127.0.0.1:8000/api/livros \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "O Hobbit",
    "autor": "J.R.R. Tolkien",
    "editora": "HarperCollins",
    "ano_publicacao": 1937,
    "lido": true
  }'
# 201 Created → retorna o livro com id, created_at e updated_at
```

### Listar livros (com filtros opcionais)

```bash
# Todos
curl http://127.0.0.1:8000/api/livros

# Filtrar por substring (case-insensitive)
curl "http://127.0.0.1:8000/api/livros?titulo=hobbit"
curl "http://127.0.0.1:8000/api/livros?autor=tolkien&editora=harper"

# Filtrar por ano exato
curl "http://127.0.0.1:8000/api/livros?ano_publicacao=1937"

# Filtrar por lido (aceita true/false, case-insensitive)
curl "http://127.0.0.1:8000/api/livros?lido=true"
```

### Buscar por id

```bash
curl http://127.0.0.1:8000/api/livros/1
# 200 OK ou 404 Not Found
```

### Atualizar parcialmente (edição e/ou marcar lido)

Envie só os campos que mudaram:

```bash
# Marcar como lido
curl -X PATCH http://127.0.0.1:8000/api/livros/1 \
  -H "Content-Type: application/json" \
  -d '{"lido": true}'

# Alterar campos em lote
curl -X PATCH http://127.0.0.1:8000/api/livros/1 \
  -H "Content-Type: application/json" \
  -d '{"editora": "Allen & Unwin", "ano_publicacao": 1937}'
```

Body vazio (`{}`) retorna `400`. Combinação `titulo`+`autor` já usada por outro livro retorna `409`.

### Remover livro

```bash
curl -X DELETE http://127.0.0.1:8000/api/livros/1 -i
# 204 No Content (sem corpo)
```

## Testes automatizados

```bash
pytest
```

A suíte usa `TestClient` do FastAPI com SQLite em memória (isolado por teste via `StaticPool`). Cobre US01–US07 + health. Ver detalhes em [tests/test_livros.py](tests/test_livros.py) e no guia manual [docs/guia-de-testes.md](docs/guia-de-testes.md).

## Estrutura do projeto

```
app/
  main.py          # FastAPI app, monta router e StaticFiles
  models.py        # SQLAlchemy engine, Base, modelo Livro
  schemas.py       # Pydantic (LivroCreate, LivroUpdate, LivroResponse)
  repository.py    # Acesso a dados (sem regras de negócio)
  service.py       # Regras de negócio (duplicata, validações cruzadas)
  router.py        # Endpoints REST sob /api
  static/          # Frontend (index.html, style.css, script.js)
tests/
  conftest.py      # Fixture do TestClient com DB in-memory
  test_livros.py   # Testes de integração da API
docs/              # Spec do projeto (constitution, requisitos, user stories, design, endpoints, tasks)
requirements.txt
biblioteca.db      # Criado em runtime (gitignored)
```

Camadas: `Request → Router → Service → Repository → Database`. Pydantic valida na borda do Router; regras de negócio ficam no Service.

## Documentação

A pasta [docs/](docs/) é a fonte da verdade do projeto:

- [00-constitution.md](docs/00-constitution.md) — princípios não-negociáveis (Spec-Driven Development)
- [01-overview.md](docs/01-overview.md) — escopo e o que está fora
- [02-requisitos.md](docs/02-requisitos.md) — RFs, RNFs e regras de negócio
- [03-user-stories.md](docs/03-user-stories.md) — US01–US07 com critérios de aceitação
- [04-design.md](docs/04-design.md) — stack, modelo de dados, decisões arquiteturais
- [05-endpoints.md](docs/05-endpoints.md) — contrato HTTP completo (request/response/status)
- [06-tasks.md](docs/06-tasks.md) — decomposição em tasks T01–T13
- [guia-de-testes.md](docs/guia-de-testes.md) — roteiro de verificação manual por task
