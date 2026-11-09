# Checkpoint 2: desenho da solução

> **Momento:** checkpoint 2, sábado, 14/11.
>
> **Prazo:** horário a definir pela coordenação.
>
> **Onde entregar:** no fork do líder do grupo, em `teams/group-N/checkpoint-2-solution-design.md`,
> por pull request.
>
> `group-N` é a pasta do seu grupo: `group-1`, `group-2` e assim por diante.

## Como usar este template

1. Copie este arquivo para `teams/group-N/checkpoint-2-solution-design.md`.
2. Preencha **todos** os campos marcados com `____`. Não apague nenhuma seção.
3. Descreva fluxos como listas numeradas: um passo por linha, com quem faz (papel ou sistema).
4. O desenho tem de mover o número escolhido no checkpoint 1. Se não move, volte e revise.

---

## Grupo e ponto de partida

- Grupo: ____
- Perda escolhida no checkpoint 1: ____
- Número a mover (baseline → meta): ____ → ____
- Frente escolhida: ____

## 1. Fluxo atual

Como o processo funciona hoje, do ponto em que a frente começa até onde ela termina.

1. ____ (quem: ____)
2. ____ (quem: ____)
3. ____ (quem: ____)
4. ____ (quem: ____)
5. ____ (quem: ____)

- Onde a perda acontece neste fluxo (número do passo): ____
- Por que acontece ali: ____

## 2. Fluxo proposto

O mesmo trecho, depois da solução. Marque com **[agente]** os passos que o agente faz e com
**[humano]** os passos em que uma pessoa decide.

1. ____ (quem: ____)
2. ____ (quem: ____)
3. ____ (quem: ____)
4. ____ (quem: ____)
5. ____ (quem: ____)

- O que deixa de acontecer: ____
- O que passa a acontecer: ____

## 3. Componentes

| Componente | O que faz | Entrada | Saída | Sistema ou dado do cliente que usa |
| --- | --- | --- | --- | --- |
| ____ | ____ | ____ | ____ | ____ |
| ____ | ____ | ____ | ____ | ____ |
| ____ | ____ | ____ | ____ | ____ |
| ____ | ____ | ____ | ____ | ____ |

Cada sistema ou dado citado aqui deve estar no checklist de acessos.

## 4. Onde entra o agente

- Tarefa do agente, em uma frase: ____
- O que o agente recebe: ____
- O que o agente devolve: ____
- Ferramentas que o agente usa (consultas, leituras, cálculos): ____
- O que o agente **não** pode fazer: ____

## 5. Onde o humano decide

O agente trabalha em **modo proposta**: ele **propõe**, uma pessoa **decide**. Nada é pago,
recusado ou liberado sem decisão humana.

### Alçadas de aprovação

| Alçada | Faixa de valor | Quem decide (papel) | O que a pessoa vê para decidir |
| --- | --- | --- | --- |
| Alçada 1 | até R$ 5 mil | ____ | ____ |
| Alçada 2 | até R$ 20 mil | ____ | ____ |
| Alçada 3 | até R$ 100 mil | ____ | ____ |
| Alçada 4 | acima de R$ 100 mil | ____ | ____ |

- Quem decide em cada alçada ainda **não** está definido pelo cliente: o grupo propõe e leva
  como pergunta.
- O que acontece quando a pessoa discorda da proposta do agente: ____
- Como a decisão fica registrada: ____

## 6. Riscos

| # | Risco | Probabilidade (baixa, média, alta) | Impacto (baixo, médio, alto) | Como o desenho reduz o risco |
| --- | --- | --- | --- | --- |
| R1 | ____ | ____ | ____ | ____ |
| R2 | ____ | ____ | ____ | ____ |
| R3 | ____ | ____ | ____ | ____ |

Pense pelo menos em: o agente propor errado, o dado de entrada vir incompleto, um acesso não
ser liberado e a equipe do cliente não usar a solução.

## 7. O que se repete na Terminal Sul

A **Terminal Sul** é uma concessionária de aeroporto, o segundo cliente do checkpoint 2.

| Parte da solução | Serve igual | Serve com ajuste (qual) | Não serve (por quê) |
| --- | --- | --- | --- |
| Fluxo proposto | ____ | ____ | ____ |
| Componentes | ____ | ____ | ____ |
| Agente | ____ | ____ | ____ |
| Alçadas e decisão humana | ____ | ____ | ____ |
| Acessos e dados | ____ | ____ | ____ |

- O que é o **núcleo reaproveitável** da solução, em uma frase: ____
- O que é específico da Já Chegou: ____

## Conferência antes de entregar

- [ ] Fluxo atual e proposto têm o mesmo começo e o mesmo fim.
- [ ] Todo passo marcado [agente] tem um passo [humano] de decisão depois dele.
- [ ] As quatro alçadas estão preenchidas ou marcadas como pergunta ao cliente.
- [ ] Pelo menos três riscos com mitigação.
- [ ] A tabela da Terminal Sul está completa.
