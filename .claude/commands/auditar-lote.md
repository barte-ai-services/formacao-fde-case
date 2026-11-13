---
description: Roda o subagente auditor-de-notas nas notas pendentes da Já Chegou, uma nota por vez, e diz quantas propostas foram gravadas em saidas/. Aceita um limite opcional, como /auditar-lote 5.
argument-hint: "[limite]"
allowed-tools: Agent, mcp__ja-chegou__listar_notas_pendentes
---

# Auditar o lote de notas pendentes

Você coordena o lote do check antecipado. Quem audita cada nota é o subagente `auditor-de-notas`; você só lista as notas, despacha o subagente e conta o resultado. Você não audita nenhuma nota.

Limite pedido: `$ARGUMENTS`

## Procedimento

1. **Leia o limite.** Se o limite pedido estiver vazio, o lote são todas as notas pendentes. Se for um número inteiro maior que zero, o lote são as primeiras notas da lista, até esse número. Se for outra coisa, pare e responda só `Uso: /auditar-lote [limite], por exemplo /auditar-lote 5`.
2. **Liste as notas** com `mcp__ja-chegou__listar_notas_pendentes`, sem filtros. Use os `nota_id` na ordem em que a tool os devolve e corte a lista no limite. Se a tool responder com erro ou com uma lista vazia, pare e diga o que ela respondeu.
3. **Despache o subagente uma nota por vez**, com a tool `Agent`, `subagent_type` igual a `auditor-de-notas`. O pedido de cada despacho é exatamente esta frase, trocando só o `nota_id`:

   ```text
   Faça o check antecipado da nota <nota_id> e registre a proposta.
   ```

   Espere a resposta de um subagente antes de despachar o próximo. Não ponha no pedido nada além dessa frase: nem dica, nem o resultado de outra nota, nem o que você acha da nota.
4. **Anote a primeira linha da resposta** de cada subagente. `Proposta registrada · <nota_id>` conta como proposta gravada. Qualquer outra resposta, inclusive `Proposta não registrada · <nota_id>`, conta como nota sem proposta: guarde o `nota_id` e a linha `Motivo:` dela. Não despache a mesma nota de novo.
5. **Siga até o fim do lote**, mesmo que alguma nota fique sem proposta.

## O que você não faz

- Não chama `ler_nota`, `comparar_itens`, `registrar_proposta` nem outra tool do `ja-chegou` além de `listar_notas_pendentes`. A proposta de cada nota é do subagente; uma proposta registrada por você mede você, e não o agente.
- Não lê arquivo nenhum do repositório, e em especial nada de `dados/gabarito/`.
- Não corrige, completa nem repete a proposta de um subagente.
- Não roda o eval: diz qual comando rodar.

## Ao terminar

Responda neste formato, sem mais nada:

```text
Lote concluído · <propostas gravadas> de <notas despachadas> notas com proposta registrada
Sem proposta: <cada nota_id com o Motivo, ou "nenhuma">
As propostas estão em saidas/propostas.jsonl (ou no arquivo de FDE_ARQUIVO_PROPOSTAS). Para medir, rode no terminal:
uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl --erros
Se gravou noutro arquivo com FDE_ARQUIVO_PROPOSTAS, troque saidas/propostas.jsonl pelo nome dele no comando.
```
