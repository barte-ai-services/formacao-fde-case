---
name: publishing-artifacts
description: "Publica no claude.ai (paginas em claude.ai/artifact/...) um artefato versionado, buscando a pasta dele na branch principal do GitHub, e localiza artefatos pelo titulo ou pelo link. Use quando for publicar ou republicar um artefato de trabalho depois do merge; quando um PR mergeado mudou uma pasta de artefato; quando precisar achar a pasta de um artefato, listar os artefatos de um repositorio ou ler a origem gravada num artefato publicado; quando for levar um artefato para outra org do claude.ai (Max, Team); ou quando uma sessao nao conseguir atualizar um artefato porque ele 'esta em outra org'. NAO cria a pasta nem abre o pull request: isso e' a skill versioning-artifacts. NAO serve para paginas que nao sao artefatos do claude.ai (GitHub Pages, sites)."
---

# Publicar artefatos

O claude.ai hospeda o artefato, mas so guarda uma copia do arquivo do momento em
que alguem publicou. A fonte da verdade e' o repositorio, e publicar e' levar a
pasta do artefato da **branch principal no GitHub** para o link da org.

O `plan` busca a pasta com `git fetch` e `git show`, sem ler o disco. Uma branch
de trabalho, uma copia local atrasada ou uma mudanca nao commitada nao chegam ao
link oficial. Quem publica e' uma sessao do Claude, com a ferramenta `Artifact`: o
claude.ai nao observa o GitHub, e nao ha publicacao a partir de CI.

Esta skill so publica. Criar a pasta, o `artifact.json` e o pull request e' a
skill `versioning-artifacts`, que tambem descreve o formato do manifesto.

## Achar um artefato

`S=.claude/skills/scripts/artifacts.py`, a partir da raiz do repositório

- **No repositorio:** `python3 $S list` imprime, para cada pagina de cada
  `artifact.json` do repo, a pasta, o titulo, o link na org logada e os links das
  outras orgs.
- **A partir de um link:** `python3 $S list --url <link>` devolve so a pasta que
  tem esse link, em qualquer org.
- **A partir do artefato publicado:** toda pagina HTML que sai do `plan` leva a
  origem numa linha de formato fixo, logo depois do `<title>`:

  ```html
  <!-- artifact-source repo="dono/repo" path="artifacts/portal" page="portal" commit="abc1234" -->
  ```

  `Artifact` `action: read` no link mostra essa linha. `dirty="true"` so aparece
  numa publicacao feita com `--local`, e avisa que a pasta tinha mudanca fora do
  commit: aquele link e' um rascunho.

Antes de editar um artefato ja publicado, leia a origem nele e edite no
repositorio indicado. Mudanca feita direto no claude.ai some na proxima publicacao
a partir do repo. Artefato sem a linha de origem ainda nao foi publicado por esta
skill: procure com `list --url` e, se nao achar, siga "Levar um artefato que so
existe publicado", na skill `versioning-artifacts`.

A linha de origem e' escrita pelo `plan`, na copia que vai para o scratchpad. O
arquivo do repositorio nao muda.

## Publicar uma pasta

`S=.claude/skills/scripts/artifacts.py`, a partir da raiz do repositório

1. `python3 $S plan <pasta> --out <scratchpad da sessao>/artefatos`. O script
   busca a pasta na branch principal do GitHub, copia cada pagina para o scratchpad
   com os marcadores trocados (a ferramenta so publica arquivos do diretorio de
   trabalho ou do scratchpad) e imprime `read_from` e, em ordem, `file_path`,
   `files`, `url`, `capabilities` e `source` de cada pagina. Ele para na primeira
   pagina sem link nesta org, porque as seguintes podem precisar dele.
   - Sem o repositorio no disco: `plan <pasta relativa a raiz> --repo dono/nome`.
     O script faz um clone raso, sem arquivos de trabalho, dentro de `--out`.
   - `plan` responde que a pasta nao existe na branch principal quando o pull
     request ainda nao foi mergeado. Nao contorne com `--local`: espere o merge.
   - O `plan` recusa quando a pagina mora em outra org (`home`). Nao contorne: diga
     ao usuario em que org ela mora e que a atualizacao precisa de uma sessao logada
     la. Publicar daqui criaria um link novo, com banco vazio, e o antigo continuaria
     no ar. So use `plan --move` quando o usuario pedir para mudar a pagina de casa,
     e diga antes que o link muda.
2. Se `unresolved` nao estiver vazio, uma pagina aponta para outra que ainda nao
   tem link nesta org: publique a outra antes.
3. Para cada pagina do plano:
   - **com `url`**: `Artifact` `action: read` no `url` (a publicacao num link que a
     conversa nao leu e' recusada) e depois `publish` com `url`, `file_path`,
     `files` e `capabilities`.
   - **sem `url`**: `publish` sem `url`, com `icon` e `description`. Grave o link
     novo: `python3 $S record <pasta> --page <nome> --url <link>`. A primeira
     publicacao define a casa. Numa mudanca de casa (`move: true`), grave o link e
     depois `record <pasta> --page <nome> --home <org nova>`; o link antigo continua
     no manifesto ate o artefato velho ser apagado na org de origem.
4. Se o plano trouxe `remaining`, rode o `plan` de novo e continue.
5. Se o manifesto ganhou um link novo, leve o `artifact.json` num PR, com a skill
   `versioning-artifacts`.

Leia o HTML inteiro antes da primeira publicacao de uma pasta que voce nao
escreveu.

## Publicar um rascunho

`plan <pasta> --local` le do disco, e `--ref <branch>` le uma branch do GitHub que
nao e' a principal. Os dois servem para ver uma mudanca num **link de teste** antes
do merge: publique sem `url`, e nao grave esse link no manifesto. O link oficial
so recebe o que esta na branch principal.

## Depois do merge

O link oficial so muda depois que a mudanca chega a branch principal. Commits,
pushes e PRs em branches de trabalho nao publicam nada.

Nesta copia do repositorio nao ha o hook `PostToolUse` do plugin: nenhum lembrete
chega depois de um `gh pr merge`. Quem mergeia um PR que mexeu numa pasta com
`artifact.json` publica como acima, na mesma sessao. Nao e' preciso atualizar a
copia local antes: o `plan` busca do GitHub.

Se o merge criou um link novo, grave-o com `record` e leve o `artifact.json` num
PR proprio.

Se o usuario pediu para nao publicar agora, diga que ficou pendente. Um
`gh pr merge --auto` ainda nao mergeou: a publicacao fica para depois do merge.
Merge feito fora da sessao (pelo GitHub): publique quando o usuario pedir ou na
proxima vez que mexer na pasta.
