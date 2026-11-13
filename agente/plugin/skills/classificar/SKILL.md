---
name: classificar
description: Classifica uma nota fiscal de mercadoria da Já Chegou como match ou numa das 8 exceções (E1 a E8), confrontando a nota com a ordem de compra e com a contagem da doca ou da loja. Use no check antecipado de uma nota, antes de propor a ação na doca e o encaminhamento.
---

# Classificar

Ponto de partida. O grupo completa esta skill com a camada de contexto de sábado: o que cada termo quer dizer na Já Chegou, as regras e os casos-limite.

## Objetivo

Dizer se a nota bate com a ordem e com o que chegou (`match`) ou em qual das 8 exceções ela cai. Os códigos estão em [references/excecoes.md](references/excecoes.md).

## Como decidir

- Compare a nota com a ordem, item a item.
- Compare a nota com a contagem da doca ou da loja.
- Escolha uma classificação só.

Para ver os itens lado a lado, rode o comparador na nota em análise (troque `NF-001` pelo `nota_id` dela). Ele mostra o fato (nota, ordem e contagem, com as diferenças de quantidade e valor) e não classifica:

```bash
uv run python ${CLAUDE_SKILL_DIR}/scripts/comparar_itens.py NF-001
```

<!-- A completar pelo grupo:
- o que conta como "mesma compra" para a duplicidade;
- o que fazer quando a nota não cita o pedido;
- como converter caixa em unidade;
- qual diferença de preço é tolerada;
- em que ordem checar as exceções quando mais de uma parece valer.
-->
