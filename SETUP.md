# Setup: preparar a sua máquina para a Formação FDE

Este guia é para quem não programa no dia a dia. Há dois caminhos: o **caminho principal**, em que o Claude Code configura a máquina com você, e o [passo a passo à mão](#passo-a-passo-à-mão), para quem prefere fazer cada instalação sozinho ou ficou travado no caminho principal. Os dois chegam ao mesmo lugar.

> **Qual é o seu sistema?**
> - **macOS:** siga as partes marcadas *macOS*.
> - **Windows:** o caminho que damos suporte é o **WSL 2 com Ubuntu** (um Linux que roda dentro do Windows). Comece pela seção [Windows (WSL 2)](#windows-wsl-2) e depois siga as partes marcadas *Windows (Ubuntu no WSL)*. Todos os comandos são digitados **dentro do terminal do Ubuntu**, não no PowerShell.
> - **Linux:** siga as partes marcadas *Windows (Ubuntu no WSL)*; os comandos são os mesmos no Ubuntu e no Debian.

## Caminho principal: o Claude Code configura a máquina com você

O repositório traz uma skill do Claude Code, a `setup-fde` (em `.claude/skills/setup-fde/`). Ela confere a máquina, instala o que falta (Git, GitHub CLI, Node.js, uv, Python 3.12, Docker, Supabase CLI e Wrangler), deixa o seu fork com `origin` e `upstream` certos, prepara o projeto e roda o verificador. O que só você pode fazer, como entrar na sua conta do GitHub, do Supabase e da Cloudflare, ela explica e espera você fazer: ela nunca pede senha, token ou chave na conversa.

1. **Instale o Claude Code.** Abra o terminal (veja [Como abrir o terminal](#como-abrir-o-terminal); no Windows, primeiro a seção [Windows (WSL 2)](#windows-wsl-2)) e rode:

   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

   O comando precisa do `curl`, que já vem no macOS e no Ubuntu. Se o Ubuntu disser que ele não existe, rode antes `sudo apt update && sudo apt install -y curl`. Feche e abra o terminal de novo.

2. **Entre com a sua conta.** Rode `claude` e siga as instruções na tela. Os organizadores vão passar as orientações sobre a conta e o acesso a usar na imersão.

3. **Peça o setup.** Com o Claude Code aberto na pasta do case, peça:

   ```
   configura o meu setup de FDE
   ```

   Ele mostra o que está pronto e o que falta, instala o que dá e diz, passo a passo, o que você precisa fazer. Se algo pedir a senha do computador, ele passa o comando para você rodar no seu terminal.

**Ainda não tem o case na sua máquina?** A skill mora dentro do repositório, então ela só aparece numa sessão do Claude Code aberta na pasta `formacao-fde-case`. Quem ainda não tem essa pasta tem dois jeitos de começar:

- abra o terminal, rode `cd ~` e depois `claude`, e peça: "instala o git e o GitHub CLI e clona o meu fork do barte-ai-services/formacao-fde-case". Se ele pedir a senha do computador ou para entrar no GitHub, rode você mesmo o comando que ele mostrar, no seu terminal. No fim, ele roda `gh repo fork barte-ai-services/formacao-fde-case --clone`, que cria a pasta `~/formacao-fde-case`; ou
- siga o [passo a passo à mão](#passo-a-passo-à-mão) até o clone (seções Git, Conta no GitHub e GitHub CLI, e o passo a passo do fork no [README.md](README.md#passo-a-passo-fazer-o-fork-e-clonar)).

Depois, feche o Claude Code, rode `cd ~/formacao-fde-case` e abra uma sessão nova com `claude`. Nela, peça de novo "configura o meu setup de FDE".

## O Ahrena no Claude Code

O **Ahrena** é um conjunto de plugins do Claude Code que a Barte usa para trabalhar com agentes. Ele traz um time de agentes, cada um com um papel: a **Athena** recebe um pedido de construção, planeja e distribui o trabalho; outros agentes constroem; o **Argos** revisa antes de qualquer coisa entrar. O case já vem configurado para usar o Ahrena (no arquivo `.claude/settings.json`), mas cada máquina precisa instalar os plugins uma vez.

**Como instalar.** A skill `setup-fde` instala: quando você pede "configura o meu setup de FDE", ela instala os plugins do Ahrena junto com o resto. No Ubuntu 22.04 (e no WSL com ele), ela antes atualiza o git, porque o que vem com o sistema é velho demais para instalar os plugins; isso pede a senha do computador, e ela passa o comando para você rodar no seu terminal. Depois, feche o Claude Code e abra de novo na pasta do case.

**Como confirmar que ele está ativo.** Dentro do Claude Code, na pasta do case, digite `/agents`. Na lista tem que aparecer a `athena` (às vezes com o nome completo, `ahrena-engineering-development:athena`). A skill `setup-fde` também confere: o item `ahrena` fica `ok` quando os plugins estão instalados, e diz quais faltam quando não estão.

## Passo a passo à mão

Se preferir fazer sozinho, siga na ordem, copiando e colando os comandos. Reserve uns 45 a 60 minutos.

Você vai instalar:

1. **Git**: o programa que guarda o histórico dos arquivos e conversa com o GitHub.
2. **Conta no GitHub**: onde fica o seu fork deste repositório.
3. **GitHub CLI (`gh`)**: o programa que faz o login do Git na sua conta do GitHub, para você conseguir enviar (`git push`) o seu trabalho.
4. **Claude Code**: o assistente de código que vamos usar na imersão.
5. **uv e Python 3.12**: o uv instala o Python e as bibliotecas do projeto.
6. **Node.js e npm**: o Node.js roda programas escritos em JavaScript, e o npm instala esses programas. O Wrangler é um deles.
7. **Docker**: roda programas dentro de "caixas" isoladas, chamadas contêineres. O Supabase usa o Docker para subir um banco de dados de teste no seu computador.
8. **Supabase CLI e conta no Supabase**: o Supabase guarda os dados e o login dos usuários do que você publica.
9. **Wrangler e conta na Cloudflare**: o Wrangler publica o seu projeto na Cloudflare, que entrega ele na internet.

No fim, você roda um verificador que diz o que está pronto e o que falta.

## Como abrir o terminal

- **macOS:** aperte `Cmd + Espaço`, digite **Terminal** e aperte Enter.
- **Windows:** depois de instalar o WSL (seção abaixo), abra o menu Iniciar, digite **Ubuntu** e aperte Enter.

Para rodar um comando, copie a linha, cole no terminal e aperte Enter. Se ele pedir uma senha, é a senha do seu computador (no macOS) ou a que você criou para o Ubuntu (no Windows). Enquanto você digita a senha nada aparece na tela; isso é normal.

## Windows (WSL 2)

*Só para Windows. No macOS, pule para [Git](#git).*

1. Abra o menu Iniciar, digite **PowerShell**, clique com o botão direito e escolha **Executar como administrador**.
2. Rode:

   ```powershell
   wsl --install -d Ubuntu
   ```

3. Reinicie o computador quando ele pedir.
4. Abra o **Ubuntu** pelo menu Iniciar. Na primeira vez ele pede um nome de usuário e uma senha para o Linux: escolha e guarde.
5. Dentro do Ubuntu, atualize o sistema e instale o básico:

   ```bash
   sudo apt update && sudo apt install -y git curl
   ```

A partir daqui, tudo é feito **dentro do Ubuntu**. Guarde os seus arquivos do curso na pasta do Ubuntu (por exemplo, em `~/formacao-fde-case`), não em `C:\`.

## Git

**macOS:** rode o comando abaixo e clique em **Instalar** na janela que aparecer (ela instala as ferramentas de linha de comando da Apple, que trazem o Git):

```bash
xcode-select --install
```

Se aparecer uma mensagem dizendo que já está instalado, ótimo: siga em frente.

**Windows (Ubuntu no WSL):** o Git já foi instalado na seção anterior. Se pulou essa parte, rode `sudo apt update && sudo apt install -y git`.

Depois, nos dois sistemas, diga ao Git o seu nome e e-mail (use o mesmo e-mail da conta do GitHub):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

Confira: `git --version` deve mostrar algo como `git version 2.x`.

## Conta no GitHub

1. Se ainda não tem, crie uma conta em [github.com/signup](https://github.com/signup).
2. Guarde o seu nome de usuário: ele aparece no link do seu fork (`https://github.com/<seu-usuario>/formacao-fde-case`).

## GitHub CLI

O GitHub CLI (`gh`) é **obrigatório**. É com ele que o Git entra na sua conta do GitHub: sem ele, o `git push` do seu fork não funciona.

**macOS**, de um destes dois jeitos:

- Se você tem o [Homebrew](https://brew.sh): `brew install gh`
- Se não tem o Homebrew: baixe o instalador `.pkg` para macOS em [cli.github.com](https://cli.github.com), abra o arquivo e siga as telas.

**Windows (Ubuntu no WSL):** `sudo apt install -y gh`

Feche e abra o terminal de novo e confira com `gh --version`.

Depois, entre na sua conta:

```bash
gh auth login
```

Responda às perguntas assim: **GitHub.com**, **HTTPS** e login pelo navegador (**Login with a web browser**). Ele mostra um código; copie, aperte Enter, cole o código na página que abrir e autorize.

Por fim, deixe o Git usar esse login:

```bash
gh auth setup-git
```

Confira com `gh auth status`: deve aparecer que você está logado em `github.com`.

## Claude Code

O Claude Code é o assistente de código que roda no terminal.

**macOS e Windows (Ubuntu no WSL):**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Feche e abra o terminal de novo, e confira com `claude --version`. Se o comando de instalação mudar, siga a página oficial de instalação do Claude Code.

Para entrar com a sua conta, rode `claude` e siga as instruções na tela. Os organizadores vão passar as orientações sobre a conta e o acesso a usar na imersão.

## uv e Python 3.12

O **uv** instala o Python certo e as bibliotecas do projeto, sem mexer no Python que já vem no seu computador.

**macOS e Windows (Ubuntu no WSL):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Feche e abra o terminal de novo e confira com `uv --version`. (No macOS, quem usa Homebrew também pode instalar com `brew install uv`.)

Agora instale o Python 3.12 pelo uv:

```bash
uv python install 3.12
```

## Node.js e npm

O **Node.js** roda programas em JavaScript; o **npm** vem junto com ele e instala esses programas. Precisamos da versão 22 ou mais nova.

**macOS** (com o [Homebrew](https://brew.sh)):

```bash
brew install node
```

**Windows (Ubuntu no WSL):** o Node.js que vem no Ubuntu é velho demais, então ele vem do repositório da NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs
```

Confira com `node --version` (deve começar com `v22` ou mais) e `npm --version`.

## Docker

O **Docker** roda programas dentro de contêineres, caixas isoladas que não bagunçam o resto do computador. Não usamos o Docker Desktop: no Mac, o motor é o **Colima**; no Ubuntu, o **Docker Engine**. Os dois são gratuitos e não pedem conta.

**macOS:**

```bash
brew install docker colima
colima start
```

O `colima start` liga o motor. Depois de reiniciar o Mac, rode `colima start` de novo antes de usar o Docker.

**Windows (Ubuntu no WSL):**

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

O segundo comando deixa você usar o Docker sem `sudo`. Ele só vale num terminal novo: no Ubuntu do WSL, abra o PowerShell, rode `wsl --shutdown` e abra o Ubuntu de novo. No Ubuntu fora do WSL, saia da sua sessão e entre de novo.

Se o Docker disser que não consegue falar com o motor (`Cannot connect to the Docker daemon`), ligue o serviço:

```bash
sudo systemctl start docker
```

Confira com `docker info`: ele deve mostrar os detalhes do motor, sem erro.

## Supabase CLI e conta no Supabase

O **Supabase** guarda os dados e o login dos usuários do que você publica. O **Supabase CLI** é o programa que conversa com ele pelo terminal.

1. Se ainda não tem, crie uma conta em [supabase.com](https://supabase.com/dashboard/sign-up). Dá para entrar com a sua conta do GitHub.
2. Instale o CLI.

   **macOS:**

   ```bash
   brew install supabase/tap/supabase
   ```

   **Windows (Ubuntu no WSL):** o CLI não se instala pelo npm. Baixe o programa pronto para a sua pasta pessoal:

   ```bash
   mkdir -p ~/.local/bin
   curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_$(dpkg --print-architecture).tar.gz | tar -xz -C ~/.local/bin supabase
   ```

   Feche e abra o terminal de novo e confira com `supabase --version`.

3. Entre na sua conta:

   ```bash
   supabase login
   ```

   Ele abre o navegador (ou mostra um link para você abrir). Entre com a sua conta do Supabase e autorize. Se ele mostrar um código de verificação no navegador, copie e cole no terminal. Confira com `supabase projects list`: deve aparecer a lista dos seus projetos, mesmo que vazia.

## Wrangler e conta na Cloudflare

A **Cloudflare** entrega o que você publica na internet. O **Wrangler** é o programa que publica, pelo terminal. Ele vem pelo npm, então instale o Node.js antes.

1. Se ainda não tem, crie uma conta gratuita em [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up).
2. Instale o Wrangler, na sua pasta pessoal (assim ele não pede a senha do computador):

   ```bash
   npm install -g --prefix ~/.local wrangler
   ```

   Feche e abra o terminal de novo e confira com `wrangler --version`. Se o terminal disser que `wrangler` não existe, rode `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc` (no Mac, `~/.zshrc` no lugar de `~/.bashrc`) e abra o terminal de novo.

3. Entre na sua conta:

   ```bash
   wrangler login
   ```

   Ele abre o navegador numa página da Cloudflare. Entre com a sua conta e clique em **Allow** para autorizar o Wrangler. Confira com `wrangler whoami`: deve aparecer o seu e-mail.

   No Ubuntu do WSL, se o navegador não abrir sozinho, copie o link que aparece no terminal e abra no navegador do Windows.

## Preparar o projeto

Com o seu fork já clonado (veja o passo a passo no [README.md](README.md#passo-a-passo-fazer-o-fork-e-clonar)), entre na pasta do projeto e instale as dependências:

```bash
cd formacao-fde-case
uv sync
```

Depois, crie o seu arquivo de configuração local a partir do exemplo:

```bash
cp .env.example .env
```

O kit de domingo não precisa de credencial nenhuma: ele roda inteiro dentro do Claude Code, e o único requisito é o seu Claude Code. O `.env` fica para alguma credencial que o seu grupo precise guardar. **Nunca** coloque o `.env` num commit: ele já está no `.gitignore`.

Para conferir que o projeto está de pé, rode os testes:

```bash
uv run pytest
```

## Conferir a instalação

Dentro da pasta do projeto, rode:

```bash
python3 scripts/check_setup.py
```

Ele mostra uma linha por item:

- `[OK]`: está tudo certo com esse item.
- `[FALTA]`: falta instalar; a própria linha diz o que fazer e qual seção deste guia seguir.
- `[AVISO]`: não impede de seguir, mas vale conferir (por exemplo, o aviso de usar o WSL no Windows).

No fim aparece o veredito: **Tudo pronto** ou quantos itens obrigatórios faltam. Corrija o que faltar e rode de novo até aparecer **Tudo pronto**.

Se o terminal disser que `python3` não existe, rode o verificador pelo uv: `uv run python scripts/check_setup.py`.

## Se algo der errado

- Feche e abra o terminal depois de cada instalação: muitos programas só aparecem num terminal novo.
- Copie a mensagem de erro inteira e mande para os organizadores, junto com a saída do `python3 scripts/check_setup.py`.
