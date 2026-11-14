---
name: setup-fde
description: Prepara ou confere a máquina para a Formação FDE. Inspeciona o computador, instala o que falta (git, GitHub CLI, Node.js com npm, uv, Python 3.12, Docker com Colima no macOS e Docker Engine no Linux, Supabase CLI, Cloudflare Wrangler, Claude Code, os plugins do Ahrena), deixa o fork do case com origin e upstream certos, roda o uv sync e o verificador do case, e acompanha a pessoa nos logins que só ela pode fazer (GitHub, Supabase, Cloudflare). Use quando a pessoa pedir "configura o meu setup", "configura o meu setup de FDE", "setup de FDE", "prepara a minha máquina", "o que falta instalar", "meu ambiente não funciona", ou quando uma ferramenta, o login do GitHub ou o fork do case estiver faltando.
---

# Setup de FDE

Esta skill deixa a máquina da pessoa pronta para a Formação FDE. Uma rodada serve tanto para uma máquina nova quanto para uma que já está em uso: o script lê a máquina primeiro e só mexe no que não está `ok`. Rodar de novo não custa nada.

Quem está do outro lado não programa no dia a dia. Explique cada passo em uma frase simples, sem jargão, e mostre o comando inteiro quando a pessoa tiver que rodar alguma coisa.

Rode todos os comandos a partir da raiz do case (a pasta `formacao-fde-case`).

## 1. Inspecionar a máquina

```sh
bash .claude/skills/setup-fde/scripts/setup-fde.sh check
```

Ele imprime uma linha por item: o status, o item e um detalhe. Não muda nada.

| Status | O que quer dizer |
|---|---|
| `ok` | nada a fazer |
| `missing`, `outdated` | o passo 2 resolve |
| `manual` | a pessoa age, e o detalhe é o comando que ela roda |

Os itens, na ordem:

| Item | O que confere |
|---|---|
| `brew` | o Homebrew, só no macOS |
| `git` | o git funciona e é 2.45 ou mais novo (o Claude Code precisa dele para instalar os plugins do Ahrena); no macOS, também as ferramentas de linha de comando da Apple. Um git velho sai `outdated`: no Ubuntu o `fix` traz o git atual do PPA `git-core`, no Mac o do Homebrew |
| `gh`, `claude` | as ferramentas estão instaladas |
| `node` | o Node.js e o npm estão instalados, e o Node.js é o 22 ou mais novo, que o Wrangler pede (senão sai `outdated`, e o `fix` atualiza) |
| `uv` | o uv está instalado e é novo o bastante para o `uv sync --check` (senão sai `outdated`, e o `fix` atualiza) |
| `python` | o uv tem um Python 3.12 ou mais novo |
| `docker` | o cliente do Docker está instalado: no macOS pelo Homebrew, no Ubuntu o Docker Engine pelo `get.docker.com`. Nunca o Docker Desktop |
| `colima` | o motor do Docker no macOS, só lá. Um Mac em que o `docker` já responde com outro motor fica `ok` |
| `docker-daemon` | o motor responde ao `docker info`. No macOS o `fix` roda `colima start`; no Ubuntu é `manual`, porque ligar o serviço e entrar no grupo `docker` pedem `sudo` e um terminal novo |
| `supabase` | o Supabase CLI: no macOS pelo `supabase/tap/supabase`, no Ubuntu o binário do último release em `~/.local/bin`. Nunca pelo `npm -g`, que o Supabase não aceita |
| `wrangler` | o Wrangler da Cloudflare, pelo npm em `~/.local` (sem `sudo`). Espera o `node` |
| `git-identity` | o git sabe o nome e o e-mail da pessoa |
| `gh-login` | o GitHub CLI está logado na conta da pessoa |
| `supabase-login` | o Supabase CLI está logado (`supabase projects list` responde) |
| `wrangler-login` | o Wrangler está logado (`wrangler whoami` mostra a conta) |
| `case-clone` | a pasta é o clone do fork da pessoa: `origin` é o fork e `upstream` é o `barte-ai-services/formacao-fde-case` |
| `uv-sync` | a `.venv` do case está em dia com o `uv.lock` |
| `check-setup` | o verificador do case (`python3 scripts/check_setup.py`) passa |
| `ahrena` | os plugins do Ahrena que o `.claude/settings.json` do case liga estão instalados e habilitados no Claude Code, para a pessoa ou para a pasta do case (o `fix` instala os que faltam) |

Mostre à pessoa as linhas que não estão `ok` antes de mudar qualquer coisa. Se todas estão `ok`, diga isso e pare.

## 2. Corrigir o que um script corrige

```sh
bash .claude/skills/setup-fde/scripts/setup-fde.sh fix
```

Ele instala cada item `missing` ou `outdated`, deixa os `ok` como estão e imprime o relatório de novo. Para corrigir um item só, diga qual: `fix uv-sync`.

Duas falhas aparecem aqui.

