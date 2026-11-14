# Contas do grupo no Supabase, na Cloudflare e no FastMCP Gateway

O grupo constrói com o Supabase (banco e autenticação) e publica com a Cloudflare (Workers). O servidor MCP do grupo pode ficar na Cloudflare ou no FastMCP Gateway, que hospeda servidores MCP escritos em Python. Quem cria as contas é o **líder do grupo**, o dono do fork líder. Depois ele convida os integrantes, quando o serviço deixa, e todo mundo trabalha nas mesmas contas.

As três contas são gratuitas. O Supabase e a Cloudflare não pedem cartão de crédito.

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

## FastMCP Gateway: o líder cria

O [FastMCP Gateway](https://gofastmcp.com/deployment/prefect-horizon), da Prefect, publica um servidor MCP em Python direto do GitHub e entrega um endereço `https://<nome>.fastmcp.app/mcp` para o Claude Code. Ele se chamava Horizon, e o painel e a documentação ainda usam esse nome no endereço (`horizon.prefect.io`). O antigo FastMCP Cloud virou o Gateway.

O plano gratuito é o **Personal**: um desenvolvedor, até 200 servidores e um dia de logs. Os convites para o grupo só existem no plano pago, então no plano gratuito quem publica é o líder, e o grupo usa o endereço que ele publicar. Os limites estão em [prefect.io/pricing](https://www.prefect.io/pricing?product=horizon).

1. Entre em [horizon.prefect.io/signup](https://horizon.prefect.io/signup) com o GitHub do líder, o mesmo do fork líder. Aqui a regra do e-mail com `+` não vale: o FastMCP Gateway só entra pelo GitHub.
2. Na primeira entrada, crie a **organização** com o nome do grupo (por exemplo, `formacao-fde-grupo-1`).
3. Conecte o GitHub: autorize o app e dê acesso só ao fork líder (**Only select repositories**).

### FastMCP Gateway: preparar o servidor no fork

O Gateway roda servidores do pacote `fastmcp`. No fork líder, o servidor do grupo precisa de:

- **o `fastmcp` nas dependências:** `uv add fastmcp`, que grava no `pyproject.toml` e no `uv.lock`;
- **o import do pacote:** `from fastmcp import FastMCP`;
- **um objeto do servidor num arquivo Python**, por exemplo `mcp = FastMCP("ja-chegou")` em `servidor/main.py`. O `if __name__ == "__main__"` é ignorado.

Antes de publicar, confira na sua máquina:

```bash
uv run fastmcp inspect servidor/main.py:mcp
```

Ele lista as tools. Se der erro aqui, também vai dar erro no Gateway.

### FastMCP Gateway: publicar

1. No painel, escolha o fork líder e preencha:
   - **Server name:** o nome do grupo. Ele vira o endereço `https://<nome>.fastmcp.app/mcp`;
   - **Entrypoint:** o arquivo e o objeto, no formato `servidor/main.py:mcp`;
   - **Authentication:** desligada. Veja abaixo por quê;
   - **Environment variables:** as chaves de que o servidor precisa, como a do Supabase. Elas ficam guardadas no Gateway e não aparecem de novo depois de salvas.
2. Clique em **Deploy Server** e acompanhe o log. Em geral leva menos de um minuto, e o servidor aparece como **Live**.
3. Cada push na branch principal do fork líder publica de novo. Cada pull request ganha uma prévia.

**Por que a autenticação desligada.** Com ela ligada, só quem é da organização chama o servidor, e no plano gratuito a organização tem só o líder. Desligada, quem tem o endereço usa o servidor. Por isso:

- **o endereço é a senha:** passe-o ao grupo pelo gerenciador de senhas ou numa mensagem direta, nunca no fork;
- **o servidor só mexe nos dados fictícios do caso:** nada de dado real, e nenhuma tool devolve uma chave;
- **no fim da imersão,** o líder religa a autenticação ou apaga o servidor.

### FastMCP Gateway: cada um liga o Claude Code

```bash
claude mcp add --transport http ja-chegou https://<nome>.fastmcp.app/mcp
```

Abra o Claude Code e rode `/mcp`: o servidor `ja-chegou` precisa aparecer conectado. O botão **Connect** de cada servidor, no painel, mostra o comando pronto.

## O que nunca entra no fork

O fork é público. Nada disto entra em commit, no código ou em arquivo versionado:

- a senha do banco do Supabase;
- as chaves do projeto Supabase (a chave secreta e a `service_role`);
- os tokens de API da Cloudflare;
- o endereço do servidor no FastMCP Gateway, enquanto a autenticação estiver desligada, e as chaves `fmcp_` do Gateway.

Elas ficam no seu gerenciador de senhas, nos secrets do Worker (`wrangler secret put`), nas variáveis de ambiente do FastMCP Gateway, nos secrets do repositório ou nos arquivos locais `.env` e `.dev.vars`, que não entram no git.

## Registre na pasta do grupo

No `README.md` da pasta do grupo, em `teams/`, o líder preenche o campo **Contas** com o nome da organização no Supabase, o nome da conta na Cloudflare e o nome da organização no FastMCP Gateway. Só os nomes, nunca as chaves nem o endereço do servidor.
