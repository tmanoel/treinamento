# Guia de Testes Manuais

Passo a passo para quem acabou de clonar o projeto e quer verificar, task por task, o que já está implementado. Os comandos assumem o terminal aberto na raiz do repositório (`biblioteca/`).

> Este não é um documento de spec — é um guia operacional. As specs estão nos arquivos numerados `00-` a `06-`.

---

## Pré-requisitos

- Python 3.11+ (o projeto foi desenvolvido em 3.13)
- `pip`
- Opcional: `curl` (geralmente já vem no Windows 10+)

Verifique:

```bash
python --version
pip --version
```

---

## Setup inicial (uma vez)

```bash
pip install -r requirements.txt
```

Isso instala FastAPI, Uvicorn, SQLAlchemy e dependências transitivas.

---

## Subir a API

Em um terminal na raiz do projeto:

```bash
uvicorn app.main:app --reload
```

O `--reload` faz o servidor reiniciar a cada alteração em arquivos `.py` — útil em desenvolvimento. Por padrão escuta em `http://127.0.0.1:8000`.

Deixe esse terminal rodando. **Abra um segundo terminal** para os testes abaixo. Para parar, `Ctrl+C` no primeiro terminal.

---

## T01 — Setup inicial do projeto

**O que a task entrega:** estrutura do projeto (`app/`, `tests/`), FastAPI rodando sob o prefixo `/api` e endpoint `GET /api/health` para health check.

### 1. Health check

**Via navegador:** acesse http://127.0.0.1:8000/api/health

Esperado:
```json
{"status":"ok"}
```

**Via curl:**
```bash
curl -i http://127.0.0.1:8000/api/health
```

Esperado: `HTTP/1.1 200 OK` + corpo `{"status":"ok"}`.

### 2. Confirmar que a API respeita o prefixo `/api` (D07)

```bash
curl -i http://127.0.0.1:8000/health
```

Esperado: `404 Not Found`. A rota só existe sob `/api/health`.

### 3. Documentação automática (Swagger UI)

Acesse http://127.0.0.1:8000/docs

O FastAPI gera automaticamente uma interface onde você pode testar os endpoints sem `curl`. À medida que as próximas tasks (T04–T09) forem implementadas, elas aparecerão aqui.

---

## T02 — Camada de persistência (SQLite + SQLAlchemy)

**O que a task entrega:** banco SQLite (`biblioteca.db`) criado automaticamente no startup, tabela `livros` com todos os campos do design §2, e gerenciamento automático de `created_at` e `updated_at`.

### 1. Confirmar que o banco foi criado

Com o uvicorn rodando, na raiz do projeto:

```bash
ls -la biblioteca.db
```

O arquivo deve existir. Se não existe, reinicie o uvicorn — ele é criado na primeira importação de `app.models`.

### 2. Inspecionar o schema da tabela `livros`

```bash
python -X utf8 -c "import sqlite3; c=sqlite3.connect('biblioteca.db'); print(c.execute(\"SELECT sql FROM sqlite_master WHERE name='livros'\").fetchone()[0])"
```

Esperado:

```sql
CREATE TABLE livros (
        id INTEGER NOT NULL,
        titulo VARCHAR NOT NULL,
        autor VARCHAR NOT NULL,
        editora VARCHAR NOT NULL,
        ano_publicacao INTEGER NOT NULL,
        lido BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        PRIMARY KEY (id)
)
```

> **Nota:** `python -X utf8` força encoding UTF-8 no console do Windows para preservar acentos (ex.: "Anéis" vs. "An�is").

### 3. Inserir um livro de teste via ORM

Como nenhum endpoint `POST /api/livros` existe ainda (vem em T04), usamos a sessão do próprio módulo:

```bash
python -X utf8 -c "
from app.models import SessionLocal, Livro
s = SessionLocal()
l = Livro(titulo='O Senhor dos Anéis', autor='J.R.R. Tolkien', editora='HarperCollins', ano_publicacao=1954)
s.add(l); s.commit(); s.refresh(l)
print('id =', l.id)
print('created_at =', l.created_at)
print('updated_at =', l.updated_at)
print('lido       =', l.lido)
s.close()
"
```

Esperado: `id = 1`, `lido = False`, `created_at` e `updated_at` com timestamps quase idênticos (diferença em microssegundos).

### 4. Consultar os registros

```bash
python -X utf8 -c "
import sqlite3
c = sqlite3.connect('biblioteca.db'); c.row_factory = sqlite3.Row
for r in c.execute('SELECT * FROM livros'):
    print(dict(r))
"
```

### 5. Verificar que `updated_at` muda no UPDATE (e `created_at` não)

```bash
python -X utf8 -c "
import time
from app.models import SessionLocal, Livro
s = SessionLocal()
l = s.query(Livro).first()
antes_created, antes_updated = l.created_at, l.updated_at
time.sleep(1)
l.titulo = 'O Senhor dos Anéis (edição revisada)'
s.commit(); s.refresh(l)
print('created_at mudou?', l.created_at != antes_created)
print('updated_at mudou?', l.updated_at != antes_updated)
"
```

Esperado: `created_at mudou? False`, `updated_at mudou? True`.

### 6. Limpar os registros de teste

```bash
python -X utf8 -c "from app.models import SessionLocal, Livro; s=SessionLocal(); s.query(Livro).delete(); s.commit()"
```

---

## Problemas comuns

### `Device or resource busy` ao remover `biblioteca.db`

Significa que o uvicorn (ou outro processo Python) está com o arquivo aberto. Pare o uvicorn (`Ctrl+C`) antes de deletar.

### Acentos aparecem como `�` no console

Windows. Use `python -X utf8 ...` em vez de `python ...`.

### `ModuleNotFoundError: No module named 'app'`

Rode os comandos a partir da **raiz do projeto** (onde está `requirements.txt`), não de dentro de `app/` ou `docs/`.

### Porta 8000 ocupada

Use outra porta:

```bash
uvicorn app.main:app --reload --port 8001
```

E ajuste as URLs dos testes (`http://127.0.0.1:8001/...`).

---

## Próximas tasks

Este guia será atualizado conforme novas tasks forem implementadas. Ordem sugerida em [06-tasks.md](06-tasks.md):

- T03 — schemas Pydantic
- T04 — `POST /api/livros`
- T05 — `GET /api/livros`
- T06 — `GET /api/livros/{id}`
- T07 — `PATCH /api/livros/{id}`
- T08 — `DELETE /api/livros/{id}`
- T09 — filtros no `GET /api/livros`
- T10 — testes automatizados (`pytest`)
- T11 — servir frontend estático
- T12 — frontend HTML/JS
- T13 — README completo
