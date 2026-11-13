---
name: definir-aprovador
description: Quem precisa aprovar o caso desta nota fiscal da Já Chegou pela régua de alçadas? Responde com regra, analista, coordenacao, diretoria ou bloqueio, a partir da divergência, do fornecedor e do valor total da nota. O agente só propõe o aprovador e nunca aprova. Use por último, depois de classificar-divergencia e de decidir-recebimento, antes de registrar a proposta.
---

# Skill 3 — Definir o aprovador

Ponto de partida. A régua completa está na tool `ler_regua`.

## Objetivo

Dizer quem precisa aprovar o caso: `regra`, `analista`, `coordenacao`, `diretoria` ou `bloqueio`.

## Como decidir

- Leia a régua com `ler_regua` e o fornecedor com `ler_fornecedor`.
- Use o valor total da nota.
- O agente só propõe o aprovador: nunca aprova nem paga.

<!-- A completar pelo grupo: a ordem de precedência entre os níveis quando mais de uma condição vale. -->
