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

**Exemplo de resposta `201`** (livro recém-criado nunca está emprestado, conforme RN07):
```json
{
  "id": 1,
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954,
  "lido": false,
  "emprestado": false,
  "emprestado_para": null,
  "data_emprestimo": null,
  "created_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-16T10:00:00Z"
}
```

> Os campos `emprestado`, `emprestado_para` e `data_emprestimo` são **derivados** do empréstimo ativo do livro (RN07). Quando `emprestado=false`, os dois últimos são `null`.

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
| `emprestado` | boolean | Filtro exato: `true` (livros com empréstimo ativo) ou `false` (sem empréstimo ativo). Atua sobre o estado derivado (RN07). |
| `emprestado_para` | string | Busca parcial, case-insensitive sobre `emprestado_para` do **empréstimo ativo**. Livros sem empréstimo ativo são excluídos. |
| `emprestado_desde` | data ISO 8601 | Filtro `>=` sobre `data_emprestimo` do **empréstimo ativo**. Livros sem empréstimo ativo são excluídos. |
| `emprestado_ate` | data ISO 8601 | Filtro `<=` sobre `data_emprestimo` do **empréstimo ativo**. Livros sem empréstimo ativo são excluídos. |

> Como query params são sempre strings em HTTP, os valores `?lido=true`/`?lido=false` e `?emprestado=true`/`?emprestado=false` (case-insensitive) são aceitos e coagidos a booleano. Essa coerção só vale para query params — no body de `POST`/`PATCH`, `lido` deve ser booleano JSON estrito (ver nota em `PATCH /api/livros/{id}`).

**Exemplos:**
```
GET /api/livros
GET /api/livros?lido=false
GET /api/livros?autor=tolkien&lido=true
GET /api/livros?emprestado=true
GET /api/livros?emprestado_para=maria
GET /api/livros?emprestado_desde=2026-01-01T00:00:00Z&emprestado_ate=2026-04-30T23:59:59Z
```

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Lista retornada (pode ser vazia) |

