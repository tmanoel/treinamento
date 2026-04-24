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

## T03 — Schemas de validação (Pydantic)

**O que a task entrega:** schemas `LivroCreate`, `LivroUpdate` e `LivroResponse` em [app/schemas.py](../app/schemas.py), validando tipos, faixa de `ano_publicacao` (RN04), strings não vazias (RN05) e serializando `created_at`/`updated_at` em ISO 8601 UTC com sufixo `Z`.

Como nenhum endpoint consome esses schemas ainda (vem a partir de T04), os testes abaixo exercitam as classes diretamente via Python.

### 1. Happy path do LivroCreate

```bash
python -X utf8 -c "
from app.schemas import LivroCreate
l = LivroCreate(titulo=' O Hobbit ', autor='Tolkien', editora='HarperCollins', ano_publicacao=1937)
print(l)
"
```

Esperado: `titulo='O Hobbit'` (espaços das bordas removidos), `lido=False` (default RN02).

### 2. Cada mensagem de erro (LivroCreate)

```bash
python -X utf8 -c "
from pydantic import ValidationError
from app.schemas import LivroCreate

def tentar(**kw):
    try:
        LivroCreate(**kw)
    except ValidationError as e:
        for err in e.errors():
            print('  -', err['msg'].replace('Value error, ', ''))

print('titulo vazio:');         tentar(titulo='', autor='A', editora='E', ano_publicacao=2000)
print('titulo só espaços:');    tentar(titulo='   ', autor='A', editora='E', ano_publicacao=2000)
print('ano < 1400:');           tentar(titulo='T', autor='A', editora='E', ano_publicacao=1000)
print('ano > ano atual:');      tentar(titulo='T', autor='A', editora='E', ano_publicacao=2099)
print('ano como string:');      tentar(titulo='T', autor='A', editora='E', ano_publicacao='2000')
print('lido como string:');     tentar(titulo='T', autor='A', editora='E', ano_publicacao=2000, lido='true')
"
```

Esperado (mensagens em português):

```
titulo vazio:
  - titulo é obrigatório
titulo só espaços:
  - titulo é obrigatório
ano < 1400:
  - ano_publicacao deve ser um número inteiro entre 1400 e 2026
ano > ano atual:
  - ano_publicacao deve ser um número inteiro entre 1400 e 2026
ano como string:
  - ano_publicacao deve ser um número inteiro entre 1400 e 2026
lido como string:
  - Input should be a valid boolean
```

> O `2026` na mensagem é interpolado em runtime via `datetime.now(tz=UTC).year`. Se o ano atual mudar, a mensagem acompanha.
>
> No `LivroCreate` (POST) a mensagem de `lido` sai com o texto padrão do Pydantic. No `LivroUpdate` (PATCH, T07) a mensagem é customizada para `"lido deve ser true ou false"`.

### 3. LivroUpdate (todos os campos opcionais)

```bash
python -X utf8 -c "
from pydantic import ValidationError
from app.schemas import LivroUpdate

# body vazio é aceito no schema (T07 trata '{}' → 400 no router)
print('update vazio:', LivroUpdate().model_dump(exclude_unset=True))

# atualizando só um campo
print('só lido:', LivroUpdate(lido=True).model_dump(exclude_unset=True))

# string vazia em campo opcional vira erro diferente do Create
try:
    LivroUpdate(titulo='')
except ValidationError as e:
    print('titulo vazio:', e.errors()[0]['msg'].replace('Value error, ', ''))
"
```

Esperado: `titulo não pode ser vazio` (mensagem de PATCH, conforme T07).

### 4. Serialização ISO 8601 UTC no LivroResponse

