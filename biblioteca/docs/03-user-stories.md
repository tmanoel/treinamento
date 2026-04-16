# Biblioteca Pessoal — User Stories

## US01 — Cadastrar livro

**Como** usuário da biblioteca,  
**quero** cadastrar um livro informando título, autor, editora e ano de publicação,  
**para que** eu possa registrar livros na minha biblioteca pessoal.

**Critérios de aceitação:**
- Todos os campos são obrigatórios
- O livro é salvo com `lido: false` por padrão
- Retorna `201` com os dados do livro criado
- Retorna `400` se algum campo obrigatório estiver ausente ou vazio
- Retorna `400` se `ano_publicacao` for inválido (fora do intervalo 1400–ano atual)
- Retorna `409` se já existir um livro com o mesmo título e autor

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
- Retorna `404` se o livro não existir

---

## US04 — Editar livro

**Como** usuário da biblioteca,  
**quero** editar os dados de um livro cadastrado,  
**para que** eu possa corrigir informações incorretas.

**Critérios de aceitação:**
- Permite atualizar qualquer campo (`titulo`, `autor`, `editora`, `ano_publicacao`, `lido`)
- Retorna `200` com os dados atualizados
- Retorna `404` se o livro não existir
- Retorna `400` se algum campo enviado for inválido ou vazio
- Retorna `409` se a edição gerar duplicata com outro livro existente

---

## US05 — Remover livro

**Como** usuário da biblioteca,  
**quero** remover um livro da minha biblioteca,  
**para que** eu possa manter minha lista organizada.

**Critérios de aceitação:**
- Retorna `200` ou `204` após remoção bem-sucedida
- Retorna `404` se o livro não existir

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
