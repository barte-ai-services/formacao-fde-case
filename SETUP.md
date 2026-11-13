# Setup: preparar a sua máquina para a Formação FDE

Este guia é para quem não programa no dia a dia. Siga na ordem, copiando e colando os comandos. Reserve uns 30 a 45 minutos e faça **até quinta-feira, 12/11**, para chegar na sexta com tudo funcionando.

Você vai instalar:

1. **Git**: o programa que guarda o histórico dos arquivos e conversa com o GitHub.
2. **Conta no GitHub**: onde fica o seu fork deste repositório.
3. **GitHub CLI (`gh`)**: o programa que faz o login do Git na sua conta do GitHub, para você conseguir enviar (`git push`) o seu trabalho.
4. **Claude Code**: o assistente de código que vamos usar na imersão.
5. **uv e Python 3.12**: o uv instala o Python e as bibliotecas do projeto.

No fim, você roda um verificador que diz o que está pronto e o que falta.

> **Qual é o seu sistema?**
> - **macOS:** siga as partes marcadas *macOS*.
> - **Windows:** o caminho que damos suporte é o **WSL 2 com Ubuntu** (um Linux que roda dentro do Windows). Comece pela seção [Windows (WSL 2)](#windows-wsl-2) e depois siga as partes marcadas *Windows (Ubuntu no WSL)*. Todos os comandos são digitados **dentro do terminal do Ubuntu**, não no PowerShell.
> - **Linux:** siga as partes marcadas *Windows (Ubuntu no WSL)*; os comandos são os mesmos no Ubuntu e no Debian.

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

O agente de domingo não precisa de chave da API: ele roda dentro do Claude Code, com o login da sua conta. O `.env` fica para alguma credencial que o seu grupo precise guardar. **Nunca** coloque o `.env` num commit: ele já está no `.gitignore`.

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
