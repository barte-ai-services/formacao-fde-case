# Checkpoint 1: diagnóstico e prioridade

**Momento:** checkpoint 1, sábado, 14/11, depois do roleplay e do dossiê.

## Grupo

**Grupo:** 4

**Integrantes:** Lenara Londero, Hugo Penna Oliveira, Pedro Eduardo Thomaz, Lucas Carvalho Rodrigues e Vinicius Feno

---

## 1. O problema

- **O que o cliente disse que é o problema:** cerca de 400 propostas de pagamento por dia montadas à mão, boletos pagos e baixados um a um, e cerca de R$ 120 mil por mês de juros e multa. Ele quer automatizar o boleto. *(Briefing, fala do CFO)*
- **O que o grupo entende que é o problema:** a Já Chegou paga R$ 543 mil por mês por mercadoria que não recebeu, e não recupera nada. Isso acontece porque ninguém confere a nota contra o pedido antes de a mercadoria entrar. *(Dossiê, Anexos 2 e 3)*
- **Onde, no caminho do pedido de compra até o pagamento, ele aparece:** entre a chegada da nota e o recebimento na doca. A nota chega antes da mercadoria, mas só é conferida depois, quando aceitá-la já significa aceitar o pedido. *(Dossiê, falas do controller e do gerente de compras)*
- **Quem sente a dor (por papel):** o controller sente no fechamento, provisionando o que não concilia. O CFO paga sem saber, porque ninguém soma as perdas num lugar só. Compras sente a ruptura quando um fornecedor bloqueia entregas. *(Dossiê, "A situação" e "Quem decide")*
- **Evidência (dossiê ou reunião):**
  - Valor recuperado de fornecedores é zero em todos os meses *(Anexo 3)*.
  - Match automático em 0,7% das notas no CD e 0,4% na loja *(Anexo 3)*.
  - "Quando a gente olha a nota, a mercadoria já entrou" *(fala do controller)*.

---

## 2. O número a mover

### Qual perda

- [x] Pagar errado
- [ ] Pagar atrasado
- [ ] Ruptura de estoque
- [ ] Custo de operar

### Baseline e meta

| Campo | Valor | Fonte |
|---|---|---|
| Indicador (como a perda é medida) | Valor pago sem mercadoria correspondente, menos o recuperado, dividido pelo valor das notas do mês, comparado pela média móvel de 3 meses | Definição do Anexo 2; a divisão e a média móvel são escolhas do grupo para neutralizar a variação de volume e de mês a mês |
| Indicadores de acompanhamento (semanais) | Valor das divergências pegas antes da doca no CD piloto, em reais, e valor da lista do dia marcado com bandeira de risco que foi pago mesmo assim | Suposição do grupo. São a prova dentro das 8 semanas, quando o P1 mensal ainda tem poucos pontos |
| Baseline (valor hoje) | 1,56% (R$ 543 mil sobre R$ 34,8 milhões por mês) | Anexo 2 (P1) e Anexo 1 (valor das notas); divisão feita pelo grupo |
| Período do baseline | Média de janeiro a setembro. Abril concentra quase 40% do P1, por isso o grupo também acompanha o número sem abril | Anexo 2 e nota abaixo dele |
| Meta | Reduzir em cerca de 30% o P1 do CD piloto, sobre a linha de base do CD que sai da Q1. Como referência, −30% na empresa toda levaria de 1,56% para cerca de 1,1% | Suposição do grupo |
| Prazo da meta | Semana 8 do projeto. Até lá, a prova são os indicadores semanais; o P1 mensal do piloto entra na média móvel. A ruptura (P3) não pode subir no piloto | Suposição do grupo |

**Por que esta perda, e não as outras três:**

- É 82% das perdas medidas em reais: R$ 543 mil contra R$ 122 mil de atraso e R$ 45 mil de custo de operar *(Anexo 2)*.
- Hoje nada é recuperado *(Anexo 3)*.
- Atacar o atraso antes faria a empresa pagar mais rápido o que não deveria pagar.

