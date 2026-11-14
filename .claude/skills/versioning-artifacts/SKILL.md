---
name: versioning-artifacts
description: "Leva um artefato do claude.ai para o repositorio no GitHub: cria a pasta com o HTML e o artifact.json, faz o commit so dela, o push e abre o pull request. Use quando for criar um artefato de trabalho novo, para que ele ja nasca no repositorio e nao numa pasta temporaria; quando for editar um artefato versionado; quando o usuario pedir para versionar um artefato no GitHub; quando um artefato so existe publicado e precisa ganhar uma pasta; ou quando o manifesto ganhou um link novo que precisa chegar a branch principal. NAO publica no claude.ai: isso e' a skill publishing-artifacts, depois do merge."
---

# Versionar artefatos

A pagina de um artefato mora numa pasta do repositorio, e chega a branch
principal por pull request. So depois do merge ela e' publicada no link oficial,
pela skill `publishing-artifacts`, que busca a pasta no GitHub.

O conteudo anda por `git`: commit e push, por SSH ou pelo que o repositorio ja
usa. O `gh` so abre o pull request. Sem ele, o script devolve o endereco em que a
pessoa abre o PR no navegador.

## O formato

Uma pasta por artefato, perto do codigo a que ele pertence (o Backstage mora em
`backstage-claude/artifact/`; os de arquitetura da plataforma em `artifacts/`):

```
artifacts/portal/
├── index.html
├── arquitetura.html        paginas extras, quando houver
├── ds/theme.js
└── artifact.json
```

```json
{
  "pages": {
    "portal": {
      "file": "index.html",
      "title": "Barte Finance OS",
      "files": ["arquitetura.html", "ds/theme.js"],
      "links": { "max": "https://claude.ai/artifact/...", "team": "https://claude.ai/artifact/..." },
      "capabilities": {}
    }
  },
  "publishOrder": ["portal"]
}
```

- `links` tem uma chave por org: `team` (org Team da Ahrena), `max` (plano
  pessoal), ou o nome da org em minusculas. O script descobre a chave da org
  logada em `~/.claude.json`.
- `capabilities` e' exatamente o que vai no parametro `capabilities` da
  publicacao (`{}` se nenhuma). Um conector (`mcp`) so funciona se a org de
  destino tiver esse conector adicionado com o mesmo nome: confira antes.
- Link fixo para outro artefato nao entra no HTML: escreva
  `{{artefato:<nome da pagina>}}`. O script troca pelo link da org de destino,
  procurando primeiro na mesma pasta e depois em todos os `artifact.json` do repo.
- `publishOrder` poe primeiro a pagina para a qual as outras apontam.

## Levar a pasta para o GitHub

`S=.claude/skills/scripts/artifacts.py`, a partir da raiz do repositório

1. Escreva ou edite o HTML na pasta do artefato, no repositorio. Uma pasta nova
   ganha o `artifact.json` no formato acima, com `links` vazio enquanto a pagina
   nao foi publicada.
2. `python3 $S submit <pasta> --branch <tipo>/<assunto> --message "<mensagem>"`.
   O script cria ou troca para a branch, prepara **so a pasta do artefato**, faz o
   commit, o push e abre o pull request contra a branch principal. A primeira
   linha da mensagem vira o titulo do PR e o resto, o corpo.
3. Leia a resposta: `pull_request` traz o link do PR. Quando vem vazio, `open_at`
   e' o endereco para abrir o PR a mao, e `gh_error` diz por que o `gh` nao abriu.
4. Entregue o link do PR ao usuario. O merge e' dele.

O `submit` recusa duas coisas, e nenhuma se contorna: fazer o commit na branch
principal, e seguir com arquivos preparados fora da pasta do artefato. No segundo
caso, tire esses arquivos do index (`git restore --staged <arquivo>`) e rode de
novo; eles vao num PR proprio.

Para ver a mudanca antes do merge, a skill `publishing-artifacts` publica um
rascunho num link de teste. O link oficial nao muda antes do merge.

## Levar um artefato que so existe publicado

Quando o artefato vive so no claude.ai (sem arquivo no repo):

1. Procure o fonte: o `sourcePath` gravado na sessao que o publicou, e, se ele
   sumiu, o mesmo titulo dentro de HTMLs na pasta de scratchpad daquela sessao
   (`grep -l "<title>Titulo"`). A sessao dona sabe qual versao e' a publicada.
2. Sem fonte em disco, o caminho e' o **Exportar** do menu do artefato, feito pelo
   usuario no navegador. A ferramenta `Artifact` nao le artefatos de outra org,
   nem com link compartilhado.
3. Crie a pasta com `index.html` e `artifact.json`, com o link antigo em
   `links.<org de origem>`, leve a pasta para o GitHub como acima e, depois do merge,
   publique na org nova com a skill `publishing-artifacts`.
4. Avise a sessao que atualiza esse artefato do link novo e de que, daqui em
   diante, ela edita no repo.
5. Apagar o original na org antiga e' irreversivel: so com confirmacao do usuario
   e numa sessao logada naquela org.

## Regra para artefatos novos

Artefato de trabalho novo ja nasce no repositorio: escreva o HTML na pasta do
repo, crie o `artifact.json` e publique a partir dele. Pasta temporaria so para
rascunho.