**A instalação pede senha.** No Ubuntu (e no Ubuntu do WSL) o git, o gh, o Node.js e o Docker entram pelo `sudo`, e esta sessão não tem terminal para a pessoa digitar a senha. O item continua `missing` e o script diz `não deu para corrigir`. Veja o caminho da pasta do case com `pwd` e dê à pessoa o comando completo para ela rodar no terminal dela, com o caminho de verdade no lugar de `<pasta do case>`:

```sh
cd <pasta do case> && bash .claude/skills/setup-fde/scripts/setup-fde.sh fix
```

Depois continue do passo 1.

**O sistema não tem instalador.** O macOS precisa do Homebrew antes, e mostra `brew` como `manual` até ele estar lá. O Homebrew também instala as ferramentas de linha de comando da Apple; sem ele, o `git` sai `manual` com `xcode-select --install`, e a pessoa aceita a janela da Apple. Um sistema que não é macOS, Debian nem Ubuntu mostra as ferramentas como `manual`: a pessoa instala do jeito dela, seguindo o `SETUP.md`.

## 3. Acompanhar a pessoa em cada item manual

Pegue as linhas `manual` na ordem em que aparecem. A ordem importa: o `gh-login` vem antes do `case-clone`, porque o fork é feito com a conta do GitHub.

Para cada uma, passe o comando do detalhe e espere a pessoa rodar. Abra `references/acessos.md` para os itens que pedem mais de um comando: o login do GitHub, o fork e o clone, os logins do Supabase e da Cloudflare, o motor do Docker no Ubuntu, e o Windows.

**Regras de segurança, sem exceção:**

- Nunca faça um login pela pessoa. O `gh auth login`, o `supabase login`, o `wrangler login` e o login do Claude Code abrem o navegador do lado dela, e é ela quem roda.
- Nunca peça para colar um token, uma senha ou uma chave na conversa. Um segredo digitado aqui é um segredo vazado. Se a pessoa colar um mesmo assim, diga para ela revogar e gerar outro.
- Quando o comando precisa de `sudo` e esta sessão não tem terminal, não tente contornar: passe o comando para a pessoa rodar no terminal dela.

**O `ahrena`.** O `fix` instala os plugins que faltam com `claude plugin install <plugin>@ahrena --scope local`, que grava no `.claude/settings.local.json` (fora do git) e deixa o `settings.json` do fork como está. Ele só tenta depois que o `git` está `ok`: com o git 2.34 do Ubuntu 22.04, a instalação cai. Depois, a pessoa fecha o Claude Code e abre uma sessão nova na pasta do case, e `/agents` mostra a `athena`.

Um item pode estar fora das mãos da pessoa, como a conta do Claude Code que os organizadores entregam. Anote quem destrava e siga em frente.

## 4. Confirmar

Rode o passo 2 mais uma vez, porque um item manual destrava outros: o `uv-sync` e o `ahrena` só andam depois do `case-clone`. Depois rode o passo 1.

O setup terminou quando o `check` sai 0. Se não sair, diga exatamente quais itens faltam e quem destrava cada um. Não diga que a máquina está pronta com uma linha que não está `ok`.

## 5. Entregar

Com tudo `ok`, aponte o [README](../../../README.md) para o jeito de trabalhar com o fork e o fork líder, e o [DOMINGO.md](../../../DOMINGO.md) para o kit de domingo. Lembre a pessoa de abrir uma sessão nova do Claude Code na pasta do case depois de um `git pull`.

## O ovo e a galinha

Esta é uma skill do projeto: ela só carrega numa sessão do Claude Code aberta dentro da pasta do case. Quem ainda não tem o clone tem dois caminhos:

- abrir o Claude Code numa pasta qualquer e pedir para instalar o git e o GitHub CLI, fazer o login (a pessoa roda o `gh auth login`) e rodar `gh repo fork barte-ai-services/formacao-fde-case --clone`; ou
- seguir o `SETUP.md` à mão até o clone.

Depois, abrir uma sessão nova do Claude Code dentro da pasta `formacao-fde-case` e pedir de novo "configura o meu setup de FDE".

## Mudando o script

`scripts/test-setup-fde.sh` é a suíte. Ela monta uma caixa de areia com dublês de cada comando, então não lê nem muda nada da máquina de verdade, e roda no `make check`. Rode antes e depois de mexer no `scripts/setup-fde.sh`. Um item novo no script ganha um caso lá.

## Quando esta skill não se aplica

**Windows fora do WSL.** O script não tem instalador para o Windows. O caminho é o WSL 2 com Ubuntu, onde esta skill roda como em qualquer Ubuntu; o `references/acessos.md` tem o comando que leva até lá.

**Uma ferramenta instalada que não funciona.** O script decide se a ferramenta está lá, não se está saudável. Uma instalação quebrada é um diagnóstico, e começa pela mensagem de erro.

**O kit de domingo.** Rodar o agente, as skills dele e o eval está no `DOMINGO.md`.