```bash
python -X utf8 -c "
from datetime import datetime
from app.schemas import LivroResponse

# simula um registro do banco (created_at/updated_at são datetimes naive em UTC)
class Fake:
    id=1; titulo='X'; autor='Y'; editora='Z'; ano_publicacao=2000; lido=False
    created_at=datetime(2026,4,17,10,0,0)
    updated_at=datetime(2026,4,17,10,30,15)

dump = LivroResponse.model_validate(Fake()).model_dump(mode='json')
print('created_at:', dump['created_at'])
print('updated_at:', dump['updated_at'])
"
```

Esperado:

```
created_at: 2026-04-17T10:00:00Z
updated_at: 2026-04-17T10:30:15Z
```

Sem microssegundos, com sufixo `Z` — formato exato do design §2.

---

## T04 — `POST /api/livros` (cadastrar livro)

**O que a task entrega:** primeiro endpoint real. A pilha `Router → Service → Repository` está montada em [app/router.py](../app/router.py), [app/service.py](../app/service.py) e [app/repository.py](../app/repository.py). Validações do T03 agora entram em ação via Pydantic, e um handler de exceções em [app/main.py](../app/main.py) converte os 422 do Pydantic em `400` com mensagens descritivas em português.

A partir daqui, a forma mais prática de testar é pelo **Swagger UI** (`/docs`) — o endpoint aparece lá com botão "Try it out".

### 1. Via Swagger UI (navegador)

Com o uvicorn rodando, acesse http://127.0.0.1:8000/docs

- Clique em `POST /api/livros` → "Try it out"
- Edite o JSON de exemplo
- "Execute" → veja status, headers e corpo da resposta

### 2. Via curl — happy path (201)

```bash
curl -i -X POST http://127.0.0.1:8000/api/livros ^
  -H "Content-Type: application/json" ^
  -d "{\"titulo\":\"O Senhor dos Anéis\",\"autor\":\"J.R.R. Tolkien\",\"editora\":\"HarperCollins\",\"ano_publicacao\":1954}"
```

> No PowerShell use aspas simples no corpo, ou prefira `Invoke-RestMethod`. O `^` acima é continuação de linha do `cmd.exe` do Windows.

Esperado: `HTTP/1.1 201 Created` e um JSON com `id`, `created_at` e `updated_at` preenchidos pelo servidor, e `lido: false` (default RN02).

### 3. Erros esperados (400)

Campo ausente:
```bash
curl -i -X POST http://127.0.0.1:8000/api/livros -H "Content-Type: application/json" -d "{\"autor\":\"A\",\"editora\":\"E\",\"ano_publicacao\":2000}"
```
→ `400` + `{"detail":"titulo é obrigatório"}`

String vazia ou só espaços:
```bash
curl -i -X POST http://127.0.0.1:8000/api/livros -H "Content-Type: application/json" -d "{\"titulo\":\"   \",\"autor\":\"A\",\"editora\":\"E\",\"ano_publicacao\":2000}"
```
→ `400` + `{"detail":"titulo é obrigatório"}`

`ano_publicacao` fora do intervalo:
```bash
curl -i -X POST http://127.0.0.1:8000/api/livros -H "Content-Type: application/json" -d "{\"titulo\":\"T\",\"autor\":\"A\",\"editora\":\"E\",\"ano_publicacao\":2099}"
```
→ `400` + `{"detail":"ano_publicacao deve ser um número inteiro entre 1400 e 2026"}`

### 4. Duplicata (409)

Cadastre um livro qualquer, depois tente enviar de novo com título e autor equivalentes (a comparação é **case-insensitive** e ignora espaços das bordas):

```bash
curl -s -X POST http://127.0.0.1:8000/api/livros -H "Content-Type: application/json" -d "{\"titulo\":\"Dom Casmurro\",\"autor\":\"Machado de Assis\",\"editora\":\"E\",\"ano_publicacao\":1899}"

curl -i -X POST http://127.0.0.1:8000/api/livros -H "Content-Type: application/json" -d "{\"titulo\":\"DOM CASMURRO\",\"autor\":\"MACHADO DE ASSIS\",\"editora\":\"X\",\"ano_publicacao\":1900}"
```
→ `409` + `{"detail":"Já existe um livro com este título e autor"}`

