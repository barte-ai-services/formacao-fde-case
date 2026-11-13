# Domingo · da solução ao agente

Um agente com três skills no check antecipado da Já Chegou: ele confronta a nota fiscal com a ordem de compra e com a contagem da doca, diz o que fazer com a mercadoria e para quem o caso vai. O agente nunca aprova nem paga.

## O que tem aqui

| Pasta | Conteúdo |
| --- | --- |
| `dados/` | Base sintética: 80 notas pendentes, ordens, recebimentos, cadastro, fornecedores, notas já lançadas, pagamentos fora do fluxo e a régua de alçadas |
| `dados/gabarito/` | A resposta certa de cada nota, usada só pelo eval. Chega no domingo de manhã |
| `mcp_server/` | As tools do agente, expostas por MCP |
| `agente/` | O agente: as instruções (`instrucoes.md`), as três skills (`plugin/skills/`) e o script que roda no Claude Agent SDK (`rodar_agente.py`) |
| `baseline/` | Regras simples, sem IA, para comparar |
| `eval/` | Mede as propostas contra o gabarito |

## As três skills

| Skill | Pergunta | Saída |
| --- | --- | --- |
| 1 · Classificar | A nota bate com a ordem e com o que chegou? | `match` ou uma das 8 exceções |
| 2 · Propor a ação na doca | O que a doca faz com a mercadoria? | `receber`, `receber_parcial` ou `recusar` |
| 3 · Encaminhar | Quem decide? | `regra`, `analista`, `coordenacao`, `diretoria` ou `bloqueio` |

As skills são um ponto de partida. O trabalho do grupo é completá-las com a camada de contexto de sábado e medir cada versão.

### Onde ficam e como editar

Cada skill segue o formato [Agent Skills](https://code.claude.com/docs/en/skills) da Anthropic: uma pasta com um `SKILL.md`, e ao lado o que ela usa sob demanda. As três vivem num plugin local, `agente/plugin/`, que o agente carrega por caminho explícito:

```
agente/plugin/
├── .claude-plugin/plugin.json          # o plugin "domingo"
└── skills/
    ├── classificar/
    │   ├── SKILL.md
    │   ├── references/excecoes.md      # os códigos das 8 exceções
    │   └── scripts/comparar_itens.py   # nota, ordem e contagem da doca lado a lado
    ├── propor-acao-na-doca/SKILL.md
    └── encaminhar/SKILL.md
```

- O `SKILL.md` abre com um frontmatter YAML: `name` (o nome da pasta) e `description`. O modelo só vê o nome e a descrição de cada skill até decidir usar uma; aí carrega o `SKILL.md` inteiro. Por isso a descrição diz o que a skill faz e quando usar.
- O corpo do `SKILL.md` é a regra que vocês escrevem. O que for longo (tabelas, exemplos, casos-limite) vai para `references/`, citado no `SKILL.md`, e o modelo lê quando precisa.
- O que é cálculo e não julgamento vai para `scripts/`. O comparador da skill `classificar` mostra o fato e não classifica; rode-o sozinho para ver o que o agente vê:

```bash
uv run python agente/plugin/skills/classificar/scripts/comparar_itens.py NF-001
```

Para testar outra versão sem apagar a de vocês, copie `agente/plugin/` para outra pasta e rode com `--skills <pasta>`.

## Como rodar

```bash
cp .env.example .env                     # preencha ANTHROPIC_API_KEY
uv sync

uv run python baseline/regras.py          # 1. o que regras simples conseguem
uv run python agente/rodar_agente.py --nota NF-001 --verbose      # 2. o agente numa nota (mostra cada tool e cada skill invocada)
uv run python agente/rodar_agente.py --todas --origem grupo-1     # 3. nas 80 notas
uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl --erros
```

O agente roda no [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) (`claude-agent-sdk`): o mesmo laço do Claude Code, com `agente/instrucoes.md` como prompt de sistema, o servidor MCP `ja-chegou` por stdio e as três skills do plugin. O modelo vem de `AGENT_MODEL` (padrão `claude-sonnet-5-5`). As opções `--limite`, `--saida`, `--origem` e `--skills` continuam valendo.

No Claude Code, o `.mcp.json` da raiz já registra o servidor `ja-chegou`: dá para conversar com os dados e testar uma skill antes de rodar o lote.

## A base

| Tipo | Notas | O que testa |
| --- | --- | --- |
| match | 8 | Inclui nota sem número de pedido com ordem existente, diferença dentro da tolerância e fornecedor bloqueado |
| E1 · Falta física | 9 | Item na nota que não chegou |
| E2 · Item trocado | 9 | Item fora da ordem no lugar de um pedido |
| E3 · Quantidade menor | 9 | Chegou menos do que a nota cobra |
| E4 · Unidade de medida | 9 | Ordem em unidade, nota em caixa de 4: o preço parece 300% maior |
| E5 · Nota sem ordem | 9 | Ninguém sabe quem comprou |
| E6 · Duplicidade | 9 | Mesma nota de novo ou nota reemitida para a mesma compra |
| E7 · Pago fora do fluxo | 9 | Loja recebeu e pagou antes de a nota chegar |
| E8 · Item sem cadastro | 9 | Ordem travada, mercadoria entrou mesmo assim |

As notas vão de cerca de R$ 450 a R$ 160 mil, para a régua de alçadas trabalhar em todos os níveis. A Já Chegou, os fornecedores, os CNPJs e as chaves são fictícios; os CNPJs têm dígito verificador inválido de propósito.

## O baseline

| Medida | Baseline |
| --- | --- |
| Acerto completo (as três skills) | 46% |
| Classificação | 80% |
| Ação na doca | 69% |
| Encaminhamento | 58% |

As regras simples acertam falta, troca e quantidade menor. Erram onde o sentido não está no campo: nota sem número de pedido, reemissão, caixa, tolerância, compra emergencial e a régua. Se o agente não passar disso, ele não se justifica.

## Guardrails

- Não existe tool para aprovar, pagar, baixar ou escrever no ERP. A única escrita é `registrar_proposta`.
- `registrar_proposta` recusa encaminhamento abaixo do que a régua exige para a classificação informada. A trava fica no sistema, não só no prompt. A recusa não diz qual é o mínimo, e fica gravada no arquivo de propostas: o eval mostra o encaminhamento na primeira tentativa, e não só no que passou depois de recusado.
- O servidor nunca lê `dados/gabarito/`.
- O agente roda isolado do repositório: `setting_sources=[]` não carrega o `.claude/settings.json` (nem os plugins que ele habilita) nem o `CLAUDE.md`, e o MCP é só o `ja-chegou` (`strict_mcp_config`). As skills entram por caminho explícito, pelo plugin local.
- As ferramentas do agente são só as tools do `ja-chegou`, `Skill`, `Read` e `Bash`, sem pedir permissão a ninguém (`permission_mode="dontAsk"`): o que não está liberado é negado.
- Um hook `PreToolUse` em `agente/rodar_agente.py` nega por padrão: do disco, o agente só lê os arquivos do plugin (as references das skills), e os dados chegam pelas tools do `ja-chegou`. Assim nem `dados/gabarito/` nem o `.env` são lidos, nem pelo `Bash`, que só roda o comparador de itens numa nota. Escrita, só em `saidas/`.