**Exemplo de resposta `200`** (array puro de livros, vazio quando não há resultados; campos de empréstimo derivados — RN07):
```json
[
  {
    "id": 1,
    "titulo": "O Senhor dos Anéis",
    "autor": "J.R.R. Tolkien",
    "editora": "HarperCollins",
    "ano_publicacao": 1954,
    "lido": false,
    "emprestado": true,
    "emprestado_para": "Maria",
    "data_emprestimo": "2026-04-20T10:00:00Z",
    "created_at": "2026-04-16T10:00:00Z",
    "updated_at": "2026-04-20T10:00:00Z"
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

**Exemplo de resposta `200`** (campos de empréstimo derivados — RN07):
```json
{
  "id": 1,
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954,
  "lido": false,
  "emprestado": false,
  "emprestado_para": null,
  "data_emprestimo": null,
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

**Exemplo de resposta `200`** (livro completo com `updated_at` novo; campos de empréstimo derivados — RN07):
```json
{
  "id": 1,
  "titulo": "O Hobbit",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1937,
  "lido": true,
  "emprestado": false,
  "emprestado_para": null,
  "data_emprestimo": null,
  "created_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-17T09:30:00Z"
}
```

> Este endpoint **não** aceita os campos `emprestado`, `emprestado_para` ou `data_emprestimo` no body — empréstimos são geridos via `POST`/`DELETE /api/livros/{id}/emprestimos` (D10).

---

## DELETE /api/livros/{id}
Remove um livro pelo ID.

**Respostas:**

| Status | Descrição |
|---|---|
| `204 No Content` | Livro removido com sucesso |
| `404 Not Found` | Livro não encontrado |

> A remoção apaga em cascata todos os empréstimos (ativos e históricos) relacionados ao livro (RN11/D12).

---

## POST /api/livros/{id}/emprestimos
Registra um novo empréstimo para o livro (RF09/US08).

**Request body:**
```json
{
  "emprestado_para": "Maria",
  "data_emprestimo": "2026-04-20T10:00:00Z"
}
```

> `emprestado_para` é obrigatório, não pode ser string vazia ou conter apenas espaços (RN05).
> `data_emprestimo` é obrigatório e deve respeitar RN09: `<= now(UTC)` e `>= created_at` do livro.

**Respostas:**

| Status | Descrição |
|---|---|
| `201 Created` | Empréstimo criado com sucesso |
| `400 Bad Request` | `emprestado_para` ausente/vazio (`"emprestado_para é obrigatório"`); `data_emprestimo` ausente, futura (`"data_emprestimo não pode ser futura"`) ou anterior à criação do livro (`"data_emprestimo não pode ser anterior à criação do livro"`) |
| `404 Not Found` | Livro não encontrado (`"Livro não encontrado"`) |
| `409 Conflict` | Livro já possui empréstimo ativo (`"Livro já está emprestado"`) — RN08 |

**Exemplo de resposta `201`:**
```json
{
  "id": 7,
  "livro_id": 1,
  "emprestado_para": "Maria",
  "data_emprestimo": "2026-04-20T10:00:00Z",
  "data_devolucao": null,
  "created_at": "2026-04-26T15:00:00Z",
  "updated_at": "2026-04-26T15:00:00Z"
}
```

---

## DELETE /api/livros/{id}/emprestimos
Encerra o empréstimo ativo do livro registrando a data de devolução (RF10/US09).

**Request body:**
```json
{
  "data_devolucao": "2026-04-26T15:00:00Z"
}
```

> `data_devolucao` é obrigatório e deve respeitar RN09: `>= data_emprestimo` do empréstimo ativo e `<= now(UTC)`.

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Empréstimo encerrado com sucesso (retorna o registro com `data_devolucao` preenchida) |
| `400 Bad Request` | `data_devolucao` ausente, futura (`"data_devolucao não pode ser futura"`), anterior à `data_emprestimo` (`"data_devolucao não pode ser anterior à data_emprestimo"`); ou livro sem empréstimo ativo (`"Livro não está emprestado"`) — RN10 |
| `404 Not Found` | Livro não encontrado (`"Livro não encontrado"`) |

**Exemplo de resposta `200`:**
```json
{
  "id": 7,
  "livro_id": 1,
  "emprestado_para": "Maria",
  "data_emprestimo": "2026-04-20T10:00:00Z",
  "data_devolucao": "2026-04-26T15:00:00Z",
  "created_at": "2026-04-26T15:00:00Z",
  "updated_at": "2026-04-26T15:00:00Z"
}
```

> Este endpoint usa `DELETE` no sentido de "encerrar o empréstimo ativo", não de apagar registros históricos. O registro continua persistido (com `data_devolucao` preenchida) para o histórico (RF11/D08).

---

## GET /api/livros/{id}/emprestimos
Retorna o histórico completo de empréstimos do livro, ordenado por `data_emprestimo` desc (RF11/US10).

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Lista de empréstimos retornada (pode ser vazia se o livro nunca foi emprestado) |
| `404 Not Found` | Livro não encontrado (`"Livro não encontrado"`) |

**Exemplo de resposta `200`:**
```json
[
  {
    "id": 7,
    "livro_id": 1,
    "emprestado_para": "Maria",
    "data_emprestimo": "2026-04-20T10:00:00Z",
    "data_devolucao": null,
    "created_at": "2026-04-26T15:00:00Z",
    "updated_at": "2026-04-26T15:00:00Z"
  },
  {
    "id": 3,
    "livro_id": 1,
    "emprestado_para": "João",
    "data_emprestimo": "2025-12-01T09:00:00Z",
    "data_devolucao": "2026-01-15T18:00:00Z",
    "created_at": "2025-12-01T09:00:00Z",
    "updated_at": "2026-01-15T18:00:00Z"
  }
]
```

---

## Frontend estático (não é endpoint REST)

Conforme decisão [D07 do design](04-design.md), a raiz `/` é servida pelo FastAPI via `StaticFiles(directory="app/static", html=True)`:

- `GET /` → serve `app/static/index.html` automaticamente (comportamento padrão do `html=True`).
- `GET /style.css`, `GET /script.js`, etc. → arquivos estáticos da pasta `app/static/`.

Essas rotas não aparecem na documentação OpenAPI e não têm contrato de API (são apenas entrega de arquivos). Alterações aqui não impactam clientes da API.
