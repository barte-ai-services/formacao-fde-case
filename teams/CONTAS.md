# Contas do grupo no Supabase e na Cloudflare

O grupo constrói com o Supabase (banco e autenticação) e publica com a Cloudflare (Workers). Quem cria as duas contas é o **líder do grupo**, o dono do fork líder. Depois ele convida os integrantes, e todo mundo trabalha nas mesmas contas.

As duas contas são gratuitas. Ninguém precisa de cartão de crédito.

## Já tem conta? Crie uma segunda só para a formação

Se você já usa o Supabase ou a Cloudflare no trabalho, não misture. Crie uma conta nova com o seu e-mail mais um `+formacao-fde` antes do `@`:

```
seu.email+formacao-fde@dominio.com
```

Os e-mails chegam na sua caixa de sempre, mas os serviços enxergam um endereço novo. Dois cuidados:

- **Crie a conta com e-mail e senha**, não com "entrar com o GitHub" ou com o Google: esses botões levam de volta à conta que você já tem.
- **Passe ao líder o endereço exato, com o `+`.** O convite tem de ir para ele.

O Gmail e o Google Workspace aceitam o `+`. Outros provedores podem não aceitar: se o e-mail de confirmação não chegar, use outro endereço.

## Supabase: o líder cria

1. Entre em [supabase.com](https://supabase.com), clique em **Start your project** e crie a conta (com o GitHub ou com e-mail).
2. Crie uma **organização** no plano **Free**, com o nome do grupo (por exemplo, `formacao-fde-grupo-1`).
3. Dentro dela, clique em **New project**:
   - **Name:** o nome do grupo;
   - **Database password:** gere uma senha forte e guarde num gerenciador de senhas. Ela não vai para o repositório;
   - **Region:** South America (São Paulo).
4. Espere o projeto ficar pronto.

No plano gratuito, um projeto parado por uma semana é pausado. Se isso acontecer, é só reativar no painel.

### Supabase: convidar o grupo

1. Abra a página **Team** da organização: [supabase.com/dashboard/org/_/team](https://supabase.com/dashboard/org/_/team).
2. Convide o e-mail de cada integrante com o papel **Developer**.
3. Cada integrante aceita o convite pelo e-mail. O convite vale por 24 horas: se vencer, convide de novo.

O plano gratuito não limita o número de membros. O papel **Developer** usa o banco e lê as chaves do projeto, mas não muda as configurações do projeto (autenticação, e-mail, API) nem a senha do banco. Essas mudanças ficam com o líder.

Depois, cada um liga a própria máquina ao projeto:

```bash
supabase login
supabase link --project-ref <ref-do-projeto>
```

O `supabase` e o `wrangler` já vêm instalados pela skill `setup-fde`.

O `ref` do projeto aparece no endereço do painel: `supabase.com/dashboard/project/<ref>`.

## Cloudflare: o líder cria

1. Entre em [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up), crie a conta e confirme o e-mail.
2. No painel, abra **Compute & AI** → **Workers & Pages** uma vez, para ativar os Workers no plano gratuito.
3. Se o painel pedir um subdomínio `workers.dev`, use o nome do grupo.

### Cloudflare: convidar o grupo

1. No painel da conta, abra a página **Members**.
2. Clique em **Invite members** e informe o e-mail de cada integrante.
3. Na política de permissão, escolha a conta inteira como escopo e um papel que permita publicar Workers (por exemplo, **Administrator**), e confirme.
4. Cada integrante aceita o convite pelo e-mail.

Os nomes dos menus da Cloudflare mudam com frequência. Se algum não bater, procure por **Members** no painel.

Depois, cada um entra pelo terminal:

```bash
wrangler login
```

Quem tem acesso a mais de uma conta na Cloudflare (a pessoal e a do grupo) escolhe a do grupo no primeiro `wrangler deploy`, quando ele perguntar, ou fixa o `account_id` da conta do grupo no arquivo de configuração do Wrangler (`wrangler.jsonc` ou `wrangler.toml`).

## Servidor MCP em Python: na conta do grupo na Cloudflare

O servidor MCP do grupo roda como um **Python Worker** na mesma conta da Cloudflare. Não tem conta nova, ninguém precisa ser convidado de novo, e não tem servidor para manter: a Cloudflare sobe o Worker quando o Claude Code chama, sem custo no plano gratuito.

O ponto de partida é o exemplo oficial da Cloudflare, um servidor MCP em Python com o SDK oficial do MCP: [python-workers-examples/mcp-server](https://github.com/cloudflare/python-workers-examples/tree/main/mcp-server).

### Criar o servidor no fork

No fork líder, peça ao Claude Code:

> Copie o exemplo `mcp-server` do repositório `cloudflare/python-workers-examples` para a pasta `servidor-mcp/` deste fork. Chame o Worker de `ja-chegou-mcp` no `wrangler.jsonc`. Tire o banco D1 do `wrangler.jsonc` e do código: os dados ficam no Supabase. Troque as tools do exemplo pelas tools do caso, lendo e gravando no Supabase pela API REST, entrando como o usuário `agente`.

Os dados ficam no Supabase, como na [arquitetura de referência](../artifacts/arquitetura-ja-chegou/index.html): o banco, o login das pessoas e as regras de quem pode o quê (RLS) moram lá. O exemplo usa o D1, o banco da própria Cloudflare, e por isso o D1 sai.

O exemplo pede o Python 3.14. A `setup-fde` instala o 3.12, mas o `uv run` baixa o 3.14 sozinho na primeira vez.

### Ligar o servidor ao Supabase como o agente

O servidor não usa a chave secreta do Supabase, que passa por cima de todas as regras. Ele entra como um usuário comum, o `agente`, e o banco só deixa esse usuário ler o caso e gravar propostas.

1. No painel do Supabase, em **Authentication** → **Users**, o líder cria o usuário do agente com **Add user**, com um e-mail do grupo e uma senha forte.
2. Dê a esse usuário o papel `agente`, como manda a arquitetura de referência.
3. Grave os dados de entrada como segredos do Worker, dentro de `servidor-mcp/`. Cada comando pede o valor no terminal:

```bash
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_PUBLISHABLE_KEY
wrangler secret put AGENTE_EMAIL
wrangler secret put AGENTE_SENHA
```

O `SUPABASE_URL` e a chave publicável (`sb_publishable_...`) estão no painel do projeto, em **Project Settings** → **API Keys**.

Para testar na sua máquina, os mesmos quatro valores vão no arquivo `servidor-mcp/.dev.vars`, um por linha (`NOME=valor`). Esse arquivo não entra no git.

### Testar na sua máquina

Dentro de `servidor-mcp/`:

```bash
uv run pywrangler dev
```

O servidor sobe em `http://localhost:8787/mcp`.

### Publicar

A cada mudança:

```bash
uv run pywrangler deploy
```

O `pywrangler` usa o `wrangler` que a `setup-fde` já instalou, e a conta em que você entrou com o `wrangler login`. O servidor fica em:

```
https://ja-chegou-mcp.<subdominio-do-grupo>.workers.dev/mcp
```

Qualquer integrante convidado na conta da Cloudflare publica de novo do mesmo jeito.

### Proteger com um token

O exemplo não confere quem chama. Peça ao Claude Code para o servidor recusar a chamada sem o cabeçalho `Authorization: Bearer <token>` e grave o token como segredo do Worker, dentro de `servidor-mcp/`:

```bash
wrangler secret put MCP_TOKEN
```

Ele pede o valor no terminal. Gere um token longo e guarde no gerenciador de senhas do grupo.

### Cada um liga o Claude Code

Primeiro, ponha o token numa variável do terminal, sem que ele apareça na tela (cole e aperte Enter):

```bash
read -rs MCP_TOKEN
```

Depois:

```bash
claude mcp add --transport http ja-chegou \
  https://ja-chegou-mcp.<subdominio-do-grupo>.workers.dev/mcp \
  --header "Authorization: Bearer $MCP_TOKEN"
```

Abra o Claude Code e rode `/mcp`: o servidor `ja-chegou` precisa aparecer conectado.

No plano gratuito, cada chamada tem 10 ms de CPU e o dia tem 100 mil chamadas ([limites](https://developers.cloudflare.com/workers/platform/pricing/)). Se uma chamada passar dos 10 ms, a Cloudflare corta e devolve o **erro 1102**. O tempo de CPU de cada chamada aparece no painel do Worker, em **Metrics**: se o 1102 aparecer, mostre esse número ao Claude Code para enxugar a tool.

## O que nunca entra no fork

O fork é público. Nada disto entra em commit, no código ou em arquivo versionado:

- a senha do banco do Supabase;
- as chaves do projeto Supabase (a chave secreta e a `service_role`);
- os tokens de API da Cloudflare;
- o `MCP_TOKEN` do servidor MCP e a senha do usuário `agente`.

Elas ficam no seu gerenciador de senhas, nos secrets do Worker (`wrangler secret put`), nos secrets do repositório ou nos arquivos locais `.env` e `.dev.vars`, que não entram no git.

## Registre na pasta do grupo

No `README.md` da pasta do grupo, em `teams/`, o líder preenche o campo **Contas** com o nome da organização no Supabase e o nome da conta na Cloudflare. Só os nomes, nunca as chaves.
