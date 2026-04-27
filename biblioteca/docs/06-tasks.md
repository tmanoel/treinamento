# Biblioteca Pessoal — Tasks

Decomposição incremental do plano em tarefas atômicas. Cada task referencia os requisitos/user stories que atende e tem critério de conclusão verificável.

## Legenda

- **Ref:** requisitos, user stories e regras de negócio cobertos
- **Depende de:** tasks que precisam estar concluídas antes
- **Pronto quando:** critério objetivo de conclusão

---

## Fase 1 — Fundação

### T01 — Setup inicial do projeto
Criar a estrutura de pastas proposta no design, instalar FastAPI e configurar o entrypoint.

- **Ref:** design §4
- **Depende de:** —
- **Pronto quando:**
  - Estrutura `app/`, `tests/`, `requirements.txt`, `README.md` existe
  - `uvicorn app.main:app` sobe a aplicação sem erros
  - Endpoint `GET /api/health` (health check, RNF06) retorna `200` com `{"status": "ok"}`
  - API roteada sob prefixo `/api` (D07)

---

### T02 — Camada de persistência (SQLite + SQLAlchemy)
Configurar o SQLAlchemy, criar a sessão do banco e o modelo `Livro` com todos os campos definidos no design.

- **Ref:** design §2, RNF03, RN06
- **Depende de:** T01
- **Pronto quando:**
  - Arquivo `biblioteca.db` é criado automaticamente ao subir a aplicação
  - Tabela `livros` tem todos os campos: `id`, `titulo`, `autor`, `editora`, `ano_publicacao`, `lido`, `created_at`, `updated_at`
  - `created_at` é preenchido automaticamente na criação
  - `updated_at` é preenchido na criação e atualizado automaticamente a cada modificação do registro
  - Ambos serializam como strings ISO 8601 em UTC (ex.: `"2026-04-17T10:00:00Z"`)

---

### T03 — Schemas de validação (Pydantic)
Criar os schemas de request/response em `schemas.py` e as validações baseadas nas regras de negócio.

- **Ref:** RN04, RN05, RNF02, RNF04
- **Depende de:** T01
- **Pronto quando:**
  - Schema `LivroCreate`, `LivroUpdate`, `LivroResponse` definidos
  - Validação `ano_publicacao` entre 1400 e ano atual (RN04)
  - Mensagem do erro de `ano_publicacao` é construída dinamicamente interpolando `datetime.now(tz=UTC).year` (ex.: `f"ano_publicacao deve ser um número inteiro entre 1400 e {datetime.now(tz=UTC).year}"`)
  - Validação de strings não vazias nem só espaços (RN05) aplicando `.strip()` antes de checar vazio; mensagem: `"<campo> é obrigatório"` (ex.: `"titulo é obrigatório"`)
  - Erros retornam mensagens descritivas em português (RNF04)

---

## Fase 2 — Endpoints

### T04 — POST /livros (cadastrar livro)
Implementar o endpoint de cadastro com verificação de duplicata.

- **Ref:** RF01, RF02, RN01, RN02, US01
- **Depende de:** T02, T03
- **Pronto quando:**
  - `POST /api/livros` retorna `201` em sucesso
  - Retorna `400` se campo obrigatório ausente/vazio ou `ano_publicacao` inválido
  - Retorna `409` se já existir livro com mesmo `titulo`+`autor` (case-insensitive)
  - Livro criado tem `lido: false` por padrão

---

### T05 — GET /livros (listar)
Implementar listagem sem filtros.

- **Ref:** RF03, US02
- **Depende de:** T02, T03
- **Pronto quando:**
  - `GET /api/livros` retorna `200` com array de livros
  - Retorna array vazio quando não há livros cadastrados

---

### T06 — GET /livros/{id} (consultar por ID)
Implementar consulta de um livro específico.

- **Ref:** RF08, US07
- **Depende de:** T02, T03
- **Pronto quando:**
  - `GET /api/livros/{id}` retorna `200` com os dados do livro
  - Retorna `404` com mensagem descritiva quando livro não existe

---

### T07 — PATCH /api/livros/{id} (editar e marcar lido/não lido)
Implementar edição parcial do livro. Esta task cobre tanto a edição genérica quanto a ação específica de marcar como lido/não lido.

