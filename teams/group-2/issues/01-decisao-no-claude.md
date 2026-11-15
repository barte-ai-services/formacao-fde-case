# Como analista, quero decidir a fila de propostas de dentro do Claude

> Grupo 2 · construção de domingo, 15/11. Recorte para caber até as 16h.

## Objetivo

O analista do contas a pagar decide a fila de **propostas** sem sair do Claude Code: vê o que espera
uma pessoa, abre a proposta com a **divergência** e a evidência, e aprova ou altera a **ação na doca**.
Ele também pode pedir ao motor de decisão uma simulação do que o motor aprovaria.

A trava fica no sistema, não só no prompt: a tool de escrita recusa o que os **limites de aprovação**
não permitem. Nenhum número vem do texto do modelo; tudo vem da base.

## Onde fica

- **Um servidor MCP novo, `ja-chegou-analista`**, em `mcp_server/analista.py`, registrado no
  `.mcp.json` ao lado do `ja-chegou`. Ele é separado de propósito: o subagente `auditor-de-notas`
  libera `mcp__ja-chegou__*`, e não pode ganhar uma tool que decide.
- Reaproveita `jachegou.base.Base`, `jachegou.comparar.comparar` e a régua de `dados/regua.json`.
  O nível mínimo é recalculado pela régua, com a mesma lógica de `nivel_minimo` do `ja-chegou`
  (extrair para `jachegou/` e importar nos dois servidores, sem duplicar).
- **Uma skill `decidir-fila`**, em `.claude/skills/decidir-fila/SKILL.md`, que orienta a sessão do analista.
- **Testes** em `tests/test_analista.py`.

## Quem é o analista

O papel vem do ambiente, repassado pelo `.mcp.json`:

- `FDE_ANALISTA_ID`: quem decide (ex.: `analista-1`). Obrigatório para gravar.
- `FDE_ANALISTA_NIVEL`: `analista` ou `coordenacao`. Padrão `analista`.

Diretoria e bloqueio nunca são decididos por este servidor.

## As tools

| Tool | Faz | Escreve |
|---|---|---|
| `listar_fila(nivel?, destino?)` | As propostas que esperam pessoa e cabem no nível do analista, ainda não decididas, ordenadas por **valor em risco** (maior primeiro) e depois por data de emissão. Cada linha: nota, fornecedor, destino, classificação, ação na doca proposta, encaminhamento, valor em risco, valor da nota. | Não |
| `ler_proposta(nota_id)` | A proposta, a nota resumida, o `comparar_itens` da nota, o fornecedor (inclusive se está bloqueado) e o nível mínimo pela régua. | Não |
| `decidir(nota_id, decisao, justificativa, acao_doca?)` | `decisao`: `aprovar` (mantém a ação proposta) ou `alterar` (troca a ação, `acao_doca` obrigatória). Grava em `saidas/decisoes.jsonl`. | Sim |
| `delegar_ao_motor(nota_ids?, classificacoes?)` | Grava um pedido de delegação em `saidas/delegacoes.jsonl`, sempre como **simulação** (`dry_run: true`), e devolve o que o motor aprovaria e o que ficaria com a pessoa. Nada é aprovado. | Só o pedido |

### De onde vem a fila

As propostas são lidas de `saidas/` (arquivo em `FDE_ARQUIVO_PROPOSTAS`, padrão `propostas.jsonl`;
se não existir, `baseline.jsonl`). Por nota, vale a última proposta aceita (linhas com `recusada`
são ignoradas). Entra na fila só o que tem encaminhamento `analista` ou `coordenacao`: `regra` não
espera pessoa, e `diretoria` e `bloqueio` ficam fora deste servidor.

## Caminho feliz

1. O analista abre o Claude Code na raiz e pede "mostra a minha fila".
2. A skill chama `listar_fila` e mostra a fila numa tabela, com o total de valor em risco.
3. Ele pede "abre a NF-0xx". A skill chama `ler_proposta` e resume a divergência e a evidência.
4. Ele diz "aprova". A skill confirma em uma linha o que vai gravar e chama `decidir`.
5. A nota sai da fila.

## Casos de canto

- Proposta com encaminhamento abaixo do nível mínimo recalculado pela régua: entra na fila com o
  nível mínimo, não com o do arquivo. O nível só sobe.
- Fornecedor bloqueado ou nota acima de R$ 100 mil: diretoria, fora da fila.
- E6: bloqueio, fora da fila.
- `alterar` para a mesma ação proposta: tratar como `aprovar`.
- `delegar_ao_motor` sem filtro: simula a fila inteira do nível do analista.

## Casos de erro (a tool recusa e não grava)

- `FDE_ANALISTA_ID` vazio.
- Nota inexistente ou sem proposta.
- Nota já decidida (a decisão vale uma vez).
- Nível mínimo da nota acima do `FDE_ANALISTA_NIVEL` (ex.: analista decidindo coordenação).
- Nível mínimo `diretoria` ou `bloqueio`.
- `decisao` fora de `aprovar` e `alterar`; `alterar` sem `acao_doca` válida.
- Justificativa com menos de 10 caracteres.

Cada recusa devolve `{"gravada": false, "erro": "..."}` com o motivo em português.

## Critérios de aceite

- [ ] AC-1: `listar_fila` devolve só propostas não decididas, de nível ao alcance do analista,
      ordenadas por valor em risco.
- [ ] AC-2: `decidir` grava em `saidas/decisoes.jsonl` uma linha com `nota_id`, `decisao`,
      `acao_doca` final, `nivel_minimo`, `decidido_por`, `nivel_de_quem_decidiu`, `justificativa`
      e `decidido_em`.
- [ ] AC-3: `decidir` recusa todos os casos de erro acima, sem gravar, e um teste cobre cada um.
- [ ] AC-4: uma nota decidida não volta para a fila e não aceita segunda decisão.
- [ ] AC-5: `delegar_ao_motor` nunca grava decisão; só grava o pedido e devolve a simulação.
- [ ] AC-6: o `auditor-de-notas` continua sem acesso às tools do `ja-chegou-analista`
      (o teste do subagente segue passando).
- [ ] AC-7: a skill `decidir-fila` diz o que a sessão nunca faz: inventar número, decidir sem o
      analista pedir, ou contornar uma recusa da tool.
- [ ] AC-8: `make check` passa.

## Fica para outras issues

- O MCP App, com a fila e a proposta desenhadas dentro do chat.
- O motor de decisão de verdade (é do grupo 1). Aqui a simulação usa uma regra simples ou o mock.
- Publicar o servidor na Cloudflare e o login pelo Access.
- Aviso por e-mail a quem aprova.

## Métrica para o pitch

Numa rodada com a fila do baseline: quantas propostas o analista decide em 10 minutos, quanto valor
em risco passa por uma pessoa e quantas tentativas de decidir acima da alçada o servidor recusou.
