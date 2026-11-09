# O caso: Já Chegou

Esta pasta guarda o material do cliente do fim de semana, a **Já Chegou**.

| Arquivo | O que tem | Quando ler |
| --- | --- | --- |
| [`briefing.md`](briefing.md) | O briefing do cliente antes do evento: quem é, o que está em jogo, como se preparar para a primeira reunião. | Antes de sábado. |
| Dossiê (pasta proposta: `case/dossier/`) | O dossiê do caso: tudo o que cinco a sete horas de conversa com o cliente teriam rendido, com os números. | **Ainda não existe.** Chega no sábado, 14/11, às 10h30. |

## O dossiê ainda não está aqui

O dossiê **não** está neste repositório agora, e isso é de propósito. Na consultoria de verdade
você não recebe os números antes de conversar com o cliente: primeiro vem a reunião, depois
os dados.

- **Quando:** sábado, **14/11, às 10h30**, logo depois do roleplay da primeira reunião com o cliente.
- **Como:** como um **commit no repositório original** (o `upstream`, de onde você fez o fork).
- **Onde vai aparecer:** a pasta proposta é `case/dossier/`. A coordenação confirma o lugar exato
  quando o dossiê for liberado.

O seu fork **não** recebe esse commit sozinho. Você precisa sincronizar o fork com o repositório
original. Isso também é um exercício de Git: faça com calma e confira o resultado.

## Como sincronizar o seu fork

Escolha **um** dos dois caminhos. O resultado é o mesmo: a `main` do seu fork passa a ter também
o que chegou no repositório original, incluindo o dossiê.

### Pelo site do GitHub

1. Abra o **seu fork** no GitHub (`https://github.com/<seu-usuario>/formacao-fde-case`).
2. Logo acima da lista de arquivos, clique em **Sync fork**.
3. Clique em **Update branch**.
4. Confira: a pasta do dossiê aparece na lista de arquivos do seu fork.
5. Se você trabalha num clone no seu computador, traga a atualização para ele:

   ```bash
   git switch main
   git pull origin main
   ```

> Se o GitHub avisar que há conflito ou oferecer descartar commits (*Discard commits*), não clique:
> chame um coach. No fork do líder isso pode acontecer porque a `main` já tem o trabalho do grupo.

### Pelo terminal

Rode no clone do seu fork, no seu computador.

1. Diga ao Git onde está o repositório original. Isso só precisa ser feito **uma vez**:

   ```bash
   git remote add upstream https://github.com/barte-ai-services/formacao-fde-case.git
   ```

   (Use a URL do repositório original. Para conferir os remotos configurados: `git remote -v`.
   Você deve ver `origin`, o seu fork, e `upstream`, o original.)

2. Baixe o que há de novo no repositório original:

   ```bash
   git fetch upstream
   ```

3. Vá para a sua `main`:

   ```bash
   git switch main
   ```

4. Junte a `main` do original com a sua:

   ```bash
   git merge upstream/main
   ```

5. Envie o resultado para o seu fork no GitHub:

   ```bash
   git push origin main
   ```

6. Confira:

   ```bash
   git log --oneline -5
   ```

   O commit do dossiê deve aparecer no `git log`, e a pasta dele, na lista de arquivos (`ls case/`).

## E o fork do líder do grupo?

Cada grupo integra o trabalho por pull requests no **fork do líder**. Por isso:

1. **O líder sincroniza primeiro.** O líder segue um dos caminhos acima no fork dele. A partir
   daí, o dossiê está no fork do líder, que é onde o grupo integra.
2. **Cada membro atualiza o próprio fork.** Cada membro sincroniza o seu fork com o original
   (mesmos passos acima), para ter o dossiê também.
3. **Cada membro traz o trabalho do grupo.** Para que os seus pull requests partam do estado
   atual do grupo, adicione o fork do líder como remoto (só uma vez) e atualize a sua `main`:

   ```bash
   git remote add leader https://github.com/<usuario-do-lider>/formacao-fde-case.git
   git fetch leader
   git switch main
   git merge leader/main
   git push origin main
   ```

4. **Trabalhe numa branch e abra o pull request no fork do líder.** Crie uma branch a partir da
   `main` atualizada (`git switch -c <nome-da-branch>`), faça seus commits, envie para o seu fork
   (`git push origin <nome-da-branch>`) e abra o pull request com destino à `main` do fork do líder.

Se `git merge` parar com conflito, não force nada: leia a mensagem, chame o grupo e, se precisar,
um coach.
