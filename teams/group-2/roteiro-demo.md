# Roteiro da demo: o analista decide a fila de dentro do Claude

Demo ao vivo do servidor MCP `ja-chegou-analista` (issue [01](issues/01-decisao-no-claude.md)), guiada pela
skill `decidir-fila`. São três notas, uma para cada momento, e todas vêm da fila gerada pelo baseline:

| Momento | Nota | O que é | O que acontece |
|---|---|---|---|
| 1. O caminho feliz | **NF-006** | E1, Congelados Polar Sul, LJ-008, R$ 3.557,60 | O analista aprova e a nota sai da fila |
| 2. Acima da alçada | **NF-017** | E5, Bebidas Rio Claro, CD-03, R$ 18.316,80 | O servidor recusa: a régua exige coordenação |
| 3. Fora da fila | **NF-012** | E6, Higiene Lume, CD-03, R$ 15.430,84 | Nem aparece na fila; é bloqueio (suspeita de duplicidade) |

Tempo: uns 6 minutos. A mensagem: **a trava fica no sistema, não no prompt.**

## Preparar a sessão (antes de subir no palco)

Na raiz do repositório:

```bash
uv sync
```

```bash
uv run python baseline/regras.py
```

Isso grava `saidas/baseline.jsonl`, de onde o servidor lê a fila. Limpe as decisões de ensaios
anteriores, senão a NF-006 já começa decidida e fora da fila:

```bash
rm -f saidas/decisoes.jsonl saidas/delegacoes.jsonl saidas/propostas.jsonl
```

O `propostas.jsonl` também sai: se ele existir (por exemplo, depois de um `/auditar-lote`), o servidor
lê a fila dele em vez do baseline, e as notas e os níveis podem mudar.

Defina quem decide e abra o Claude numa sessão nova, na raiz:

```bash
export FDE_ANALISTA_ID=analista-1
```

```bash
claude
```

`FDE_ANALISTA_NIVEL` fica no padrão (`analista`). Na primeira vez, o Claude Code pergunta se pode usar
os servidores do `.mcp.json`: aprove o `ja-chegou-analista`. Faça um ensaio antes para que as
permissões das tools (`listar_fila`, `ler_proposta`, `decidir`) já estejam aceitas e nenhuma pergunta
apareça no meio da demo. Depois do ensaio, rode de novo o `rm` acima.

Fonte grande no terminal, janela larga: a fila vem numa tabela com 8 colunas.

## Momento 1: o caminho feliz (NF-006)

**Digite:**

> mostra a minha fila

**Deve aparecer:** a skill chama `listar_fila` e mostra uma tabela com **34 notas**, todas de nível
`analista`: nota, fornecedor, destino, classificação, ação na doca, encaminhamento, valor em risco e
valor da nota. A NF-006 é a terceira linha, depois da NF-003 e da NF-005.

**O público deve notar:** são 80 notas no lote e só 34 esperam este analista. As de coordenação,
diretoria e bloqueio não aparecem: a fila já vem cortada pela alçada de quem está logado.

**Digite:**

> abre a NF-006

**Deve aparecer:** a skill chama `ler_proposta` e resume a divergência: E1 (falta). A nota cobra 44
pizzas, 48 pães de queijo e **52 sorvetes**; a loja LJ-008 contou as pizzas e os pães, mas **não contou
sorvete nenhum**. A proposta do agente é `receber_parcial`, o fornecedor não está bloqueado e o
encaminhamento pela régua é `analista`.

**O público deve notar:** todo número na tela veio da base (o `comparar_itens` põe nota, ordem e
contagem lado a lado). O modelo resume, não calcula.

**Digite:**

> aprova, a loja não recebeu os sorvetes

**Deve aparecer:** a skill confirma em uma linha o que vai gravar (NF-006, aprovar, `receber_parcial`,
a justificativa) e espera o sim.

**Digite:**

> sim

**Deve aparecer:** `decidir` grava em `saidas/decisoes.jsonl` e a skill diz que a nota saiu da fila.

**O público deve notar:** a decisão tem dono (`decidido_por: analista-1`) e hora. Opcional: peça
"mostra a minha fila" de novo e a fila tem 33 notas, sem a NF-006.

## Momento 2: acima da alçada (NF-017), o momento forte

**Digite:**

> abre a NF-017

