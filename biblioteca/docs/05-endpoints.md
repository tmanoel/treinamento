# Biblioteca Pessoal — Endpoints

Base URL da API: `/api` — todos os endpoints REST estão sob esse prefixo (ex.: `/api/livros`, `/api/health`). A raiz `/` é reservada ao frontend estático (ver §Frontend estático ao final).

Padrão de datas em request/response: strings ISO 8601 em UTC (ex.: `"2026-04-17T10:00:00Z"`), conforme [04-design.md §2](04-design.md).

---

## GET /api/health
Verifica se a aplicação está no ar (RNF06).

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Aplicação operacional |

**Exemplo de resposta `200`:**
```json
{"status": "ok"}
```

---

## POST /api/livros
Cadastra um novo livro.

**Request body** (`lido` é opcional, padrão `false`):
```json
{
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954,
  "lido": false
}
```

**Respostas:**

| Status | Descrição |
|---|---|
| `201 Created` | Livro cadastrado com sucesso |
| `400 Bad Request` | Campo obrigatório ausente, vazio ou `ano_publicacao` inválido |
| `409 Conflict` | Já existe um livro com o mesmo título e autor |

**Exemplo de resposta `201`:**
```json
{
  "id": 1,
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954,
  "lido": false,
  "created_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-16T10:00:00Z"
}
```

---

## GET /api/livros
Lista todos os livros. Aceita filtros via query params.

**Query params (todos opcionais):**

| Param | Tipo | Descrição |
|---|---|---|
| `titulo` | string | Busca parcial, case-insensitive |
| `autor` | string | Busca parcial, case-insensitive |
| `editora` | string | Busca parcial, case-insensitive |
| `ano_publicacao` | inteiro | Filtro exato |
| `lido` | boolean | Filtro exato: `true` ou `false` |

> Como query params são sempre strings em HTTP, os valores `?lido=true` e `?lido=false` (case-insensitive) são aceitos e coagidos a booleano. Essa coerção só vale para query params — no body de `POST`/`PATCH`, `lido` deve ser booleano JSON estrito (ver nota em `PATCH /api/livros/{id}`).

**Exemplos:**
```
GET /api/livros
GET /api/livros?lido=false
GET /api/livros?autor=tolkien&lido=true
```

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Lista retornada (pode ser vazia) |

**Exemplo de resposta `200`** (array puro de livros, vazio quando não há resultados):
```json
[
  {
    "id": 1,
    "titulo": "O Senhor dos Anéis",
    "autor": "J.R.R. Tolkien",
    "editora": "HarperCollins",
    "ano_publicacao": 1954,
    "lido": false,
    "created_at": "2026-04-16T10:00:00Z",
    "updated_at": "2026-04-16T10:00:00Z"
  }
]
```

---

## GET /api/livros/{id}
Retorna os dados de um livro específico pelo ID.

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Dados do livro retornados |
| `404 Not Found` | Livro não encontrado |

**Exemplo de resposta `200`:**
```json
{
  "id": 1,
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954,
  "lido": false,
  "created_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-16T10:00:00Z"
}
```

---

## PATCH /api/livros/{id}
Atualiza os dados de um livro existente. Cobre tanto a edição genérica (RF05/US04) quanto a ação de marcar como lido/não lido (RF04/US03).

**Request body** (todos os campos opcionais, ao menos um obrigatório):
```json
{
  "titulo": "O Hobbit",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1937,
  "lido": true
}
```

> `lido` deve ser um booleano (`true` ou `false`). Strings como `"true"` são inválidas.

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Livro atualizado com sucesso |
| `400 Bad Request` | Nenhum campo enviado no body, campo inválido, vazio, `ano_publicacao` fora do intervalo válido, ou `lido` não booleano |
| `404 Not Found` | Livro não encontrado |
| `409 Conflict` | Atualização geraria duplicata com outro livro (mensagem: `"Já existe um livro com este título e autor"`). Reenviar os mesmos `titulo`/`autor` do próprio livro não gera 409 (ver RN01). |

**Exemplo de resposta `200`** (livro completo com `updated_at` novo):
```json
{
  "id": 1,
  "titulo": "O Hobbit",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1937,
  "lido": true,
  "created_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-17T09:30:00Z"
}
```

---

## DELETE /api/livros/{id}
Remove um livro pelo ID.

**Respostas:**

| Status | Descrição |
|---|---|
| `204 No Content` | Livro removido com sucesso |
| `404 Not Found` | Livro não encontrado |

---

## Frontend estático (não é endpoint REST)

Conforme decisão [D07 do design](04-design.md), a raiz `/` é servida pelo FastAPI via `StaticFiles(directory="app/static", html=True)`:

- `GET /` → serve `app/static/index.html` automaticamente (comportamento padrão do `html=True`).
- `GET /style.css`, `GET /script.js`, etc. → arquivos estáticos da pasta `app/static/`.

Essas rotas não aparecem na documentação OpenAPI e não têm contrato de API (são apenas entrega de arquivos). Alterações aqui não impactam clientes da API.