- **Ref:** RF04, RF05, RN01, RN03, US03, US04
- **Depende de:** T02, T03
- **Pronto quando:**
  - Permite atualizar qualquer campo (`titulo`, `autor`, `editora`, `ano_publicacao`, `lido`)
  - Retorna `200` com os dados atualizados
  - Ordem de validação do `400`: (1) body vazio → `"Informe ao menos um campo para atualizar"`; (2) `lido` não booleano → `"lido deve ser true ou false"`; (3) `ano_publicacao` fora do intervalo → mensagem dinâmica (ver T03); (4) campo obrigatório enviado como string vazia ou apenas espaços → `"<campo> não pode ser vazio"` (ex.: `"autor não pode ser vazio"`)
  - Retorna `404` se livro não existe (`"Livro não encontrado"`)
  - Retorna `409` se a edição gerar duplicata com **outro** livro (ignora o próprio `id` na verificação — ver RN01). Mensagem: `"Já existe um livro com este título e autor"`
  - `updated_at` é atualizado automaticamente

---

### T08 — DELETE /api/livros/{id} (remover)
Implementar remoção de livro.

- **Ref:** RF06 (remoção), US05
- **Depende de:** T02
- **Pronto quando:**
  - `DELETE /api/livros/{id}` retorna `204 No Content` em sucesso
  - Retorna `404` se livro não existe

---

### T09 — GET /livros com filtros (buscar)
Adicionar suporte a query params de busca e filtro no endpoint de listagem.

- **Ref:** RF07, US06
- **Depende de:** T05
- **Pronto quando:**
  - Query params `titulo`, `autor`, `editora` fazem busca parcial case-insensitive
  - Query params `ano_publicacao` e `lido` fazem filtro exato
  - Filtros podem ser combinados
  - Retorna `200` com lista filtrada (pode ser vazia)

---

## Fase 3 — Qualidade

### T10 — Testes automatizados
Escrever testes cobrindo os critérios de aceitação de todas as user stories e do health check.

- **Ref:** todas as US (US01–US07), RNF06
- **Depende de:** T04, T05, T06, T07, T08, T09
- **Pronto quando:**
  - Todos os critérios de aceitação das user stories têm ao menos um teste
  - `GET /api/health` tem teste cobrindo o `200` com `{"status": "ok"}` (RNF06)
  - `pytest` roda todos os testes com sucesso
  - Testes usam banco em memória (não afeta `biblioteca.db`)

---

### T11 — Servir arquivos estáticos do frontend
Configurar o FastAPI para servir a pasta `app/static/` na raiz, conforme D07.

- **Ref:** design §4 (Frontend), D07
- **Depende de:** T01
- **Pronto quando:**
  - Montagem feita via `app.mount("/", StaticFiles(directory="app/static", html=True), name="frontend")` — o flag `html=True` faz `GET /` servir `index.html` automaticamente, sem rota dedicada
  - Montagem acontece **depois** do roteador de API (`/api/...`) para não sobrepor os endpoints REST
  - Estrutura `app/static/` com `index.html`, `style.css`, `script.js` existe (podem estar vazios)

---

### T12 — Frontend funcional (HTML + JS)
Implementar a interface simples para testar a API pelo navegador.

- **Ref:** design §4 (Frontend)
- **Depende de:** T04, T05, T07, T08, T09, T11
- **Pronto quando:**
  - Formulário de cadastro envia `POST /api/livros` e exibe mensagem de sucesso/erro
  - Lista exibe todos os livros com botões de editar, remover e marcar como lido
  - Filtros por título, autor, editora, `lido` e `ano_publicacao` consomem `GET /api/livros` com os query params correspondentes e atualizam a lista (ex.: `GET /api/livros?autor=tolkien&lido=true`)
  - Mensagens de erro da API são exibidas em português para o usuário

---

### T13 — README e instruções de execução
Documentar como clonar, instalar, rodar e testar o projeto.

- **Ref:** —
- **Depende de:** T10, T12
- **Pronto quando:**
  - README explica dependências, como instalar e como rodar
  - Inclui exemplos de chamadas para cada endpoint (curl ou similar)
  - Menciona como rodar os testes
  - Explica como acessar o frontend no navegador

---

## Fase 4 — Empréstimos

### T14 — Modelo `Emprestimo` + migração
Criar a tabela `emprestimos` com FK para `livros`, índice e cascade delete.

- **Ref:** design §2 (Entidade `Emprestimo`), RN07–RN11, D08, D12
- **Depende de:** T02
- **Pronto quando:**
  - SQLAlchemy model `Emprestimo` definido com campos: `id`, `livro_id` (FK → `livros.id`, `ON DELETE CASCADE`), `emprestado_para`, `data_emprestimo`, `data_devolucao` (nullable), `created_at`, `updated_at`
  - Índice em `livro_id` para acelerar lookups de empréstimo ativo
  - Tabela criada automaticamente ao subir a aplicação (junto com `livros`)
  - `created_at`/`updated_at` seguem o mesmo padrão de `Livro` (preenchimento e atualização automáticos, ISO 8601 UTC)
  - PRAGMA `foreign_keys = ON` configurado no SQLAlchemy engine para que SQLite respeite o `ON DELETE CASCADE`

