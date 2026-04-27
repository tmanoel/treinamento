# Biblioteca Pessoal — User Stories

## US01 — Cadastrar livro

**Como** usuário da biblioteca,  
**quero** cadastrar um livro informando título, autor, editora e ano de publicação,  
**para que** eu possa registrar livros na minha biblioteca pessoal.

**Critérios de aceitação:**
- Todos os campos são obrigatórios
- `lido` é opcional; se não informado, o livro é salvo com `lido: false`
- Retorna `201` com os dados do livro criado, incluindo `id`, `created_at` e `updated_at` gerados pelo servidor
- Retorna `400` com mensagem descritiva se algum campo obrigatório estiver ausente, for enviado como string vazia ou contiver apenas espaços (ex: `"titulo é obrigatório"`; o mesmo vale para `"   "`)
- Retorna `400` com mensagem descritiva se `ano_publicacao` for inválido (ex: `"ano_publicacao deve ser um número inteiro entre 1400 e 2026"`)
- Retorna `409` com mensagem descritiva se já existir um livro com o mesmo título e autor — comparação case-insensitive (ex: `"Já existe um livro com este título e autor"`)

---

## US02 — Listar livros

**Como** usuário da biblioteca,  
**quero** ver todos os livros cadastrados,  
**para que** eu tenha uma visão geral da minha biblioteca.

**Critérios de aceitação:**
- Retorna `200` com a lista de todos os livros
- Retorna lista vazia quando não houver livros cadastrados

---

## US03 — Marcar livro como lido/não lido

**Como** usuário da biblioteca,  
**quero** marcar um livro como lido ou não lido,  
**para que** eu possa acompanhar meu progresso de leitura.

**Critérios de aceitação:**
- Retorna `200` com os dados atualizados
- `updated_at` é atualizado automaticamente
- Retorna `400` com mensagem descritiva se `lido` não for um booleano (ex: `"lido deve ser true ou false"`)
- Retorna `404` com mensagem descritiva se o livro não existir (ex: `"Livro não encontrado"`)

---

## US04 — Editar livro

**Como** usuário da biblioteca,  
**quero** editar os dados de um livro cadastrado,  
**para que** eu possa corrigir informações incorretas.

**Critérios de aceitação:**
- Permite atualizar qualquer campo (`titulo`, `autor`, `editora`, `ano_publicacao`, `lido`)
- Retorna `200` com os dados atualizados
- Retorna `404` com mensagem descritiva se o livro não existir (ex: `"Livro não encontrado"`)
- Retorna `400` com mensagem descritiva se nenhum campo for enviado (ex: `"Informe ao menos um campo para atualizar"`)
- Retorna `400` com mensagem descritiva se algum campo enviado for inválido, string vazia ou contendo apenas espaços (ex: `"autor não pode ser vazio"`)
- Retorna `400` com mensagem descritiva se `ano_publicacao` for inválido (ex: `"ano_publicacao deve ser um número inteiro entre 1400 e 2026"`)
- `updated_at` é atualizado automaticamente
- Retorna `409` com mensagem descritiva se a edição gerar duplicata com outro livro existente — comparação case-insensitive (ex: `"Já existe um livro com este título e autor"`)

---

## US05 — Remover livro

**Como** usuário da biblioteca,  
**quero** remover um livro da minha biblioteca,  
**para que** eu possa manter minha lista organizada.

**Critérios de aceitação:**
- Retorna `204` após remoção bem-sucedida (sem corpo na resposta)
- Retorna `404` com mensagem descritiva se o livro não existir (ex: `"Livro não encontrado"`)

---

## US06 — Buscar e filtrar livros

**Como** usuário da biblioteca,  
**quero** buscar livros por título, autor, editora, ano de publicação, status de leitura ou status de empréstimo,  
**para que** eu encontre rapidamente o livro que procuro.

**Critérios de aceitação:**
- Busca por `titulo`, `autor` ou `editora` é parcial e case-insensitive
- Filtro por `ano_publicacao` é exato (inteiro)
- Filtro por `lido` aceita `true` ou `false`
- Filtro por `emprestado` aceita `true` ou `false` — atua sobre o empréstimo ativo (RN07)
- Busca por `emprestado_para` é parcial e case-insensitive — atua sobre o empréstimo ativo
- Filtros `emprestado_desde` e `emprestado_ate` (datas ISO 8601) delimitam o intervalo de `data_emprestimo` do empréstimo ativo
- Filtros podem ser combinados
- Retorna `200` com a lista filtrada (pode ser vazia)

