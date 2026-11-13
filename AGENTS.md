# Regras do repositório do case

Vale para qualquer agente, e para quem trabalha com um. O que vale para o time inteiro vem do Ahrena e não é copiado aqui; o que está aqui só vale neste repositório. `CLAUDE.md` aponta para cá.

Antes de mudar qualquer coisa, leia o [README](README.md) e o [`DOMINGO.md`](DOMINGO.md).

## Este repositório é público

Os alunos da Formação FDE fazem fork dele. Por isso:

- **Nada que entregue as respostas entra aqui antes da hora:**
  - o gabarito (`dados/gabarito/`) só entra no domingo de manhã;
  - o gerador da base e a solução de referência nunca entram.
- **Os três ficam no repositório privado [`formacao-fde-ops`](https://github.com/barte-ai-services/formacao-fde-ops), em `kit-domingo/`.**
- **A base de domingo não se edita à mão.** Ela sai do gerador no ops, com a semente padrão dele, e chega aqui copiada.
- **Nenhum nome de cliente real** no texto nem nos dados. Os testes guardam a lista do que é proibido.
- **Nada de segredo.** O kit não precisa de credencial: roda dentro do Claude Code. Se um grupo precisar guardar alguma, ela fica no `.env`, que não entra no git.

## Issues

As issues deste repositório moram no `formacao-fde-ops`, que é privado. O PR daqui fecha o plano de lá com `Closes barte-ai-services/formacao-fde-ops#N`.

## O gate

`make check` roda os testes (`uv run pytest`) e passa antes do commit. Os testes que dependem do gabarito pulam enquanto ele não está.

## Documentação e nomes

Prosa em português. Código em português também, como o kit já está.