---

### T15 — Schemas Pydantic de empréstimo
Criar schemas `EmprestimoCreate`, `EmprestimoClose`, `EmprestimoResponse` em `schemas.py`.

- **Ref:** RN05, RN09, RNF02, RNF04
- **Depende de:** T01
- **Pronto quando:**
  - `EmprestimoCreate`: `emprestado_para` str não vazia (`.strip()`, mensagem `"emprestado_para é obrigatório"`); `data_emprestimo` datetime; validação de futuro (`"data_emprestimo não pode ser futura"`) — a validação contra `created_at` do livro fica no Service (T16) por exigir o livro
  - `EmprestimoClose`: `data_devolucao` datetime; validação de futuro (`"data_devolucao não pode ser futura"`) — comparação contra `data_emprestimo` fica no Service (T17)
  - `EmprestimoResponse`: todos os campos do model (`id`, `livro_id`, `emprestado_para`, `data_emprestimo`, `data_devolucao`, `created_at`, `updated_at`); datas em ISO 8601 UTC (`"YYYY-MM-DDTHH:MM:SSZ"`)

---

### T16 — Endpoint `POST /api/livros/{id}/emprestimos`
Implementar criação de empréstimo, com checagem de empréstimo ativo (RN08) e validação de data contra `created_at` do livro (RN09).

- **Ref:** RF09, RN05, RN08, RN09, US08
- **Depende de:** T14, T15
- **Pronto quando:**
  - Retorna `201` com o `EmprestimoResponse`
  - Retorna `400` se `emprestado_para` ausente/vazio, `data_emprestimo` ausente, futura, ou anterior a `livros.created_at` (mensagem `"data_emprestimo não pode ser anterior à criação do livro"`)
  - Retorna `404` se livro não existe (`"Livro não encontrado"`)
  - Retorna `409` se já existe `Emprestimo` ativo para o livro (`"Livro já está emprestado"`)

---

### T17 — Endpoint `DELETE /api/livros/{id}/emprestimos`
Implementar fechamento do empréstimo ativo.

- **Ref:** RF10, RN09, RN10, US09
- **Depende de:** T14, T15
- **Pronto quando:**
  - Retorna `200` com o `EmprestimoResponse` atualizado (com `data_devolucao` preenchida)
  - Retorna `400` se `data_devolucao` ausente, futura, anterior à `data_emprestimo` do empréstimo ativo, ou se livro não tem empréstimo ativo (`"Livro não está emprestado"`)
  - Retorna `404` se livro não existe (`"Livro não encontrado"`)
  - `updated_at` do empréstimo é atualizado

---

### T18 — Endpoint `GET /api/livros/{id}/emprestimos`
Implementar listagem do histórico de empréstimos do livro.

- **Ref:** RF11, US10
- **Depende de:** T14, T15
- **Pronto quando:**
  - Retorna `200` com array de `EmprestimoResponse` ordenado por `data_emprestimo` desc (mais recente primeiro)
  - Retorna lista vazia (`[]`) quando o livro existe mas nunca foi emprestado
  - Retorna `404` se livro não existe (`"Livro não encontrado"`)

---

### T19 — Filtros novos em `GET /api/livros` + ajuste do `LivroResponse`
Adicionar query params `emprestado`, `emprestado_para`, `emprestado_desde`, `emprestado_ate` em `GET /api/livros`. Ajustar `LivroResponse` para incluir os campos derivados (`emprestado`, `emprestado_para`, `data_emprestimo`).

- **Ref:** RF07 (atualizado), RF12, RN07, US06 (atualizada), D09
- **Depende de:** T14, T09
- **Pronto quando:**
  - `LivroResponse` inclui `emprestado` (bool, derivado), `emprestado_para` (str|null, do empréstimo ativo) e `data_emprestimo` (datetime|null, do empréstimo ativo) em **todos** os endpoints que retornam livro (`POST`, `GET`, `GET /{id}`, `PATCH`)
  - `?emprestado=true|false` filtra livros pela existência (ou não) de empréstimo ativo
  - `?emprestado_para=<termo>` faz busca parcial case-insensitive sobre o `emprestado_para` do empréstimo ativo (livros sem ativo são excluídos do resultado)
  - `?emprestado_desde=<data>` e `?emprestado_ate=<data>` filtram pela `data_emprestimo` do empréstimo ativo (livros sem ativo são excluídos)
  - Filtros podem ser combinados entre si e com os existentes
  - Implementação no Repository via `LEFT JOIN` ou subquery em `emprestimos` filtrando `data_devolucao IS NULL`