### 5. Verificar persistência

Após os testes, confirme via SQLite que os livros ficaram gravados:
```bash
python -X utf8 -c "
import sqlite3
c = sqlite3.connect('biblioteca.db'); c.row_factory = sqlite3.Row
for r in c.execute('SELECT id, titulo, autor, lido FROM livros'):
    print(dict(r))
"
```

### 6. Limpeza

```bash
python -X utf8 -c "from app.models import SessionLocal, Livro; s=SessionLocal(); s.query(Livro).delete(); s.commit()"
```

---

## T05 — `GET /api/livros` (listar)

**O que a task entrega:** endpoint de listagem sem filtros. Retorna todos os livros cadastrados em ordem de `id` ascendente. Filtros por título/autor/editora/ano/lido só entram em T09.

### 1. Lista vazia (base recém-criada)

Com a tabela sem registros (use a limpeza de T04 se precisar):

```bash
curl -i http://127.0.0.1:8000/api/livros
```

Esperado: `200 OK` + corpo `[]`.

### 2. Lista com vários livros

Cadastre dois livros via `POST /api/livros`, depois:

```bash
curl -s http://127.0.0.1:8000/api/livros
```

Esperado: array com os dois livros, cada um contendo `id`, `titulo`, `autor`, `editora`, `ano_publicacao`, `lido`, `created_at` e `updated_at` (sempre com sufixo `Z`). Ordem por `id` ascendente.

### 3. Via Swagger UI

http://127.0.0.1:8000/docs → `GET /api/livros` → "Try it out" → "Execute". A resposta aparece com todos os livros do banco.

> A partir de T09 este endpoint aceita query params para busca e filtro (`?autor=tolkien&lido=true` etc.) — ver seção T09 abaixo.

---

## T06 — `GET /api/livros/{id}` (buscar por id)

**O que a task entrega:** endpoint que retorna um único livro pelo `id` (RF03). Responde `404` com mensagem em português quando o livro não existe.

### 1. Happy path (200)

Cadastre um livro via `POST /api/livros` e anote o `id` retornado. Depois:

```bash
curl -i http://127.0.0.1:8000/api/livros/1
```

Esperado: `200 OK` e JSON com o livro completo (`id`, `titulo`, `autor`, `editora`, `ano_publicacao`, `lido`, `created_at`, `updated_at`). As datas vêm com sufixo `Z`.

### 2. Livro inexistente (404)

```bash
curl -i http://127.0.0.1:8000/api/livros/9999
```

Esperado: `404 Not Found` + `{"detail":"Livro não encontrado"}`.

### 3. `id` não numérico (400)

```bash
curl -i http://127.0.0.1:8000/api/livros/abc
```

Esperado: `400` + `{"detail":"livro_id deve ser um número inteiro"}`. O handler de validação em [app/main.py](../app/main.py) traduz erros de parse de inteiro do Pydantic para português.

### 4. Via Swagger UI

http://127.0.0.1:8000/docs → `GET /api/livros/{livro_id}` → "Try it out" → digite um `id` → "Execute".

---

## T07 — `PATCH /api/livros/{id}` (editar)

**O que a task entrega:** endpoint de edição parcial (RF04 + RF05). Aceita qualquer subconjunto dos campos de um livro — inclusive apenas `lido` para marcar como lido. O `updated_at` é atualizado automaticamente. Respeita a regra RN01 ignorando o próprio `id` na checagem de duplicata.

### Ordem de validação

As validações seguem esta precedência (definida em CLAUDE.md — a primeira que falhar é a que aparece na resposta):

1. Body vazio (`{}`) → `"Informe ao menos um campo para atualizar"`
2. `lido` não booleano → `"lido deve ser true ou false"`
3. `ano_publicacao` fora do intervalo → `"ano_publicacao deve ser um número inteiro entre 1400 e {ano_atual}"`
4. `titulo`/`autor`/`editora` vazio ou só espaços → `"<campo> não pode ser vazio"`

