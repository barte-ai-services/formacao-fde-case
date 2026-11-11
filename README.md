# Formação FDE: repositório do case

Este é o repositório do case da **Formação FDE**, a imersão presencial da Barte na Casa Barte, em São Paulo, de **13 a 15 de novembro de 2026**.

É aqui que vocês vão trabalhar durante o fim de semana: o desafio do kit, o dossiê do cliente **Já Chegou**, os dados, os modelos dos entregáveis e o ponto de partida do agente que cada grupo constrói no domingo. O material chega aos poucos, no ritmo da imersão (veja [O que chega quando](#o-que-chega-quando)).

A solução de referência dos instrutores não faz parte deste repositório.

## Antes de tudo: prepare a sua máquina

Siga o [SETUP.md](SETUP.md). Ele explica, passo a passo, como instalar o Git, criar a conta no GitHub, instalar e conectar o GitHub CLI (`gh`), instalar o Claude Code, o uv e o Python 3.12, no macOS ou no Windows (com WSL 2).

No fim, rode o verificador, que diz o que está pronto e o que falta:

```bash
python3 scripts/check_setup.py
```

## Como o trabalho se organiza: fork individual e fork líder

- **Cada aluno tem o seu fork.** Um fork é a sua cópia deste repositório na sua conta do GitHub. Faça o seu até **quinta-feira, 12/11**.
- **Cada grupo escolhe um fork líder.** É o fork de uma pessoa do grupo, onde o trabalho do grupo se junta.
- **Os integrantes entregam por pull request no fork líder.** Cada pessoa trabalha no próprio fork e abre um pull request (PR) para o fork líder do grupo.
- **O Fernando acompanha os forks.** É assim que os instrutores veem o andamento de cada grupo.
- **A Barte Forge não é necessária.** Ela só aparece como referência na aula de Agent Engineering.

### Passo a passo: fazer o fork e clonar

1. Entre na página deste repositório no GitHub, já logado na sua conta.
2. Clique em **Fork** (canto superior direito) e depois em **Create fork**. O GitHub cria `https://github.com/<seu-usuario>/formacao-fde-case`.
3. No terminal, clone o **seu** fork e entre na pasta:

   ```bash
   git clone https://github.com/<seu-usuario>/formacao-fde-case.git
   cd formacao-fde-case
   ```

4. Registre o repositório original como `upstream`, para receber o que for publicado depois (como o dossiê de sábado):

   ```bash
   git remote add upstream https://github.com/barte-ai-services/formacao-fde-case.git
   ```

5. Prepare o projeto e confira a máquina (detalhes no [SETUP.md](SETUP.md)):

   ```bash
   uv sync
   cp .env.example .env
   python3 scripts/check_setup.py
   ```

### Como receber o que chega depois no repositório original

Quando algo novo for publicado aqui (por exemplo, o dossiê no sábado), atualize o seu fork de um destes dois jeitos:

- **Pelo GitHub:** na página do seu fork, clique em **Sync fork** e depois em **Update branch**. Em seguida, no terminal, rode `git pull`.
- **Pelo terminal:**

  ```bash
  git fetch upstream
  git merge upstream/main
  git push
  ```

### Como funciona o PR do grupo

1. Combinem no grupo de quem é o **fork líder** e anotem o link na pasta do grupo em [`teams/`](teams/README.md).
2. Cada integrante trabalha numa branch do próprio fork:

   ```bash
   git switch -c my-change
   # ...edite os arquivos, depois:
   git add .
   git commit -m "Add diagnosis draft"   # mensagem curta dizendo o que mudou
   git push -u origin my-change
   ```

3. No GitHub, abra o pull request escolhendo como destino o **fork líder** (em *base repository*, escolha `<usuario-do-lider>/formacao-fde-case`, branch `main`).
4. A descrição do PR já vem com um roteiro: o que mudou, a que entregável ou checkpoint se refere, como foi testado e um checklist de segurança. O modelo está em [`.github/pull_request_template.md`](.github/pull_request_template.md).
5. Quem é dono do fork líder revisa e faz o merge. Depois, os outros integrantes trazem o que entrou no fork líder:

   ```bash
   git remote add leader https://github.com/<usuario-do-lider>/formacao-fde-case.git   # só na primeira vez
   git fetch leader
   git merge leader/main
   ```

Nunca coloque o arquivo `.env` nem nenhuma chave ou senha num commit. O `.env` já está no `.gitignore`.

**Atenção: este repositório é público, e o seu fork também é.** Qualquer pessoa na internet pode ver o que você coloca nele, inclusive o histórico de commits. Nunca faça commit de segredos (o `.env`, chaves de API, senhas, tokens).

## O que chega quando

| Quando | O que acontece |
|---|---|
| Quarta, 11/11 | Vocês recebem o link deste repositório. |
| Quinta, 12/11 | Prazo para cada aluno fazer o seu fork e rodar o setup ([SETUP.md](SETUP.md) e `python3 scripts/check_setup.py`). |
| Sexta, 13/11, 18h–21h | Abertura da imersão na Casa Barte. |
| Sábado, 14/11, 9h | Git em prática e formação dos grupos, junto com o **desafio do kit** (pasta `challenge/`). |
| Sábado, 14/11, 9h40 | Roleplay: primeira reunião com o CFO, a controladoria e compras da Já Chegou. |
| Sábado, 14/11, 10h30 | O **dossiê** chega como um commit no repositório original (a pasta exata será indicada pela coordenação; a proposta é `case/dossier/`). Atualize o seu fork para recebê-lo. |
| Sábado, 14/11, 12h | **Checkpoint 1**: diagnóstico e prioridade (o problema, o número a mover, a prioridade). |
| Sábado, 14/11, 15h–18h | Solution Design e aplicação no caso (a aplicação vai das 16h15 às 17h30, depois do café da tarde), fechando com o **checkpoint 2**: checklist de acessos e credenciais, desenho da solução, plano de entrega e o que se repete num segundo cliente, a Terminal Sul. |
| Domingo, 15/11, 9h–10h30 | Aula: da solução ao agente (componentes, harness, ferramentas, evals, guardrails), metade teoria e metade mão na massa. |
| Domingo, 15/11, 10h30–11h30 | Q&A com convidado. |
| Domingo, 15/11, 11h30–15h45 | Construção em grupo, com coaches circulando (almoço das 13h às 14h). O ponto de partida do agente entra no repositório nesse dia. |
| Domingo, 15/11, 16h15 | Pitches dos grupos e fechamento, depois do café da tarde. |

## Mapa das pastas

O material de domingo (dados, ponto de partida do agente) entra neste repositório durante a imersão.

| Pasta | O que tem |
|---|---|
| `case/` | O case da Já Chegou: o briefing e o dossiê, que só aparece no sábado depois do roleplay. |
| `challenge/` | As instruções do desafio do kit, de sábado de manhã. |
| `templates/` | Os modelos dos entregáveis dos checkpoints. |
| `teams/` | Uma pasta por grupo, com nome, integrantes e o link do fork líder. |
| `scripts/` | Utilitários, como o verificador de setup `scripts/check_setup.py`. |
| `tests/` | Os testes automáticos do repositório (`uv run pytest`). |

## Comandos do dia a dia

```bash
uv sync                           # instala as dependências do projeto
uv run pytest                     # roda os testes
python3 scripts/check_setup.py    # confere a sua máquina
```

## Licença

Este repositório é distribuído sob a Apache License 2.0 (veja [`LICENSE`](LICENSE) e [`NOTICE`](NOTICE)). Copyright 2026 Barte.
