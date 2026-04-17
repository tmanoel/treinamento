# Biblioteca Pessoal — Constitution

Princípios não-negociáveis que regem o projeto. Toda decisão técnica e toda revisão de código deve respeitar estes artigos. Alterações neste documento exigem consenso do grupo.

---

## Artigo 1 — A spec é a fonte da verdade

Nenhum código é escrito sem uma spec correspondente (RF, US ou task). Se durante a implementação surgir uma necessidade não prevista, a spec deve ser atualizada **antes** do código ser escrito.

## Artigo 2 — Rastreabilidade

Todo código deve ser rastreável até uma spec. PRs devem citar explicitamente o RF, US ou task que implementam.

## Artigo 3 — Testes antes do merge

Nenhum endpoint é considerado pronto sem testes cobrindo ao menos os critérios de aceitação da user story correspondente. Testes quebrados na branch principal são tratados como incidente.

## Artigo 4 — Erros descritivos em português

Todas as respostas de erro (`400`, `404`, `409`) devem conter mensagem em português clara e acionável para o cliente (ex: `"titulo é obrigatório"`, não `"invalid input"`).

## Artigo 5 — Códigos HTTP semânticos

Respostas HTTP devem seguir rigorosamente o significado do código: `201` para criação, `204` para remoção, `400` para dado inválido, `404` para recurso não encontrado, `409` para conflito/duplicata.

## Artigo 6 — Validação na borda

Dados externos (query params, body de requisição) são validados via schemas Pydantic antes de chegar à camada de serviço. Nenhuma regra de negócio deve presumir que a entrada é confiável.

## Artigo 7 — Consistência nos docs

Quando um documento for alterado, todos os documentos dependentes devem ser revisados na mesma mudança. Inconsistências entre docs são consideradas defeitos.

## Artigo 8 — Decisões explícitas

Toda escolha técnica não-trivial deve ser registrada no `04-design.md` (seção "Decisões"). Decisões implícitas no código são proibidas — se não está documentada, ela não existe.

## Artigo 9 — Commits pequenos e revisáveis

Cada commit deve representar uma mudança coesa e compreensível. Commits gigantes misturando refactor + feature + ajuste de doc são proibidos.

## Artigo 10 — Simplicidade primeiro

Não introduzir abstrações, camadas ou bibliotecas que a spec não exija. Se não está no design, começa simples — otimização e generalização vêm depois, com justificativa.
