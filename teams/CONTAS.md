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

Quem tem acesso a mais de uma conta na Cloudflare (a pessoal e a do grupo) escolhe a do grupo no primeiro `wrangler deploy`, quando ele perguntar, ou fixa o `account_id` da conta do grupo no `wrangler.toml` do projeto.

## O que nunca entra no fork

O fork é público. Nada disto entra em commit, no código ou em arquivo versionado:

- a senha do banco do Supabase;
- as chaves do projeto Supabase (a chave secreta e a `service_role`);
- os tokens de API da Cloudflare.

Elas ficam no seu gerenciador de senhas, nos secrets do Worker (`wrangler secret put`), nos secrets do repositório ou nos arquivos locais `.env` e `.dev.vars`, que não entram no git.

## Registre na pasta do grupo

No `README.md` da pasta do grupo, em `teams/`, o líder preenche o campo **Contas** com o nome da organização no Supabase e o nome da conta na Cloudflare. Só os nomes, nunca as chaves.
