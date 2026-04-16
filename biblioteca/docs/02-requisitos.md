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

### RF04 — Consultar livro por ID
O sistema deve retornar os dados de um livro específico a partir do seu ID.

### RF05 — Marcar livro como lido/não lido
O sistema deve permitir atualizar o status de leitura de um livro (`lido: true | false`).

---

## Requisitos Não Funcionais

### RNF01 — API REST
A interface do sistema deve seguir o estilo arquitetural REST.

### RNF02 — Formato de dados
Todas as requisições e respostas devem utilizar JSON.

### RNF03 — Persistência
Os dados devem ser persistidos entre reinicializações da aplicação.

---

## Regras de Negócio

### RN01 — Duplicata
Dois livros são considerados duplicatas quando possuem o mesmo `titulo` e `autor` (comparação case-insensitive).

### RN02 — Status padrão
Todo livro recém-cadastrado deve ter `lido: false` por padrão.

### RN03 — Campos imutáveis após cadastro
`titulo`, `autor` e `ano_publicacao` não podem ser alterados após o cadastro. Apenas `lido` pode ser atualizado.