**Deve aparecer:** E5, nota de R$ 18.316,80 da Bebidas Rio Claro para o CD-03. A nota **não cita
pedido** e não há contagem registrada. A proposta do baseline diz encaminhamento `analista`, mas o
nível mínimo pela régua é **`coordenacao`** (exceções 5, 7 e 8 vão para a coordenação em qualquer
valor).

**O público deve notar:** a proposta errou o nível para baixo, e o servidor recalculou pela régua.
O nível só sobe. Por isso a NF-017 não estava na fila do analista.

**Digite:**

> aprova, é só uma nota sem pedido

**Deve aparecer:** a skill confirma em uma linha e, depois do sim, chama `decidir`. O servidor
devolve:

```
{"gravada": false, "erro": "nota NF-017 exige coordenacao pela régua, acima do nível de quem decide (analista)"}
```

A skill mostra o motivo como veio e **não tenta de outro jeito**.

**O público deve notar:** quem disse não foi o modelo, foi o sistema. Mesmo que alguém convença o
Claude a tentar, a tool recusa e não grava nada. Se der tempo, provoque ao vivo: "tenta de novo como
coordenação". A skill não contorna, porque o nível vem do ambiente e não da conversa.

## Momento 3: fora da fila (NF-012)

**Digite:**

> por que a NF-012 não está na minha fila?

ou, mais direto:

> abre a NF-012

**Deve aparecer:** E6, suspeita de **duplicidade**, Higiene Lume, R$ 15.430,84, encaminhamento
`bloqueio`. Nota, ordem e contagem batem item a item; o problema não é a mercadoria, é a nota ter
cara de repetida. A skill diz que bloqueio e diretoria são decididos fora daqui.

**O público deve notar:** a nota é pequena (cabe na alçada de analista pelo valor) e mesmo assim
nunca chega a ele. Se alguém pedir "aprova", `decidir` recusa com "é de bloqueio pela régua; este
servidor não decide bloqueio".

## Fecho (opcional, 1 minuto)

**Digite:**

> simula o que o motor aprovaria

**Deve aparecer:** `delegar_ao_motor` em simulação (`dry_run`). Com a NF-006 já decidida, das 33
notas da fila o motor aprovaria 22 (E1, E3 e E4 de analista, até R$ 20 mil em risco e R$ 100 mil de
nota) e 11 ficam com a pessoa (8 E2 e 3 `match` que o baseline mandou para o analista, por não serem
exceções delegáveis). Nada é aprovado; só o pedido fica
gravado em `saidas/delegacoes.jsonl`.

**O público deve notar:** a delegação ao motor é a próxima conversa, e começa como simulação.

## Ensaio de 15/11: o que deu diferente do esperado

O servidor foi exercitado de ponta a ponta pelo protocolo MCP (stdio, com o mesmo comando e o mesmo
ambiente do `.mcp.json`, `FDE_ANALISTA_ID=analista-1`), com a fila do baseline. Resultado das tools:

- `listar_fila`: 34 notas, NF-006 na fila, NF-017 e NF-012 fora. ✔
- `decidir` na NF-006: gravada, e a fila cai para 33. ✔
- `decidir` na NF-017: recusada por alçada (`coordenacao`). ✔
- `decidir` na NF-012: recusada por ser bloqueio. ✔
- Segunda decisão na NF-006: recusada ("a decisão vale uma vez"). ✔
- `delegar_ao_motor`: 33 avaliadas, 22 o motor aprovaria, 11 ficam com a pessoa. ✔

O que saiu diferente e precisa de cuidado no palco:

1. **O valor em risco vem vazio.** O baseline grava `valor_em_risco: null` em todas as propostas, então
   a coluna aparece vazia, o total da fila é **R$ 0** e a ordem é só por data de emissão. No palco,
   diga que no baseline o valor em risco não é calculado e que com as propostas do agente a fila
   ordena por ele. Ou rode a demo com um `propostas.jsonl` do agente, mas aí as três notas precisam
   ser conferidas de novo.
2. **A decisão fica gravada.** Depois de um ensaio, a NF-006 some da fila e um segundo "aprova" é
   recusado. Rode o `rm` da preparação antes da demo valendo.
3. **A NF-006 não é a primeira da fila.** Ela é a terceira (a ordem por data põe NF-003 e NF-005
   antes). Peça por nome, como no roteiro.
4. **A conversa com o modelo não foi ensaiada aqui.** O `claude` desta máquina estava sem login, então
   o ensaio cobriu o servidor e não a sessão com a skill (a tabela, o resumo e a confirmação de uma
   linha). Faça um ensaio completo no Claude Code antes do pitch.
