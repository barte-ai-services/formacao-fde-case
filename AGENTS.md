# Regras do repositório do case

Vale para qualquer agente, e para quem trabalha com um. O que vale para o time inteiro vem do Ahrena e não é copiado aqui; o que está aqui só vale neste repositório. `CLAUDE.md` aponta para cá.

Antes de mudar qualquer coisa, leia o [README](README.md). O kit de domingo, com o `DOMINGO.md`, só chega aqui no domingo de manhã; até lá ele fica guardado no `formacao-fde-ops`.

## Este repositório é público

Os alunos da Formação FDE fazem fork dele. Por isso:

- **Nada que entregue as respostas entra aqui antes da hora:**
  - o kit de domingo (agente, skills, servidor MCP, base, baseline e eval) só entra no domingo às 8h30, e o gabarito (`dados/gabarito/`) também só no domingo de manhã;
  - o gerador da base e a solução de referência nunca entram.
- **Até a hora deles, todos ficam no repositório privado [`formacao-fde-ops`](https://github.com/barte-ai-services/formacao-fde-ops), em `kit-domingo/`.**
- **A base de domingo não se edita à mão.** Ela sai do gerador no ops, com a semente padrão dele, e chega aqui copiada.
- **Nenhum nome de cliente real** no texto nem nos dados. Os testes guardam a lista do que é proibido.
- **Nada de segredo.** O kit não precisa de credencial: roda dentro do Claude Code. Se um grupo precisar guardar alguma, ela fica no `.env`, que não entra no git.

## Issues

As issues deste repositório moram no `formacao-fde-ops`, que é privado. O PR daqui fecha o plano de lá com `Closes barte-ai-services/formacao-fde-ops#N`.

## O gate

`make check` roda os testes (`uv run pytest`) e passa antes do commit. Os testes do kit de domingo chegam com ele; os que dependem do gabarito pulam enquanto ele não está.

## Documentação e nomes

Prosa em português. Código em português também, como o kit já está.

<!-- ahrena:agency:start -->
## Build work enters through the agency

Build work enters through a session that takes the role of the `athena` agent
(`ahrena-engineering-development:athena`, opened with `/issue-tl` on Claude Code):
the session reads her definition and is the tech lead of the issue until it ends.
She plans the issue, routes the concern, and delegates each layer to `iris`
(frontend), `apollo` (backend) or `clio` (data), running the develop→Argos loop
(at most three rounds) before each stacked pull request. Do not implement build
work directly. Where a session cannot take her role, call her as a subagent and
write what she returns for the person under `person-facing-text`, never pasting
her protocol block. Athena orchestrates; she does not write production code, pass
a review verdict, or apply a fix.
<!-- ahrena:agency:end -->
