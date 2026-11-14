# Skills do projeto

As skills desta pasta aparecem para qualquer sessão do Claude Code aberta na raiz do case.

## A do setup

`setup-fde` é deste repositório. As skills do kit de domingo chegam com ele.

## As de artefato: cópia do Ahrena

`publishing-artifacts` e `versioning-artifacts`, com o `scripts/artifacts.py` de que as duas dependem, são cópia do plugin `ahrena-artifacts`.

- **Origem:** `ahrenatechnology/ahrena-plugins-marketplace`, em `plugins/ahrena-artifacts`. É um repositório privado, e por isso as skills estão copiadas aqui: a turma não tem acesso a ele.
- **Versão:** 0.5.0.
- **O que mudou na cópia:**
  - as skills acham o script em `.claude/skills/scripts/artifacts.py`, a partir da raiz do repositório;
  - o texto sobre o hook virou um aviso de que ele não veio.
- **O hook não vem junto.** O plugin tem um hook `PostToolUse` no `Bash` que, depois de um `gh pr merge` que mexeu numa pasta de artefato, lembra de publicar. Aqui não há esse hook: quem mergeia publica na mesma sessão, pela `publishing-artifacts`.

Para atualizar, copie de novo as duas pastas e o script de uma versão nova do plugin, refaça os dois ajustes acima e troque a versão neste README.

## Quem publica a arquitetura

A página de `artifacts/arquitetura-ja-chegou/` mora na org da Barte (`home: team`), e só a Barte a republica, no link gravado no `artifact.json`. Num fork, não rode o `plan` dessa pasta para o link oficial: a sua sessão não alcança esse link. Para ver uma cópia sua, publique um rascunho (`plan --local`, publicação sem `url`) e não grave esse link no manifesto.

A pasta `scripts/` não é uma skill: não tem `SKILL.md`, e o Claude Code não a carrega como skill.
