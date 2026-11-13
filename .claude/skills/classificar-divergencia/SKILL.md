---
name: classificar-divergencia
description: O que há de errado com esta nota fiscal de mercadoria da Já Chegou? Responde se a nota bate com a ordem de compra e com a contagem da doca ou da loja (match) ou em qual das 8 exceções (E1 a E8) ela cai. Use primeiro no check antecipado de cada nota, antes de decidir-recebimento e de definir-aprovador.
---

# Skill 1 — Classificar a divergência

Ponto de partida. O grupo completa esta skill com a camada de contexto de sábado: o que cada termo quer dizer na Já Chegou, as regras e os casos-limite.

## Objetivo

Dizer se a nota bate com a ordem e com o que chegou (`match`) ou em qual das 8 exceções ela cai.

## As 8 exceções

| Código | Exceção |
| --- | --- |
| E1 | Falta física |
| E2 | Item trocado |
| E3 | Quantidade menor |
| E4 | Unidade de medida |
| E5 | Nota sem ordem |
| E6 | Duplicidade |
| E7 | Pago fora do fluxo |
| E8 | Item sem cadastro |

<!-- A completar pelo grupo: o que cada exceção quer dizer na Já Chegou, com um exemplo da base. -->

## Como decidir

- Compare a nota com a ordem, item a item.
- Compare a nota com a contagem da doca ou da loja.
- Escolha uma classificação só.

Para ver os itens lado a lado, chame a tool `comparar_itens` do `ja-chegou` com o `nota_id` da nota em análise. Ela mostra o fato (nota, ordem e contagem, com as diferenças de quantidade e valor) e não classifica.

<!-- A completar pelo grupo:
- o que conta como "mesma compra" para a duplicidade;
- o que fazer quando a nota não cita o pedido;
- como converter caixa em unidade;
- qual diferença de preço é tolerada;
- em que ordem checar as exceções quando mais de uma parece valer.
-->