### Setup

Cadastre dois livros via `POST /api/livros` e anote os `id`s retornados. Os exemplos abaixo assumem `id=1` (O Hobbit) e `id=2` (Dom Casmurro).

### 1. Happy path — editar qualquer campo (200)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"editora\":\"Allen & Unwin\",\"ano_publicacao\":1938}"
```

Esperado: `200 OK` + livro atualizado. O `updated_at` muda; o `created_at` permanece igual.

### 2. Marcar como lido (RF04)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"lido\":true}"
```

Esperado: `200 OK` + `"lido": true`. Marcar como lido é só um caso particular da edição (decisão D06 — único endpoint cobre RF04 e RF05).

### 3. Livro inexistente (404)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/9999 -H "Content-Type: application/json" -d "{\"lido\":true}"
```

Esperado: `404` + `{"detail":"Livro não encontrado"}`.

### 4. Body vazio (400)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{}"
```

Esperado: `400` + `{"detail":"Informe ao menos um campo para atualizar"}`.

### 5. `lido` não booleano (400)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"lido\":\"sim\"}"
```

Esperado: `400` + `{"detail":"lido deve ser true ou false"}`.

### 6. `ano_publicacao` fora do intervalo (400)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"ano_publicacao\":2099}"
```

Esperado: `400` + `{"detail":"ano_publicacao deve ser um número inteiro entre 1400 e 2026"}`.

### 7. Campo string vazio ou só espaços (400)

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"titulo\":\"   \"}"
```

Esperado: `400` + `{"detail":"titulo não pode ser vazio"}`.

### 8. Duplicata em outro livro (409)

Tente atualizar `id=2` (Dom Casmurro) para o mesmo título+autor do `id=1`:

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/2 -H "Content-Type: application/json" -d "{\"titulo\":\"O Hobbit\",\"autor\":\"Tolkien\"}"
```

Esperado: `409` + `{"detail":"Já existe um livro com este título e autor"}`. A comparação é case-insensitive e ignora espaços.