---

## 3. A prioridade

| Frente | Retorno | Tempo até o primeiro valor (5 = mais rápido) | Esforço (5 = menor esforço) | Total |
|---|---|---|---|---|
| Check antecipado e devolução: conferir nota × ordem antes da entrega; a doca recebe, recebe parcial ou recusa | 5 | 3 | 3 | **11** |
| Priorização de caixa e aprovação: lista do dia automática, alçadas, bloqueio de duplicidade | 2 | 4 | 4 | 10 |
| Conciliação ordem × nota × recebido depois do recebimento, com conversão de unidade | 3 | 2 | 2 | 7 |
| Cadastro e ordem complementar na origem | 2 | 1 | 1 | 4 |

**Frente escolhida para começar:** check antecipado e devolução, com piloto num CD, começando pelo alerta antes da doca e pela recusa na doca. Para começar, precisa da credencial da SEFAZ em nome da empresa, hoje no login de um terceirizado, e da leitura das ordens no ERP *(Anexo 6)*. Em paralelo, a lista do dia com bandeira de risco.

**Por quê:**

- É a única frente que age antes de a nota ser aceita. Depois disso, o jurídico entende que não há o que recuperar *(fala do controller)*.
- Começa pelo CD, que concentra 64% do valor com 17% das notas e tem doca agendada *(Anexo 1; divisão feita pelo grupo)*.
- A lista do dia entra junto porque dá ao CFO, já no primeiro mês, a visão do que pode ser pago e do que tem risco. Na semana 1, só com o CSV diário já liberado *(Anexo 6)*, ela marca duplicidade, título sem nota vinculada e valor acima de R$ 100 mil. Quando a conferência começa, passa a marcar também nota sem ordem e nota sem recebimento.

**O que fica para depois, e por quê:**

- **Devolução no ERP:** depende de escrita no ERP, e a homologação é uma cópia de março *(Anexo 6)*. O piloto começa só com alerta e recusa na doca, que não exigem escrita.
- **Conciliação depois do recebimento:** depende da leitura do ERP, ainda sem previsão, e do relatório diário do WMS; nas lojas, a divergência corre por WhatsApp *(Anexo 6)*.
- **Cadastro e ordem complementar:** depende de três áreas e de mudança de processo *(Dossiê, frentes)*.

---

## 4. A reformulação do pedido do CFO

| | Texto |
|---|---|
| O pedido, como o CFO trouxe | "Lançar, pagar e baixar sem ninguém digitar, e parar de pagar juros e multa." |
| O pedido, como o grupo propõe | "Pagar só o que é devido, e pagar no prazo." Primeiro, conferir a nota contra o pedido antes da entrega. Em paralelo, entregar a lista do dia automática, separada entre o que pode ser pago e o que tem risco, com alçadas e bloqueio de duplicidade. |
| Por que a mudança move mais o número | O P1 é 4,5 vezes o P2. Com match automático abaixo de 1%, automatizar o pagamento só acelera o erro. A régua de priorização diz que, se o dado de entrada não é confiável, acelerar a etapa seguinte aumenta o erro. |
| Como o grupo vai apresentar isso ao CFO | 1. Começar pelo que ele pediu: a lista do dia, separada entre o que pode pagar e o que tem risco, e o bloqueio da duplicidade que o fez aprovar tudo à mão. 2. Mostrar o número que ninguém soma: R$ 543 mil por mês, sem retorno. 3. Ligar ao que ele já prometeu ao conselho: escalar sem crescer o time só funciona se o que se paga estiver certo. 4. Pedir que ele patrocine, junto com compras, a regra de recusa na doca. |

**Se o grupo decidir manter o pedido como veio, explique por quê:** não se aplica. O grupo reformula o pedido e atende uma parte dele.

---

