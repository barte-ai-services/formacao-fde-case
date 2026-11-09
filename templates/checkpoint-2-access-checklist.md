# Checkpoint 2: checklist de acessos, credenciais e dados

> **Momento:** checkpoint 2, sábado, 14/11.
>
> **Prazo:** horário a definir pela coordenação.
>
> **Onde entregar:** no fork do líder do grupo, em `teams/group-N/checkpoint-2-access-checklist.md`,
> por pull request.
>
> `group-N` é a pasta do seu grupo: `group-1`, `group-2` e assim por diante.

## Como usar este template

1. Copie este arquivo para `teams/group-N/checkpoint-2-access-checklist.md`.
2. Uma linha por acesso. Se o mesmo sistema precisa de leitura e de escrita, são duas linhas.
3. Preencha **todas** as colunas. Se não souber, escreva "não sei" e leve a pergunta para a
   tabela de perguntas no fim.
4. Donos sempre **por papel** (por exemplo: controller, compras, TI), nunca por nome.
5. Peça o **mínimo** necessário. Cada acesso a mais é risco a mais para o cliente.

### Como preencher cada coluna

| Coluna | O que escrever |
| --- | --- |
| Sistema ou fonte | O sistema, a planilha, a caixa de e-mail ou o arquivo. |
| O que precisamos | O dado ou a ação (ler pedidos, ler notas fiscais, gravar um status). |
| Tipo de acesso | Leitura, escrita, exportação de arquivo, credencial de API, usuário de teste. |
| Para quê | Qual parte da solução usa este acesso. |
| Dono (papel) | Quem no cliente pode liberar. |
| Prazo | Até quando o grupo precisa do acesso para não travar o plano. |
| Risco | O que pode dar errado (vazamento, gravação indevida, dado sensível) e o nível: baixo, médio ou alto. |
| Plano B | O que fazer se o acesso não vier a tempo (amostra exportada, dado simulado). |
| Status | Pedido, liberado, negado ou pendente. |

---

## Grupo

- Grupo: ____

## Acessos

| # | Sistema ou fonte | O que precisamos | Tipo de acesso | Para quê | Dono (papel) | Prazo | Risco (nível e motivo) | Plano B | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| A2 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| A3 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| A4 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| A5 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| A6 | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |

## Credenciais: como vão ser guardadas

- Onde as credenciais ficam (nunca no repositório; por exemplo, no arquivo `.env`, que não vai para o Git): ____
- Quem do grupo tem acesso a elas: ____
- Quando e como serão revogadas ao fim do trabalho: ____

## Dados sensíveis

- Quais dados pessoais ou financeiros passam pela solução: ____
- O que o grupo faz para não expô-los (mascarar, não registrar em log, não versionar): ____

## Perguntas para o cliente

| # | Pergunta | Para quem (papel) |
| --- | --- | --- |
| P1 | ____ | ____ |
| P2 | ____ | ____ |
| P3 | ____ | ____ |

## Conferência antes de entregar

- [ ] Toda linha tem dono por papel, prazo, risco e plano B.
- [ ] Nenhum acesso de escrita sem motivo explícito na coluna "Para quê".
- [ ] Nenhuma credencial real escrita neste arquivo.
- [ ] Cada acesso aparece no desenho da solução (`checkpoint-2-solution-design.md`).
