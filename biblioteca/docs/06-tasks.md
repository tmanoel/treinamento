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
  - Endpoint `GET /` (health check) retorna `200`

---

### T02 — Camada de persistência (SQLite + SQLAlchemy)
Configurar o SQLAlchemy, criar a sessão do banco e o modelo `Livro` com todos os campos definidos no design.

- **Ref:** design §2, RNF03
- **Depende de:** T01
- **Pronto quando:**
  - Arquivo `biblioteca.db` é criado automaticamente ao subir a aplicação
  - Tabela `livros` tem todos os campos: `id`, `titulo`, `autor`, `editora`, `ano_publicacao`, `lido`, `created_at`, `updated_at`
  - `created_at` e `updated_at` são preenchidos automaticamente

---

### T03 — Schemas de validação (Pydantic)
Criar os schemas de request/response em `schemas.py` e as validações baseadas nas regras de negócio.

- **Ref:** RN04, RN05, RNF02, RNF04
- **Depende de:** T01
- **Pronto quando:**
  - Schema `LivroCreate`, `LivroUpdate`, `LivroResponse` definidos
  - Validação `ano_publicacao` entre 1400 e ano atual (RN04)
  - Validação de strings não vazias nem só espaços (RN05)
  - Erros retornam mensagens descritivas em português (RNF04)

---

## Fase 2 — Endpoints

### T04 — POST /livros (cadastrar livro)
Implementar o endpoint de cadastro com verificação de duplicata.

- **Ref:** RF01, RF02, RN01, RN02, US01
- **Depende de:** T02, T03
- **Pronto quando:**
  - `POST /livros` retorna `201` em sucesso
  - Retorna `400` se campo obrigatório ausente/vazio ou `ano_publicacao` inválido
  - Retorna `409` se já existir livro com mesmo `titulo`+`autor` (case-insensitive)
  - Livro criado tem `lido: false` por padrão

---

### T05 — GET /livros (listar)
Implementar listagem sem filtros.

- **Ref:** RF03, US02
- **Depende de:** T02, T03
- **Pronto quando:**
  - `GET /livros` retorna `200` com array de livros
  - Retorna array vazio quando não há livros cadastrados

---

### T06 — GET /livros/{id} (consultar por ID)
Implementar consulta de um livro específico.

- **Ref:** RF08, US07
- **Depende de:** T02, T03
- **Pronto quando:**
  - `GET /livros/{id}` retorna `200` com os dados do livro
  - Retorna `404` com mensagem descritiva quando livro não existe

---

### T07 — PATCH /livros/{id} (editar e marcar lido/não lido)
Implementar edição parcial do livro. Esta task cobre tanto a edição genérica quanto a ação específica de marcar como lido/não lido.

- **Ref:** RF05, RF06, RN03, US03, US04
- **Depende de:** T02, T03
- **Pronto quando:**
  - Permite atualizar qualquer campo (`titulo`, `autor`, `editora`, `ano_publicacao`, `lido`)
  - Retorna `200` com os dados atualizados
  - Retorna `400` se campo inválido
  - Retorna `404` se livro não existe
  - Retorna `409` se a edição gerar duplicata
  - `updated_at` é atualizado automaticamente

---

### T08 — DELETE /livros/{id} (remover)
Implementar remoção de livro.

- **Ref:** RF06 (remoção), US05
- **Depende de:** T02
- **Pronto quando:**
  - `DELETE /livros/{id}` retorna `204 No Content` em sucesso
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
Escrever testes cobrindo os critérios de aceitação de todas as user stories.

- **Ref:** todas as US (US01–US07)
- **Depende de:** T04, T05, T06, T07, T08, T09
- **Pronto quando:**
  - Todos os critérios de aceitação das user stories têm ao menos um teste
  - `pytest` roda todos os testes com sucesso
  - Testes usam banco em memória (não afeta `biblioteca.db`)

---

### T11 — Servir arquivos estáticos do frontend
Configurar o FastAPI para servir a pasta `app/static/` e criar o arquivo inicial `index.html` mínimo.

- **Ref:** design §4 (Frontend)
- **Depende de:** T01
- **Pronto quando:**
  - `GET /` serve `index.html` da pasta `static/`
  - Estrutura `app/static/` com `index.html`, `style.css`, `script.js` existe (podem estar vazios)

---

### T12 — Frontend funcional (HTML + JS)
Implementar a interface simples para testar a API pelo navegador.

- **Ref:** design §4 (Frontend)
- **Depende de:** T04, T05, T07, T08, T09, T11
- **Pronto quando:**
  - Formulário de cadastro envia `POST /livros` e exibe mensagem de sucesso/erro
  - Lista exibe todos os livros com botões de editar, remover e marcar como lido
  - Campo de busca consome `GET /livros?titulo=...` e atualiza a lista
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
```

## Ordem sugerida de execução

1. **T01** (setup)
2. **T02** + **T03** + **T11** (em paralelo)
3. **T04–T08** (em paralelo — um dev por endpoint)
4. **T09** (depende de T05)
5. **T12** (frontend — depende dos endpoints)
6. **T10** (integra tudo)
7. **T13** (documentação final)
