# Os acessos que só a pessoa dá

O que o `setup-fde.sh` mostra como `manual`, com os valores de cada um. Todo comando aqui é rodado pela pessoa, no terminal dela.

## Identidade do git

```sh
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

Use o mesmo e-mail da conta do GitHub, para que cada commit apareça com o nome da pessoa.

## Login do GitHub

```sh
gh auth login
```

Responda assim: **GitHub.com**, **HTTPS** e **Login with a web browser**. Ele mostra um código; a pessoa copia, aperta Enter, cola o código na página que abrir e autoriza. As permissões padrão bastam para o case.

Depois, deixe o git usar esse login, para o `git push` funcionar:

```sh
gh auth setup-git
```

Confira com `gh auth status`.

Quem ainda não tem conta cria uma em https://github.com/signup antes.

## O fork e o clone

Cada pessoa trabalha no próprio fork. Com o `gh` logado, um comando faz o fork e o clone, e já deixa o `origin` apontando para o fork e o `upstream` para o original:

```sh
gh repo fork barte-ai-services/formacao-fde-case --clone
cd formacao-fde-case
```

Quem clonou o original em vez do fork conserta de dentro da pasta, sem clonar de novo:

```sh
gh repo fork --remote
```

O original vira `upstream` e o fork vira `origin`.

Quem tem o fork clonado mas não tem o `upstream` recebe ele do `fix`. Se o `upstream` aponta para outro lugar:

```sh
git remote set-url upstream https://github.com/barte-ai-services/formacao-fde-case.git
```

## Conta do Claude Code

```sh
claude
```

Na primeira vez ele pede para entrar com a conta e abre o navegador. Os organizadores passam as orientações sobre a conta e o acesso a usar na imersão. Nenhuma chave entra no repositório nem na conversa.

## Windows

Tudo roda dentro do WSL 2, e o Windows em si só recebe o WSL. No PowerShell, como administrador:

```powershell
wsl --install -d Ubuntu
```

Reinicie quando ele pedir, abra o **Ubuntu** pelo menu Iniciar e crie o usuário e a senha do Linux. Dali em diante, tudo acontece no terminal do Ubuntu: o Claude Code, o clone do case e esta skill, que vê um Ubuntu como outro qualquer. Guarde o case na pasta do Ubuntu (por exemplo, `~/formacao-fde-case`), não em `C:\`.