---

## US07 — Consultar livro por ID

**Como** usuário da biblioteca,  
**quero** consultar os detalhes de um livro específico pelo seu ID,  
**para que** eu possa ver todas as informações de um livro sem precisar listar toda a biblioteca.

**Critérios de aceitação:**
- Retorna `200` com os dados do livro
- Retorna `404` com mensagem descritiva se o livro não existir (ex: `"Livro não encontrado"`)

---

## US08 — Emprestar livro

**Como** usuário da biblioteca,  
**quero** marcar um livro existente como emprestado, registrando para quem emprestei e quando,  
**para que** eu acompanhe quais livros não estão comigo no momento.

**Critérios de aceitação:**
- Retorna `201` com os dados do empréstimo criado (`id`, `livro_id`, `emprestado_para`, `data_emprestimo`, `data_devolucao: null`, `created_at`, `updated_at`)
- Retorna `400` com mensagem descritiva se `emprestado_para` estiver ausente, vazio ou contiver apenas espaços (ex.: `"emprestado_para é obrigatório"`)
- Retorna `400` com mensagem descritiva se `data_emprestimo` for inválida (ex.: `"data_emprestimo não pode ser futura"`, `"data_emprestimo não pode ser anterior à criação do livro"`)
- Retorna `404` com mensagem descritiva se o livro não existir (ex.: `"Livro não encontrado"`)
- Retorna `409` com mensagem descritiva se o livro já possuir um empréstimo ativo (ex.: `"Livro já está emprestado"`)
- Após sucesso, `GET /api/livros/{id}` passa a retornar `emprestado: true` com `emprestado_para` e `data_emprestimo` preenchidos (RN07)

---

## US09 — Devolver livro

**Como** usuário da biblioteca,  
**quero** registrar a devolução de um livro emprestado, informando a data,  
**para que** o sistema reflita que o livro voltou para minha biblioteca e mantenha o histórico.

**Critérios de aceitação:**
- Retorna `200` com os dados do empréstimo encerrado (com `data_devolucao` preenchida)
- Retorna `400` com mensagem descritiva se `data_devolucao` for inválida (ex.: `"data_devolucao não pode ser anterior à data_emprestimo"`, `"data_devolucao não pode ser futura"`)
- Retorna `400` com mensagem descritiva se o livro não tiver empréstimo ativo (ex.: `"Livro não está emprestado"`)
- Retorna `404` com mensagem descritiva se o livro não existir (ex.: `"Livro não encontrado"`)
- Após sucesso, `GET /api/livros/{id}` passa a retornar `emprestado: false` com `emprestado_para` e `data_emprestimo` como `null` (RN07)

---

## US10 — Consultar histórico de empréstimos do livro

**Como** usuário da biblioteca,  
**quero** consultar o histórico completo de empréstimos de um livro,  
**para que** eu saiba para quem e quando emprestei o livro ao longo do tempo.

**Critérios de aceitação:**
- Retorna `200` com a lista de empréstimos do livro (ativos e encerrados), ordenada por `data_emprestimo` desc
- Retorna lista vazia quando o livro nunca foi emprestado
- Retorna `404` com mensagem descritiva se o livro não existir (ex.: `"Livro não encontrado"`)

---

## Requisitos Transversais (RNF01–RNF05)

Aplicam-se a todas as stories acima:

- **RNF01 — API REST:** todos os endpoints seguem o estilo arquitetural REST (recursos nomeados no plural, verbos HTTP semânticos)
- **RNF02 — JSON:** todas as requisições e respostas utilizam `Content-Type: application/json`
- **RNF03 — Persistência:** os dados são preservados entre reinicializações da aplicação
- **RNF04 — Validação de entrada:** o sistema retorna mensagens de erro descritivas quando campos obrigatórios estiverem ausentes ou inválidos (ex: `"titulo é obrigatório"`)
- **RNF05 — Códigos HTTP semânticos:** o sistema utiliza códigos HTTP adequados: `201` para criação, `204` para remoção, `400` para dados inválidos, `404` para recurso não encontrado, `409` para duplicata
