# Domingo · da solução ao agente

Um agente com três skills no check antecipado da Já Chegou: ele confronta a nota fiscal com a ordem de compra e com a contagem da doca, diz o que fazer com a mercadoria e para quem o caso vai. O agente nunca aprova nem paga.

## O que tem aqui

| Pasta | Conteúdo |
| --- | --- |
| `dados/` | Base sintética: 80 notas pendentes, ordens, recebimentos, cadastro, fornecedores, notas já lançadas, pagamentos fora do fluxo e a régua de alçadas |
| `dados/gabarito/` | A resposta certa de cada nota, usada só pelo eval. Chega no domingo de manhã |
| `mcp_server/` | As tools do agente, expostas por MCP (o servidor `ja-chegou`) |
| `.claude/agents/check-antecipado.md` | O agente: um subagente do Claude Code. O frontmatter diz as tools e as skills; o corpo é o prompt de sistema |
| `.claude/skills/` | As três skills, no formato Agent Skills |
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

Cada skill segue o formato [Agent Skills](https://code.claude.com/docs/en/skills) da Anthropic: uma pasta com um `SKILL.md`. As três ficam nas skills do projeto, em `.claude/skills/`:

```
.claude/
├── agents/
│   └── check-antecipado.md         # o subagente: frontmatter + prompt de sistema
└── skills/
    ├── classificar/SKILL.md
    ├── propor-acao-na-doca/SKILL.md
    └── encaminhar/SKILL.md
```

- O `SKILL.md` abre com um frontmatter YAML: `name` (o nome da pasta) e `description`, que diz o que a skill faz e quando usar. O corpo é a regra que vocês escrevem.
- O subagente carrega as três já no começo, pelo campo `skills` do frontmatter: o conteúdo inteiro de cada `SKILL.md` entra no contexto dele.
- O subagente não tem `Read` nem `Bash`. Por isso tudo o que a skill precisa saber fica no próprio `SKILL.md`: uma pasta `references/` ao lado não seria lida.
- O que é cálculo e não julgamento vira tool do `ja-chegou`. A `comparar_itens` põe nota, ordem e contagem da doca lado a lado, item a item, com as diferenças de quantidade e valor. Ela mostra o fato e não classifica.

### O agente

O agente é o arquivo `.claude/agents/check-antecipado.md`, um [subagente do Claude Code](https://code.claude.com/docs/en/sub-agents):

- **O corpo é o prompt de sistema.** Para mudar como o agente trabalha, editem o texto depois do frontmatter.
- **`tools` libera só as tools do `ja-chegou`** (`mcp__ja-chegou__*`). Sem `Read`, `Bash`, `Write`, `Edit`, `Glob` e `Grep`, o agente não abre arquivo nenhum, nem `dados/gabarito/`. A única escrita é `registrar_proposta`.
- **`skills` carrega as três skills.** O agente não tem a tool `Skill`, então não invoca outras skills do projeto, da sua conta ou dos plugins.
- **`model` é o modelo do agente** (`sonnet`).

Não deixem de fora nenhum desses campos ao editar: é o frontmatter que segura os guardrails.

## Como rodar

Tudo roda com o **login da sua conta no Claude Code**: não há chave da API para configurar. Rode os comandos na raiz do repositório.

Antes de tudo, o baseline, para saber o número a bater:

```bash
uv sync
uv run python baseline/regras.py
```

### O agente numa nota

Abra o Claude Code na raiz do repositório (`claude`). Na primeira vez, ele pergunta se pode usar o servidor `ja-chegou` do `.mcp.json`: aprove. Depois peça:

```
use o subagente check-antecipado na nota NF-001
```

O Claude despacha o subagente, que lê a nota pelas tools do `ja-chegou`, aplica as três skills e termina com `registrar_proposta`. Quando ele pedir permissão para usar uma tool do `ja-chegou`, aprove. Para conferir o que o subagente tem, rode `/agents`.

### O agente nas 80 notas

De dentro do Claude Code, peça:

```
liste as notas pendentes com listar_notas_pendentes e use o subagente check-antecipado em cada uma, uma nota por vez
```

Ou, no terminal, um laço com `claude -p --agent check-antecipado`. Cada nota roda numa sessão própria, com o subagente no lugar do Claude Code. `--allowedTools` libera as tools do `ja-chegou` sem perguntar, já que no `-p` não há ninguém para aprovar:

```bash
for nota in $(uv run python -c "from jachegou.base import Base; print(*Base().notas)"); do
  claude -p --agent check-antecipado --allowedTools "mcp__ja-chegou__*" \
    "Faça o check antecipado da nota $nota e registre a proposta com registrar_proposta."
done
```

Para testar antes num pedaço, troque `print(*Base().notas)` por `print(*list(Base().notas)[:10])`.

### Medir

`registrar_proposta` grava cada proposta em `saidas/propostas.jsonl`. O eval e o baseline são os mesmos de sempre:

```bash
uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl --erros
```

O arquivo acumula: se a mesma nota tiver mais de uma proposta, vale a última. Para medir uma versão nova das skills do zero, renomeie ou apague `saidas/propostas.jsonl` antes de rodar o lote.

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
- As ferramentas do subagente são só as tools do `ja-chegou` (`tools: mcp__ja-chegou__*`). Sem `Read`, `Bash`, `Write`, `Edit`, `Glob` e `Grep`, ele não lê `dados/gabarito/` nem o `.env`, e não escreve fora de `saidas/`.
- As skills entram pelo campo `skills` do frontmatter. Sem a tool `Skill`, o subagente não carrega as outras skills do projeto, da sua conta ou dos plugins do `.claude/settings.json`.
