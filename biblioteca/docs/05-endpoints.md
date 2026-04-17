# Biblioteca Pessoal — Endpoints

Base URL: `/livros`

---

## POST /livros
Cadastra um novo livro.

**Request body:**
```json
{
  "titulo": "O Senhor dos Anéis",
  "autor": "J.R.R. Tolkien",
  "editora": "HarperCollins",
  "ano_publicacao": 1954
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
  "created_at": "2026-04-16T10:00:00",
  "updated_at": "2026-04-16T10:00:00"
}
```

---

## GET /livros
Lista todos os livros. Aceita filtros via query params.

**Query params (todos opcionais):**

| Param | Tipo | Descrição |
|---|---|---|
| `titulo` | string | Busca parcial, case-insensitive |
| `autor` | string | Busca parcial, case-insensitive |
| `editora` | string | Busca parcial, case-insensitive |
| `ano_publicacao` | inteiro | Filtro exato |
| `lido` | boolean | Filtro exato: `true` ou `false` |

**Exemplos:**
```
GET /livros
GET /livros?lido=false
GET /livros?autor=tolkien&lido=true
```

**Respostas:**

| Status | Descrição |
|---|---|
| `200 OK` | Lista retornada (pode ser vazia) |

---

## GET /livros/{id}
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
  "created_at": "2026-04-16T10:00:00",
  "updated_at": "2026-04-16T10:00:00"
}
```

---

## PATCH /livros/{id}
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
| `400 Bad Request` | Campo inválido, vazio, `ano_publicacao` fora do intervalo válido, ou `lido` não booleano |
| `404 Not Found` | Livro não encontrado |
| `409 Conflict` | Atualização geraria duplicata com outro livro |

---

## DELETE /livros/{id}
Remove um livro pelo ID.

**Respostas:**

| Status | Descrição |
|---|---|
| `204 No Content` | Livro removido com sucesso |
| `404 Not Found` | Livro não encontrado |
