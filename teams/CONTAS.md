# Contas do grupo no Supabase e na Cloudflare

O grupo constrói com o Supabase (banco e autenticação) e publica com a Cloudflare (Workers). Quem cria as duas contas é o **líder do grupo**, o dono do fork líder. Depois ele convida os integrantes, e todo mundo trabalha nas mesmas contas.

As duas contas são gratuitas. Ninguém precisa de cartão de crédito.

## Já tem conta? Crie uma segunda só para a formação

Se você já usa o Supabase ou a Cloudflare no trabalho, não misture. Crie uma conta nova com o seu e-mail mais um `+formacao-fde` antes do `@`:

```
seu.email+formacao-fde@dominio.com
```

Os e-mails chegam na sua caixa de sempre, mas os serviços enxergam um endereço novo. O Gmail e o Google Workspace aceitam o `+`. Outros provedores podem não aceitar: se o e-mail de confirmação não chegar, use outro endereço.

## Supabase: o líder cria

1. Entre em [supabase.com](https://supabase.com), clique em **Start your project** e crie a conta (com o GitHub ou com e-mail).
2. Crie uma **organização** no plano **Free**, com o nome do grupo (por exemplo, `formacao-fde-grupo-1`).
3. Dentro dela, clique em **New project**:
   - **Name:** o nome do grupo;
   - **Database password:** gere uma senha forte e guarde num gerenciador de senhas. Ela não vai para o repositório;
   - **Region:** South America (São Paulo).
4. Espere o projeto ficar pronto.

No plano gratuito, um projeto parado por muitos dias é pausado. Se isso acontecer, é só reativar no painel.

### Supabase: convidar o grupo

1. Na organização, abra **Settings** → **Team**.
2. Clique em **Invite member**, informe o e-mail de cada integrante e escolha o papel **Developer**.
3. Cada integrante aceita o convite pelo e-mail.

Depois, cada um liga a própria máquina ao projeto:

```bash
npx supabase login
npx supabase link --project-ref <ref-do-projeto>
```

O `ref` do projeto aparece no endereço do painel: `supabase.com/dashboard/project/<ref>`.

## Cloudflare: o líder cria

1. Entre em [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up), crie a conta e confirme o e-mail.
2. No painel, abra **Workers & Pages** uma vez, para ativar os Workers no plano gratuito.
3. Se o painel pedir um subdomínio `workers.dev`, use o nome do grupo.

### Cloudflare: convidar o grupo

1. No painel da conta, abra **Manage Account** → **Members**.
2. Clique em **Invite**, informe o e-mail de cada integrante e escolha um papel que permita publicar Workers (por exemplo, **Administrator**).
3. Cada integrante aceita o convite pelo e-mail.

Depois, cada um entra pelo terminal:

```bash
npx wrangler login
```

Quem tem mais de uma conta na Cloudflare (a pessoal e a do grupo) escolhe a do grupo quando o Wrangler perguntar.

## O que nunca entra no fork

O fork é público. Nada disto entra em commit, no código ou em arquivo versionado:

- a senha do banco do Supabase;
- as chaves do projeto Supabase (a chave secreta e a `service_role`);
- os tokens de API da Cloudflare.

Elas ficam no seu gerenciador de senhas, nos secrets do Worker (`npx wrangler secret put`), nos secrets do repositório ou no `.env`, que não entra no git.

## Registre na pasta do grupo

No `README.md` da pasta do grupo, em `teams/`, o líder preenche o campo **Contas** com o nome da organização no Supabase e o nome da conta na Cloudflare. Só os nomes, nunca as chaves.
