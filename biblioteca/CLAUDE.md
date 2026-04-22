# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado do repositório

O repositório está em **fase de especificação** — só existe a pasta [docs/](docs/) com os documentos do projeto. Ainda não há código (`app/`), testes (`tests/`), `requirements.txt` nem `README.md`. As estruturas e comandos descritos nos docs (FastAPI, `uvicorn app.main:app`, `pytest`) são **propostas a serem implementadas**, não estado atual.

Antes de assumir que algo existe (rota, módulo, modelo), confirme lendo os arquivos.

## Documentos e ordem de leitura

Os docs em [docs/](docs/) são a fonte da verdade do projeto e têm dependência entre si — leia nesta ordem quando precisar de contexto completo:

1. [00-constitution.md](docs/00-constitution.md) — princípios não-negociáveis (ler sempre)
2. [01-overview.md](docs/01-overview.md) — escopo do produto e o que está fora
3. [02-requisitos.md](docs/02-requisitos.md) — RFs, RNFs e regras de negócio (RN01–RN06)
4. [03-user-stories.md](docs/03-user-stories.md) — US01–US07 com critérios de aceitação
5. [04-design.md](docs/04-design.md) — stack, modelo de dados, arquitetura em camadas, decisões D01–D07
6. [05-endpoints.md](docs/05-endpoints.md) — contrato HTTP (request/response/status)
7. [06-tasks.md](docs/06-tasks.md) — decomposição em tasks T01–T13 com dependências

## Princípios da constitution (resumo operacional)

Os 10 artigos da [constitution](docs/00-constitution.md) governam toda decisão. Os de maior impacto no dia-a-dia:

- **Spec é a fonte da verdade (Art. 1, 2):** nenhum código sem RF/US/task correspondente. Se a implementação revelar necessidade nova, atualize a spec **antes** do código. PRs devem citar o RF/US/task que implementam.
- **Consistência entre docs (Art. 7):** alterar um doc exige revisar os dependentes na mesma mudança. Se você mudar [02-requisitos.md](docs/02-requisitos.md), verifique [03-user-stories.md](docs/03-user-stories.md), [05-endpoints.md](docs/05-endpoints.md) e [06-tasks.md](docs/06-tasks.md).
- **Decisões explícitas (Art. 8):** toda escolha técnica não-trivial vai na seção "Decisões" de [04-design.md](docs/04-design.md). Se não está documentada, não existe.
- **Simplicidade (Art. 10):** não introduzir abstrações, camadas ou bibliotecas que a spec não exija.
- **Commits pequenos (Art. 9):** uma mudança coesa por commit; não misturar refactor + feature + ajuste de doc.

## Convenções obrigatórias na API

Estas regras aparecem espalhadas pelos docs e valem para qualquer endpoint novo:

- **Prefixo `/api`** para todos os endpoints REST (D07). A raiz `/` é reservada ao frontend estático servido por `StaticFiles(directory="app/static", html=True)`.
- **Mensagens de erro em português** (Art. 4), claras e acionáveis. Ex.: `"titulo é obrigatório"`, não `"invalid input"`.
- **Códigos HTTP semânticos** (Art. 5, RNF05): `201` criação, `204` remoção (sem corpo), `400` dado inválido, `404` não encontrado, `409` duplicata.
- **Validação na borda** (Art. 6): query params e body validados via Pydantic antes de chegar à camada de serviço.
- **Campos gerados pelo servidor** (RN06): `id`, `created_at`, `updated_at` são preenchidos pelo sistema, nunca pelo cliente. `created_at` é imutável; `updated_at` muda a cada modificação.
- **Datas em ISO 8601 UTC**: `created_at`/`updated_at` serializados como `"2026-04-17T10:00:00Z"` ([04-design.md §2](docs/04-design.md)).
- **Mensagem de erro de `ano_publicacao`** interpola o ano corrente em runtime via `datetime.now(tz=UTC).year` (T03). Ex.: `"ano_publicacao deve ser um número inteiro entre 1400 e 2026"`.
- **Coerção de `lido`**: aceita string `"true"`/`"false"` (case-insensitive) **somente** em query params de `GET /api/livros`. No body de `POST`/`PATCH` deve ser booleano JSON estrito.
- **Duplicata** (RN01): comparação case-insensitive de `titulo`+`autor`. No `PATCH`, ignorar o próprio `id` na verificação — reenviar os mesmos `titulo`/`autor` do livro não gera 409.
- **Ordem de validação no PATCH** (T07): (1) body vazio → `"Informe ao menos um campo para atualizar"`; (2) `lido` não booleano; (3) `ano_publicacao` fora do intervalo; (4) campo string vazio/só espaços → `"<campo> não pode ser vazio"`.

## Stack e arquitetura aprovadas

Decisões já fechadas em [04-design.md §5](docs/04-design.md):

- **Python 3.11+ + FastAPI** (D01)
- **SQLite + SQLAlchemy** (D02), arquivo `biblioteca.db` criado automaticamente
- **ID inteiro autoincremento** (D03)
- **`created_at` e `updated_at`** ambos presentes (D04)
- **Único `PATCH /api/livros/{id}`** cobre tanto edição genérica (RF05) quanto marcar como lido (RF04) — `lido` é campo como qualquer outro (D06)
- **Camadas:** `Request → Router → Service → Repository → Database`. Pydantic na borda do Router; regras de negócio (ex.: duplicata) no Service.

Estrutura proposta (ainda não criada — ver [04-design.md §4](docs/04-design.md)):

```
app/{main,models,schemas,repository,service,router}.py
app/static/{index.html,style.css,script.js}
tests/test_livros.py
```

## Comandos (após implementação de T01)

Os docs preveem estes comandos — só funcionarão depois que o respectivo task for executado:

- Subir API (após T01): `uvicorn app.main:app --reload`
- Rodar testes (após T10): `pytest`
- Health check: `GET /api/health` deve retornar `200` com `{"status": "ok"}` (RNF06)

## Idioma

Toda a documentação, mensagens de erro da API e comunicação do projeto são em **português**. Mantenha o mesmo idioma ao editar specs ou escrever código voltado ao usuário final.
