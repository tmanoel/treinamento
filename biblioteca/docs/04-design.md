# Biblioteca Pessoal — Design e Arquitetura

> Este documento apresenta propostas técnicas para discussão. O grupo é encorajado a questionar, adaptar ou substituir qualquer decisão aqui registrada antes de iniciar a implementação.

---

## 1. Stack Proposta

| Camada | Proposta | Alternativas |
|---|---|---|
| Linguagem | Python 3.11+ | Node.js, Java, Go |
| Framework | FastAPI | Flask, Django REST, Express |
| Banco de dados | SQLite | PostgreSQL, MongoDB |
| ORM | SQLAlchemy | Tortoise ORM, Peewee |
| Validação | Pydantic (nativo no FastAPI) | Marshmallow, Cerberus |

**Justificativa:**
- **FastAPI** gera documentação OpenAPI automaticamente, útil para o grupo visualizar e testar os endpoints
- **SQLite** elimina a necessidade de instalar e configurar um servidor de banco de dados, reduzindo a fricção para rodar localmente
- **Pydantic** resolve a RNF04 (validação com mensagens descritivas) de forma declarativa, sem código extra

**Pontos para o grupo debater:**
- SQLite é suficiente ou precisamos de PostgreSQL desde o início?
- O grupo tem preferência por outra linguagem/stack?

---

## 2. Modelo de Dados

### Entidade: `Livro`

| Campo | Tipo | Restrições |
|---|---|---|
| `id` | inteiro | chave primária, autoincremento |
| `titulo` | string | obrigatório, não vazio |
| `autor` | string | obrigatório, não vazio |
| `editora` | string | obrigatório, não vazio |
| `ano_publicacao` | inteiro | obrigatório, entre 1400 e ano atual |
| `lido` | booleano | obrigatório, padrão `false` |
| `created_at` | datetime | preenchido automaticamente na criação |
| `updated_at` | datetime | atualizado automaticamente a cada modificação |

**Pontos para o grupo debater:**
- Precisamos de `created_at` / `updated_at` para rastreabilidade?
- O `id` deve ser inteiro sequencial ou UUID?

---

## 3. Arquitetura da Aplicação

### Estrutura de camadas proposta

```
Request → Router → Service → Repository → Database
```

- **Router** — recebe a requisição HTTP e valida o schema de entrada (Pydantic)
- **Service** — aplica as regras de negócio (ex: verificar duplicatas)
- **Repository** — executa as operações no banco de dados

**Justificativa:** separar regras de negócio do acesso a dados facilita os testes unitários e torna o código mais fácil de manter.

**Pontos para o grupo debater:**
- Para um projeto desse tamanho, essa separação é necessária ou é over-engineering?

---

## 4. Estrutura de Pastas Proposta

```
biblioteca/
├── docs/                  # especificações (este diretório)
├── app/
│   ├── main.py            # entrypoint da aplicação
│   ├── models.py          # definição das tabelas (SQLAlchemy)
│   ├── schemas.py         # schemas de validação (Pydantic)
│   ├── repository.py      # acesso ao banco de dados
│   ├── service.py         # regras de negócio
│   └── router.py          # rotas HTTP
├── tests/
│   └── test_livros.py     # testes da API
├── requirements.txt
└── README.md
```

---

## 5. Decisões em Aberto

| # | Decisão | Status |
|---|---|---|
| D01 | Stack definitiva | ✅ Python 3.11+ + FastAPI |
| D02 | SQLite vs PostgreSQL | ✅ SQLite |
| D03 | ID inteiro vs UUID | ✅ ID inteiro autoincremento |
| D04 | Incluir `created_at`/`updated_at` | ✅ Sim, ambos os campos |

---

## 6. Dependências entre Fases

```
01-overview ──► 02-requisitos ──► 03-user-stories ──► 04-design
                                                           │
                                              ┌────────────┴────────────┐
                                              ▼                         ▼
                                        05-endpoints              implementação
                                              │
                                              ▼
                                           testes
```

| Fase | Depende de | Bloqueada por |
|---|---|---|
| `02-requisitos` | `01-overview` | — |
| `03-user-stories` | `02-requisitos` | — |
| `04-design` | `02-requisitos` | Decisões D01–D04 (grupo) |
| `05-endpoints` | `04-design` | Stack e modelo de dados aprovados |
| Implementação | `04-design` + `05-endpoints` | Todos os docs aprovados |
| Testes | `05-endpoints` + `03-user-stories` | Endpoints definidos |

> **Atenção:** as decisões em aberto (seção 5) bloqueiam o avanço para os endpoints e a implementação.