## 5. Hipóteses e o que falta saber

### Hipóteses

| # | Hipótese | Como confirmar | Se estiver errada, o que muda |
|---|---|---|---|
| H1 | A maior parte do P1 vem de divergências visíveis na nota antes da entrega: item trocado, unidade de medida, nota sem ordem, duplicidade e item sem cadastro (exceções 2, 4, 5, 6 e 8). Nas exceções 1 e 3, a nota é igual à ordem e só a contagem na doca mostra a falta. | Cruzar as notas pagas de janeiro a setembro com as ordens de compra e classificar cada divergência pelos tipos do Anexo 4. | Se a maior parte for falta física (exceções 1 e 3), o foco passa da conferência nota × ordem para a contagem guiada na doca e na loja. |
| H2 | A empresa pode recusar a nota antes de aceitá-la. A NF-e tem a manifestação do destinatário, que permite registrar "operação não realizada" ou "desconhecimento da operação". Isso daria base para a recusa total ou parcial na doca. | Validar com o jurídico e com o controller, responsável pela área fiscal, como a recusa total e a parcial são feitas hoje. | Se a recusa não for aceita, a alavanca passa a ser negociar créditos e notas de débito com fornecedores, o que é mais lento e depende de compras. |
| H3 | Sem a força-tarefa, o atraso volta ao patamar de janeiro a agosto, cerca de 44% do valor pago após o vencimento. | Acompanhar o CSV diário de títulos pagos em outubro e novembro *(Anexo 6)*. | Se o atraso continuar baixo, o P2 pesa menos e a lista do dia perde ainda mais prioridade. |
| H4 | Com a lista do dia marcada por risco, o CFO segura os pagamentos com bandeira e aceita deixar de aprovar item a item o que não tem risco. | Acompanhar, nas primeiras semanas, quanto do valor com bandeira ele segura e quanto paga mesmo assim. | Se ele pagar mesmo com bandeira, a visibilidade não move o P1: a trava precisa vir de uma regra no fluxo, e não só da lista. |

*A conta de cerca de 44% é uma suposição do grupo: (41% × 9 − 16%) ÷ 8, supondo meses de peso parecido, a partir do Anexo 3.*

### O que falta saber

| # | Pergunta | Para quem (por papel) | Por que importa |
|---|---|---|---|
| Q1 | Quanto do P1 vem do CD e quanto vem das lojas, e de qual tipo de exceção? Por que abril concentrou quase 40%? | Controller | Confirma o CD como piloto e define se a frente 1 começa pela conferência nota × ordem ou pela contagem na doca. |
| Q2 | Compras aceita recusar na doca uma entrega com divergência, mesmo de fornecedor considerado bom? Quem decide a tolerância? | Gerente de compras e comercial | Sem essa regra, o alerta antes da doca não vira recusa e o P1 não cai. |
| Q3 | Quanto custou a semana de força-tarefa de setembro, em horas do controller e da equipe dedicada? | Controller | Define a linha de base honesta do atraso e mostra quanto custa manter o processo à mão. |
| Q4 | Quanto valem em reais os 1,2 ponto percentual de ruptura? | Gerente de compras e comercial | Pode mudar o tamanho da prioridade da lista do dia, que protege os fornecedores críticos. |
| Q5 | Quais campos o CSV diário de títulos traz: número da nota vinculada, linha digitável do boleto, fornecedor e unidade? | Controller | Define quais bandeiras de risco a lista do dia marca já na primeira semana, sem esperar a conferência. |

---

## Conferência antes de entregar

- [x] Uma perda marcada, com baseline, meta e fonte.
- [x] Quatro frentes pontuadas e uma escolhida, com o porquê.
- [x] Pedido do CFO reformulado (ou mantido, com justificativa).
- [x] Pelo menos três hipóteses e três perguntas abertas.
- [x] Nenhuma pessoa citada pelo nome: só pelo papel.
