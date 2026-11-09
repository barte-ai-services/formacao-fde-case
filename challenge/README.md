# Desafio do kit: a peça que falta

> Sábado, 14/11, das 9h às 9h40, junto com a aula de Git na prática e a formação dos grupos.

No seu kit há uma **caixa trancada com um jogo de Tetris**. O seu crachá traz **"a peça que
falta"**. A resposta que abre a caixa está escondida **neste repositório**: em algum lugar do
histórico do Git, das branches ou das tags. Ela pode estar codificada.

Para achá-la, você vai usar os mesmos comandos de Git que usa no dia a dia de um projeto. Este
guia ensina esses comandos. Ele **não** diz onde está a pista.

## Antes de tudo: o seu fork precisa ter todas as branches e tags

Um fork que só tem a `main` não tem a pista inteira.

### Ao criar o fork

Na tela **Create a new fork** do GitHub, **desmarque** a opção **Copy the main branch only**.
Assim o seu fork leva todas as branches do repositório original.

### Clone o seu fork

```bash
git clone https://github.com/<seu-usuario>/formacao-fde-case.git
cd formacao-fde-case
git fetch --all --tags
```

### Se você já fez o fork só com a `main`

Não precisa apagar nada. Traga as branches e as tags do repositório original para o seu clone:

```bash
git remote add upstream https://github.com/barte-ai-services/formacao-fde-case.git   # só uma vez
git fetch upstream --tags
```

Depois disso, as branches do original aparecem como `upstream/<nome>` e as tags ficam no seu
clone. Confira com `git branch -a` e `git tag`.

Se já existe um remoto `upstream`, pule o `git remote add` (veja os remotos com `git remote -v`).

## Os comandos que você vai usar

Rode cada um, leia a saída e pergunte-se: **o que aqui parece fora do lugar?**

### 1. Ver o histórico inteiro, de todas as branches

```bash
git log --all --oneline --graph
```

- `--all`: mostra os commits de **todas** as branches e tags, não só da branch atual.
- `--oneline`: um commit por linha (hash curto e mensagem).
- `--graph`: desenha as linhas que mostram de onde cada branch saiu.

Sem `--all`, você só vê o histórico da branch em que está.

### 2. Listar as branches

```bash
git branch -a
```

- Sem `-a`, aparecem só as branches locais.
- Com `-a`, aparecem também as remotas (`remotes/origin/...`, `remotes/upstream/...`).

Para olhar uma branch remota sem trocar de branch: `git log --oneline upstream/<nome>`.

### 3. Listar as tags e as mensagens delas

```bash
git tag -n
```

- `git tag` lista os nomes das tags.
- `git tag -n` mostra também a primeira linha da mensagem de cada tag. Uma tag anotada pode
  ter uma mensagem própria, separada da mensagem do commit para o qual aponta.
- `git tag -n99` mostra até 99 linhas da mensagem.

### 4. Inspecionar qualquer coisa: commit, branch ou tag

```bash
git show <ref>
```

`<ref>` pode ser um hash de commit, o nome de uma branch ou o nome de uma tag. Para uma tag
anotada, `git show` mostra primeiro a tag (quem criou, quando, a mensagem) e depois o commit.

Para ver só a mensagem e a lista de arquivos, sem o diff: `git show --stat <ref>`.

### 5. Ler as mudanças, commit a commit

```bash
git log -p
```

- `-p` mostra o diff de cada commit: o que entrou e o que saiu, linha a linha.
- Junte com `--all` para todas as branches: `git log --all -p`.
- Para um arquivo só: `git log -p -- <caminho-do-arquivo>`.
- Para procurar um texto em todas as mudanças da história: `git log --all -S '<texto>'`.

Um arquivo que foi apagado continua no histórico. O `git log -p` mostra o conteúdo que ele tinha.

### 6. Ler as mensagens de commit com atenção

```bash
git log --all --format='%h %ad %an%n%B' --date=short
```

Mostra hash, data, autor e a mensagem **completa** de cada commit (`%B`), não só a primeira
linha. Mensagens de commit também guardam informação.

## Se o que você achar parecer embaralhado

Texto que parece aleatório pode estar **codificado**: formatos comuns incluem base64,
hexadecimal e outros. Alguns exemplos de como decodificar no terminal:

- base64:

  ```bash
  echo '<texto-codificado>' | base64 -d
  ```

- hexadecimal:

  ```bash
  echo '<texto-codificado>' | xxd -r -p
  ```

- em Python, trocando a função pela do formato que você suspeita:

  ```bash
  python3 -c "import binascii; print(binascii.unhexlify('<texto-codificado>').decode())"
  ```

Se a saída ainda parecer embaralhada, pense no que mais poderia ter sido feito com o texto.

## Regras

- Vale tudo o que o Git mostra. Não vale abrir a caixa à força.
- Achou? Guarde a resposta com o grupo e abra a caixa.
- Travou? Releia este guia de cima para baixo e rode os comandos de novo com `--all`.

<!-- organizers: the real clue is planted upstream by the instructors; this file holds no secret. <<KIT_SECRET_PLACEHOLDER>> -->
