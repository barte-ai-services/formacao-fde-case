# Pitch de domingo · Grupo 2

> **Momento:** pitch dos grupos, domingo, 15/11, às **16h30**.
>
> **Fontes:** "Dossiê" é o dossiê pós-reunião do Pack 2; a solução está em `mcp_server/analista.py`, `.claude/skills/decidir-fila/` e `tests/test_analista.py`; o roteiro da demo vem de `teams/group-2/roteiro-demo.md` e a prova das travas de `teams/group-2/eval.md`.
>
> O bloco Eval é apresentado pelo Danillo Andrade, com o Leonardo Helal.

---

## Grupo

- Grupo: Grupo 2
- Integrantes: Bruno Filho, Daniel Rivelino, Danillo Andrade, Leonardo Helal e Marcelo Calazans (PM)

## Roteiro

| # | Bloco | Tempo | Quem fala |
| --- | --- | --- | --- |
| 1 | Problema | a definir pela coordenação | Bruno |
| 2 | Número | a definir pela coordenação | Bruno |
| 3 | Solução | a definir pela coordenação | Marcelo Calazans |
| 4 | Demo | a definir pela coordenação | Daniel Rivelino, com Leonardo Helal |
| 5 | Eval | a definir pela coordenação | Danillo Andrade, com Leonardo Helal |
| 6 | Próximos passos | a definir pela coordenação | Bruno |

### 1. Problema

- O problema da Já Chegou, em uma frase: a empresa paga notas fiscais que ninguém conferiu contra o pedido e contra o que chegou. Só 0,7% das notas do CD batem sozinhas com a ordem, e o recuperado é zero (Dossiê, Anexo 3).
- O pedido do CFO e como o grupo o reformulou:
  - **Pedido:** "Contratei para automatizar o boleto" (Dossiê). Lançar, pagar e baixar sem digitação, e parar de pagar juros.
  - **Reformulação:** não ajustar o pedido para bater com a nota, e sim o agente propor uma ação para cada nota e uma pessoa da alçada decidir. Automatizar o boleto antes disso só pagaria mais rápido o que está errado.
- Quem sente a dor (por papel):
  - **CFO:** aprova cada pagamento, sem teto, e paga juros.
  - **Controller e analistas do contas a pagar:** cruzam ordem, nota e recebido à mão, por 14 dias até o lançamento no CD.
  - **Compras:** a doca aceita a carga inteira para não romper, e o financeiro paga a divergência depois.

### 2. Número

- A perda escolhida: **pagar errado** (P1).
- Baseline: **R$ 543 mil por mês** pagos sem mercadoria correspondente, média de jan a set, com recuperado zero (Dossiê, Anexo 2). É 1,56% do valor das notas.
- Meta: parar de pagar sem conferência. Toda nota com divergência passa por uma proposta e pela decisão de uma pessoa do nível certo antes de virar pagamento. A meta em reais (perda líquida pela metade em 8 semanas) é suposição do grupo, a validar no piloto.
- Por que este número:
  - P1 é 4,5 vezes os juros (R$ 543 mil contra R$ 122 mil por mês) e 76% da perda em reais do contas a pagar (Dossiê, Anexo 2).
  - O pedido do CFO, como veio, cobre só P2 e P4: R$ 167 mil de R$ 710 mil por mês.

### 3. Solução

- O fluxo proposto, em cinco passos:
  1. A nota é conferida contra a ordem e o recebido, e a regra gera uma **proposta** com a ação na doca: receber, receber parcial ou recusar.
  2. A régua define o **nível** de quem aprova: regra, analista, coordenação, diretoria ou bloqueio.
  3. O analista abre a fila **dentro do Claude**, pelo servidor MCP `ja-chegou-analista`. Onde o host desenha MCP Apps, como o Claude Desktop, a fila abre como tela no chat; no Claude Code, em texto.
  4. Ele abre a proposta, vê a divergência e a evidência, e **aprova ou altera** a ação, com justificativa.
  5. Ele pode pedir ao motor de decisão uma **simulação** do que o motor aprovaria. Nada é aprovado pela simulação.
- Onde entra o agente:
  - A skill `decidir-fila` guia a sessão do analista: mostra a fila, resume a divergência e confirma o que vai gravar.
  - O subagente `auditor-de-notas` audita a nota, mas não tem nenhuma tool que decide.
- Onde o humano decide (modo proposta e alçadas):
  - Toda decisão é de uma pessoa da alçada. O agente só propõe.
  - **As travas estão no código, não no prompt:**
    - o nível é recalculado pela régua e só sobe;
    - diretoria e bloqueio nunca são decididos por este servidor;
    - cada proposta é decidida uma vez;
    - toda recusa devolve `gravada: false` e não grava nada.