### 9. Reenviar o mesmo título+autor do próprio livro NÃO gera 409

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 -H "Content-Type: application/json" -d "{\"titulo\":\"O Hobbit\",\"autor\":\"Tolkien\",\"editora\":\"Outra\"}"
```

Esperado: `200 OK`. A checagem de duplicata ignora o próprio `id`.

### 10. Via Swagger UI

http://127.0.0.1:8000/docs → `PATCH /api/livros/{livro_id}` → "Try it out" → informe `livro_id` e um JSON parcial no corpo.

---

## T08 — `DELETE /api/livros/{id}` (remover)

**O que a task entrega:** endpoint de remoção (RF06). Retorna `204 No Content` em sucesso (sem corpo) e `404` se o livro não existir.

### 1. Happy path (204)

Cadastre um livro via `POST /api/livros` e anote o `id`. Depois:

```bash
curl -i -X DELETE http://127.0.0.1:8000/api/livros/1
```

Esperado: `HTTP/1.1 204 No Content` — **sem corpo de resposta**. `204` indica sucesso e que o cliente não precisa atualizar a view (é o recomendado para `DELETE` pela RFC 7231).

### 2. Confirmar que o livro sumiu

```bash
curl -i http://127.0.0.1:8000/api/livros/1
```

Esperado: `404` + `{"detail":"Livro não encontrado"}`.

```bash
curl -s http://127.0.0.1:8000/api/livros
```

O livro removido não aparece mais na listagem.

### 3. Remover livro inexistente (404)

```bash
curl -i -X DELETE http://127.0.0.1:8000/api/livros/9999
```

Esperado: `404` + `{"detail":"Livro não encontrado"}`.

### 4. Via Swagger UI

http://127.0.0.1:8000/docs → `DELETE /api/livros/{livro_id}` → "Try it out" → informe o `id` → "Execute". A resposta aparece com `Response body` vazio e `Code: 204`.

---

## T09 — Filtros no `GET /api/livros`

**O que a task entrega:** query params para busca e filtro no endpoint de listagem (RF07). Strings são busca parcial case-insensitive; número e booleano são filtro exato. Todos os filtros combinam com `AND`.

| Param | Tipo | Comportamento |
|---|---|---|
| `titulo` | string | Busca parcial, case-insensitive (`ilike %valor%`) |
| `autor` | string | Busca parcial, case-insensitive |
| `editora` | string | Busca parcial, case-insensitive |
| `ano_publicacao` | inteiro | Filtro exato |
| `lido` | `true`/`false` | Filtro exato; aceita `true`/`false` (case-insensitive) **apenas em query param** |

### Setup

Cadastre alguns livros via `POST /api/livros` para ter o que filtrar. Os exemplos abaixo assumem quatro títulos misturando autores, editoras e anos.

### 1. Busca parcial case-insensitive (strings)

```bash
curl -s "http://127.0.0.1:8000/api/livros?titulo=hobbit"
curl -s "http://127.0.0.1:8000/api/livros?autor=MACHADO"
curl -s "http://127.0.0.1:8000/api/livros?editora=collins"
```

Cada chamada retorna só os livros cujo campo **contém** o valor informado, ignorando maiúsculas/minúsculas.

### 2. Filtro exato por ano e por lido

```bash
curl -s "http://127.0.0.1:8000/api/livros?ano_publicacao=1937"
curl -s "http://127.0.0.1:8000/api/livros?lido=true"
curl -s "http://127.0.0.1:8000/api/livros?lido=FALSE"
```

`lido` aceita qualquer combinação de maiúsculas/minúsculas (`true`, `True`, `TRUE`, `false`, `False`, `FALSE`).

### 3. Combinação de filtros

```bash
curl -s "http://127.0.0.1:8000/api/livros?autor=tolkien&lido=false"
```

Retorna os livros do autor Tolkien que **ainda não foram lidos**. Os filtros se acumulam com `AND`.

### 4. Lista vazia (200)

```bash
curl -i "http://127.0.0.1:8000/api/livros?autor=autor-inexistente"
```

Esperado: `200 OK` + corpo `[]`. Sem resultado **não é** 404 — a listagem filtrada existe, apenas está vazia.

### 5. `lido` inválido (400)

```bash
curl -i "http://127.0.0.1:8000/api/livros?lido=sim"
curl -i "http://127.0.0.1:8000/api/livros?lido=1"
```

Esperado em ambos: `400` + `{"detail":"lido deve ser true ou false"}`. Apenas os literais `true` e `false` (case-insensitive) são aceitos — outros valores do Pydantic como `1`, `0`, `yes`, `no` são rejeitados propositalmente.

### 6. `ano_publicacao` não numérico (400)

```bash
curl -i "http://127.0.0.1:8000/api/livros?ano_publicacao=abc"
```

Esperado: `400` + `{"detail":"ano_publicacao deve ser um número inteiro"}`.

### 7. Importante: a coerção de `lido` só vale em query param

No corpo de `POST`/`PATCH`, `lido` precisa ser booleano JSON estrito:

```bash
# isto funciona — query param
curl -s "http://127.0.0.1:8000/api/livros?lido=true"

# isto falha — body com string em vez de booleano
curl -i -X PATCH http://127.0.0.1:8000/api/livros/1 \
  -H "Content-Type: application/json" \
  -d "{\"lido\":\"true\"}"
# → 400 "lido deve ser true ou false" (T07)
```

### 8. Via Swagger UI

http://127.0.0.1:8000/docs → `GET /api/livros` → "Try it out". O Swagger mostra campos para cada query param; preencha só os que quiser usar.

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

- T10 — testes automatizados (`pytest`)
- T11 — servir frontend estático
- T12 — frontend HTML/JS
- T13 — README completo