---

### T20 — Frontend: UI de empréstimo
Adicionar interface para emprestar/devolver livros, visualizar histórico e filtrar por empréstimo.

- **Ref:** RF09, RF10, RF11, RF12, US08, US09, US10
- **Depende de:** T16, T17, T18, T19
- **Pronto quando:**
  - Tabela principal mostra coluna(s) com status do empréstimo (`emprestado`, `emprestado_para`, `data_emprestimo`)
  - Botão "Emprestar" (ou similar) em livros não emprestados abre formulário/modal pedindo `emprestado_para` e `data_emprestimo`; submete `POST /api/livros/{id}/emprestimos`
  - Botão "Devolver" em livros emprestados abre formulário/modal pedindo `data_devolucao`; submete `DELETE /api/livros/{id}/emprestimos`
  - Botão/link "Ver histórico" mostra a lista de empréstimos via `GET /api/livros/{id}/emprestimos` (modal, painel expansível, ou seção dedicada — escolha do dev)
  - Formulário de filtros inclui campos para `emprestado`, `emprestado_para`, `emprestado_desde`, `emprestado_ate`
  - Mensagens de erro da API (400/404/409) são exibidas em português

---

### T21 — Testes automatizados de empréstimo
Cobrir critérios de US08–US10 e os filtros novos da US06 atualizada.

- **Ref:** US06 (atualizada), US08, US09, US10, RN07–RN11
- **Depende de:** T16, T17, T18, T19
- **Pronto quando:**
  - Testes para cada critério de US08, US09, US10 (sucesso e cada erro 400/404/409)
  - Teste de RN08 (não permite duplo empréstimo ativo)
  - Teste de RN10 (devolução em livro sem ativo retorna 400)
  - Teste de RN09 (datas inválidas em ambas as direções)
  - Teste de RN07 (`LivroResponse` reflete corretamente `emprestado`, `emprestado_para`, `data_emprestimo` antes/depois de empréstimo e devolução)
  - Teste de RN11 (DELETE de livro com empréstimos remove os empréstimos em cascata)
  - Testes dos novos filtros em `GET /api/livros` (`emprestado`, `emprestado_para`, `emprestado_desde`, `emprestado_ate`, combinações)
  - `pytest` roda todos os testes com sucesso, incluindo os pré-existentes

---

### T22 — Atualizar README com a feature de empréstimo
Documentar os 3 novos endpoints, os novos filtros e a UI de empréstimo no README.

- **Ref:** —
- **Depende de:** T20, T21
- **Pronto quando:**
  - Exemplos `curl` para `POST /api/livros/{id}/emprestimos`, `DELETE /api/livros/{id}/emprestimos`, `GET /api/livros/{id}/emprestimos`
  - Exemplos `curl` dos novos filtros em `GET /api/livros`
  - Descrição da UI de empréstimo (botões, fluxo, histórico)
  - Menciona regra de empréstimo ativo único (RN08) e cascata na remoção (RN11)

---

## Resumo de dependências

```
T01 ──► T02 ──► T04, T05, T06, T07, T08
    ├── T03 ─┘                     │
    │                              │
    │             T05 ──► T09 ─────┤
    │                              │
    │                              ▼
    └── T11 ──► T12 ──────────────►│
                                   ▼
                                  T10 ──► T13

T02 ──► T14 ──► T16, T17, T18 ──► T20 ──► T22
    ├── T15 ─┘                       │     │
    │                                │     │
    └── T09 ──► T19 ─────────────────┤     │
                                     ▼     │
                                    T21 ───┘
```

## Ordem sugerida de execução

1. **T01** (setup)
2. **T02** + **T03** + **T11** (em paralelo)
3. **T04–T08** (em paralelo — um dev por endpoint)
4. **T09** (depende de T05)
5. **T12** (frontend — depende dos endpoints)
6. **T10** (integra tudo)
7. **T13** (documentação final da fase 1–3)
8. **T14** + **T15** (modelo e schemas de empréstimo, em paralelo)
9. **T16–T18** (em paralelo — um dev por endpoint de empréstimo)
10. **T19** (filtros novos + ajuste do `LivroResponse`)
11. **T20** (frontend de empréstimo — depende dos endpoints)
12. **T21** (testes integrados)
13. **T22** (atualização final do README)