### 4. Demo

- Plano A: o vídeo da demo, `teams/group-2/video-demo/demo-fila-analista.mp4` (36 s), tocado no slide da demo. Os números vêm das tools do servidor; a conversa é uma reconstrução animada.
  1. **Ver a fila:** "mostra a minha fila", 34 notas esperando o analista.
  2. **Abrir a NF-035** (E3, Congelados Polar Sul): nota, pedido e doca lado a lado; faltam 49 pizzas na doca.
  3. **Decidir:** aprovar com motivo e confirmação; a decisão é gravada e a fila cai de 34 para 33.
  4. **As travas de alçada:** o que está acima do nível do analista, ou é diretoria ou bloqueio, ele não decide.
- O que o público deve notar:
  - A pessoa decide; o agente organiza e propõe.
  - A recusa vem do sistema, não de uma instrução ao modelo: mesmo que alguém peça ao Claude, a tool não grava.
  - Todo número na tela vem da base, nunca do texto do modelo.
- Plano B: as capturas reais da tela nos slides (a fila no MCP App, a NF-006 aprovada e a recusa da NF-017, acima da alçada). O roteiro da demo ao vivo continua em `teams/group-2/roteiro-demo.md`.
- Código final e teste técnico: ficam com o time da Barte, a partir do servidor no fork líder.

### 5. Eval

- Contra o que o agente foi avaliado:
  - 33 testes do servidor `ja-chegou-analista`, rodados offline sobre a base real com propostas de cada tipo, inclusive chamando pelo protocolo MCP;
  - 2 testes que provam que o subagente `auditor-de-notas` não alcança nenhuma tool de decisão;
  - os 13 casos do mock do motor, cada um com a resposta esperada.
- Resultado: **48 de 48 passaram** (tabela trava por trava em `teams/group-2/eval.md`). Na `main`, `make check` dá 111 passando e 3 pulados.
  - As **14 tentativas** de decidir fora da regra ou da alçada foram recusadas sem gravar nada.
  - Nenhuma delegação ao motor gravou decisão.
  - Frase para o palco: "Mesmo que alguém peça ao Claude, a tool não grava. A trava está no sistema, e o teste prova."
- Onde o agente erra, e o que isso significa para o cliente:
  - **A identidade vem do ambiente, sem login.** Em produção, vai para o Cloudflare Access, com a identidade de cada analista.
  - **Duas sessões podem decidir a mesma nota ao mesmo tempo.** Com o banco da solução, a decisão passa a ser única.
  - **O texto do modelo não tem eval de ponta a ponta.** Por isso a pessoa lê a evidência antes de decidir, e todo número vem da base.
  - **A simulação do motor usa uma regra mínima,** não o motor real do Grupo 1.

### 6. Próximos passos

- O que o grupo faria na próxima semana com o cliente:
  - Rodar a fila em modo sombra sobre as notas do CD, com o controller e o CFO assinando o baseline.
  - Ligar a delegação ao motor real do Grupo 1, primeiro só como simulação.
  - Levar o servidor `ja-chegou-analista` para produção: hoje ele roda na máquina do analista e lê arquivos locais; em produção, fica atrás do Cloudflare Access, com a identidade de cada analista, e passa a chamar a API da solução em vez de ler arquivos.
  - Entregar ao time da Barte o código final e o teste técnico do servidor `ja-chegou-analista`, que estão no fork líder.
  - Pedir os acessos que bloqueiam a primeira entrega: credencial de serviço na captura de NF, usuário de leitura no ERP e homologação atualizada (Dossiê, Anexo 6).
- Fica para depois:
  - o processo de **notas de devolução**, para recuperar o que hoje é zero;
  - testar a tela da fila (MCP App) num host de verdade: o código já está na `main`, mas a tela ainda não foi aberta no Claude Desktop;
  - a automação do boleto, que só vem depois da conferência.
- O que se repete na Terminal Sul: a mesma estrutura de três fontes comparadas, proposta e decisão por alçada. A causa e a regra mudam: lá são contrato, declarado e fiscal; aqui, pedido, nota e recebido.
- O pedido ao cliente: o CFO patrocinar o modo proposta, aceitando que a aprovação passe por alçada e não por ele item a item, e liberar os acessos acima.

## Conferência antes de subir ao palco

- [x] Os seis blocos estão preenchidos, na ordem.
- [x] Cada bloco tem quem fala.
- [x] O número aparece com baseline e meta.
- [x] A demo tem plano B.
