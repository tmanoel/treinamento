# Biblioteca Pessoal — User Stories

## US01 — Cadastrar livro

**Como** usuário da biblioteca,  
**quero** cadastrar um livro informando título, autor, editora e ano de publicação,  
**para que** eu possa registrar livros na minha biblioteca pessoal.

**Critérios de aceitação:**
- Todos os campos são obrigatórios
- O livro é salvo com `lido: false` por padrão
- Retorna `201` com os dados do livro criado
- Retorna `400` com mensagem descritiva se algum campo obrigatório estiver ausente ou vazio (ex: `"titulo é obrigatório"`)
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
- Retorna `400` com mensagem descritiva se algum campo enviado for inválido ou vazio (ex: `"autor não pode ser vazio"`)
- Retorna `400` com mensagem descritiva se `ano_publicacao` for inválido (ex: `"ano_publicacao deve ser um número inteiro entre 1400 e 2026"`)
- Retorna `409` com mensagem descritiva se a edição gerar duplicata com outro livro existente — comparação case-insensitive (ex: `"Já existe um livro com este título e autor"`)

---

## US05 — Remover livro

**Como** usuário da biblioteca,  
**quero** remover um livro da minha biblioteca,  
**para que** eu possa manter minha lista organizada.

**Critérios de aceitação:**
- Retorna `200` ou `204` após remoção bem-sucedida
- Retorna `404` com mensagem descritiva se o livro não existir (ex: `"Livro não encontrado"`)

---

## US06 — Buscar e filtrar livros

**Como** usuário da biblioteca,  
**quero** buscar livros por título, autor ou editora e filtrar por status de leitura,  
**para que** eu encontre rapidamente o livro que procuro.

**Critérios de aceitação:**
- Busca por `titulo`, `autor` ou `editora` é parcial e case-insensitive
- Filtro por `lido` aceita `true` ou `false`
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

## Requisitos Transversais (RNF01, RNF02, RNF03)

Aplicam-se a todas as stories acima:

- **RNF01 — API REST:** todos os endpoints seguem o estilo arquitetural REST (recursos nomeados no plural, verbos HTTP semânticos)
- **RNF02 — JSON:** todas as requisições e respostas utilizam `Content-Type: application/json`
- **RNF03 — Persistência:** os dados são preservados entre reinicializações da aplicação
