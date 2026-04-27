# Biblioteca Pessoal — Requisitos

## Requisitos Funcionais

### RF01 — Cadastrar livro
O sistema deve permitir o cadastro de um livro com os campos:
- `titulo` (obrigatório)
- `autor` (obrigatório)
- `ano_publicacao` (obrigatório)
- `editora` (obrigatório)

### RF02 — Impedir duplicatas
O sistema deve rejeitar o cadastro de um livro com o mesmo título e autor de um livro já existente.

### RF03 — Listar livros
O sistema deve retornar todos os livros cadastrados.

### RF04 — Marcar livro como lido/não lido
O sistema deve permitir atualizar o status de leitura de um livro (`lido: true | false`).

### RF05 — Editar livro
O sistema deve permitir a atualização dos dados de um livro existente pelo seu ID.

### RF06 — Remover livro
O sistema deve permitir a exclusão de um livro pelo seu ID.

### RF07 — Buscar e filtrar livros
O sistema deve permitir buscar livros por:
- `titulo` (busca parcial, case-insensitive)
- `autor` (busca parcial, case-insensitive)
- `editora` (busca parcial, case-insensitive)
- `ano_publicacao` (filtro exato)
- `lido` (filtro exato: `true | false`)
- `emprestado` (filtro exato: `true | false`) — atua sobre o empréstimo ativo (ver RN07)
- `emprestado_para` (busca parcial, case-insensitive) — atua sobre o empréstimo ativo
- `emprestado_desde` (data ISO 8601, filtro `>=`) — sobre `data_emprestimo` do empréstimo ativo
- `emprestado_ate` (data ISO 8601, filtro `<=`) — sobre `data_emprestimo` do empréstimo ativo

### RF08 — Consultar livro por ID
O sistema deve retornar os dados de um livro específico pelo seu ID.

### RF09 — Emprestar livro
O sistema deve permitir registrar o empréstimo de um livro existente, informando `emprestado_para` (string não vazia) e `data_emprestimo`. Cria um novo registro de empréstimo ativo (sem `data_devolucao`).

### RF10 — Devolver livro
O sistema deve permitir registrar a devolução do livro emprestado, informando `data_devolucao`. Encerra o empréstimo ativo correspondente.

### RF11 — Consultar histórico de empréstimos do livro
O sistema deve retornar o histórico completo de empréstimos (ativos e encerrados) de um livro específico pelo seu ID.

### RF12 — Filtrar livros por empréstimo
O sistema deve permitir filtrar a lista de livros por status de empréstimo, pessoa para quem foi emprestado e período de empréstimo (ver query params em RF07).

---

## Requisitos Não Funcionais

### RNF01 — API REST
A interface do sistema deve seguir o estilo arquitetural REST.

### RNF02 — Formato de dados
Todas as requisições e respostas devem utilizar JSON.

### RNF03 — Persistência
Os dados devem ser persistidos entre reinicializações da aplicação.

### RNF04 — Validação de entrada
O sistema deve retornar mensagens de erro descritivas quando campos obrigatórios estiverem ausentes ou inválidos (ex: `"titulo é obrigatório"`).

### RNF05 — Códigos HTTP semânticos
O sistema deve utilizar códigos HTTP adequados: `201` para criação, `204` para remoção, `400` para dados inválidos, `404` para recurso não encontrado, `409` para duplicata.

### RNF06 — Health check
O sistema deve expor um endpoint de verificação de disponibilidade (`GET /api/health`) que retorne `200 OK` com corpo `{"status": "ok"}` quando a aplicação estiver operacional. Destinado a verificações externas (monitoramento, smoke tests).

---

## Regras de Negócio

### RN01 — Duplicata
Dois livros são considerados duplicatas quando possuem o mesmo `titulo` e `autor` (comparação case-insensitive). Na edição (`PATCH`), a verificação deve ignorar o próprio livro pelo `id` — atualizar um livro mantendo seus próprios `titulo`/`autor` não é duplicata.

### RN02 — Status padrão
`lido` é opcional no cadastro. Se não informado, o livro é criado com `lido: false`.

### RN03 — Campos editáveis
Todos os campos (`titulo`, `autor`, `editora`, `ano_publicacao`, `lido`) podem ser atualizados via RF05.

### RN04 — Ano de publicação válido
`ano_publicacao` deve ser um número inteiro entre 1400 e o ano corrente. Valores fora desse intervalo devem ser rejeitados.

### RN05 — Campos obrigatórios não vazios
Campos obrigatórios não podem ser enviados como string vazia ou contendo apenas espaços.

### RN06 — Campos gerados pelo servidor
Todo livro possui `id`, `created_at` e `updated_at` gerados automaticamente pelo sistema — não são informados pelo usuário. `created_at` é preenchido na criação e nunca alterado. `updated_at` é preenchido na criação e atualizado a cada modificação do registro.

### RN07 — Estado "emprestado" é derivado
O campo `emprestado` exibido no `LivroResponse` é calculado em runtime: `true` se existe um empréstimo ativo (registro de `Emprestimo` com `data_devolucao IS NULL`) para o livro, `false` caso contrário. Não é coluna na tabela `livros`. Quando `emprestado=true`, os campos `emprestado_para` e `data_emprestimo` na resposta refletem o empréstimo ativo; quando `false`, são `null`.

### RN08 — Empréstimo ativo único
Cada livro pode ter, no máximo, **um** empréstimo ativo (sem `data_devolucao`) por vez. Tentativa de criar novo empréstimo enquanto já existe um ativo deve ser rejeitada com `409 Conflict` e mensagem `"Livro já está emprestado"`.

### RN09 — Validação de datas de empréstimo
- `data_emprestimo` deve ser `<=` `now(UTC)` (não pode ser futura) e `>=` `created_at` do livro (não pode ser anterior à criação do livro). Mensagens: `"data_emprestimo não pode ser futura"`, `"data_emprestimo não pode ser anterior à criação do livro"`.
- `data_devolucao` deve ser `>=` `data_emprestimo` do empréstimo ativo e `<=` `now(UTC)`. Mensagens: `"data_devolucao não pode ser anterior à data_emprestimo"`, `"data_devolucao não pode ser futura"`.

### RN10 — Devolução exige empréstimo ativo
Tentativa de devolução em livro que não possui empréstimo ativo deve ser rejeitada com `400 Bad Request` e mensagem `"Livro não está emprestado"`.

### RN11 — Cascata na remoção do livro
Ao remover um livro (`DELETE /api/livros/{id}`), todos os empréstimos relacionados (ativos e históricos) são removidos em cascata (FK `ON DELETE CASCADE`). Não há órfãos.
