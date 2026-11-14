# Dossiê pós-reunião: Já Chegou

> Sábado, 14/11, 10h30. Leia depois da primeira reunião com o cliente. O briefing de antes da
> reunião está em [`../briefing.md`](../briefing.md).

O CFO pediu para automatizar boletos e parar de pagar juros. As conversas com o time mostram que
a Já Chegou perde cerca de **R$ 665 mil por mês** pagando errado e pagando atrasado, quase 15
vezes o custo do time que paga. Este dossiê reúne o que o squad teria ouvido em cinco a sete
horas de entrevistas depois da primeira reunião.

## A situação

É a segunda semana do projeto. O CFO espera ver algo funcionando no primeiro mês e já contou ao
conselho que o financeiro vai escalar sem crescer o time. O próprio CFO aprova cada pagamento,
sem teto, desde que um boleto foi pago duas vezes. O controller fecha o mês provisionando o que
não concilia.

Ninguém na empresa soma as perdas do contas a pagar num lugar só. Cada área vê a sua parte. O
squad precisa decidir, até o checkpoint de sábado, qual problema atacar primeiro, qual número vai
provar o valor e como levar essa conversa ao CFO.

## Quem decide

Três cargos respondem por toda a operação do contas a pagar, do pedido ao pagamento.

| Cargo | O que quer | Como é medido |
| --- | --- | --- |
| CFO, sponsor | Parar de pagar juros e multa, fechar o mês mais cedo e controlar cada saída de caixa; aprova tudo, sem teto | Resultado financeiro, fechamento, caixa e relação com bancos |
| Controller | Fechar sem provisão gorda, menos fila manual no contas a pagar, hoje com 5 analistas terceirizados, e o hub e o ERP estáveis | Prazo de fechamento e ajustes, prazo de pagamento e disponibilidade dos sistemas |
| Gerente de compras e comercial | Produto novo na prateleira, mesmo sem cadastro, receber rápido e não romper estoque; também responde pelo cadastro de produtos e fornecedores | Venda, margem e ruptura |

Os incentivos não se alinham. Compras e comercial ganham quando a mercadoria entra. O financeiro
absorve o custo da divergência depois.

## Como o contas a pagar funciona hoje

O fluxo tem duas etapas sem integração entre elas. A primeira confere se a nota está certa. A
segunda decide o que pagar com o caixa do dia e hoje começa antes de a primeira terminar.

**Da compra à nota conferida**

1. O forecast gera o plano de compra e a ordem sobe para o ERP; 20% dos pedidos ainda sobem por
   CSV feito à mão.
2. A ordem vai ao fornecedor, 60% por e-mail automático e o resto em CSV ou PDF.
3. O fornecedor emite a nota antes de entregar.
4. O CD recebe com doca agendada em planilha; a loja recebe a qualquer hora pelo app.
5. A nota entra pela SEFAZ e o time cruza ordem, nota e recebido à mão.
6. Divergência vira ordem complementar, criada por três áreas, em 2 dias a 3 meses.

**Do caixa ao pagamento**

7. Os analistas do contas a pagar montam a lista do dia, com cerca de 400 propostas, a partir do
   ERP, do e-mail e do WhatsApp.
8. O saldo é conferido às 8h e muda ao longo do dia.
9. O CFO decide o que pagar entre 16h e 18h, com pagamentos parciais, e aprova cada item, sem teto
   de valor.
10. Os boletos são pagos um a um no banco e baixados um a um no ERP.
11. Compras emergenciais das lojas são pagas fora do fluxo e aparecem depois.

**Fechamento**

12. O mês fecha quando as notas sem conciliação são resolvidas ou provisionadas.

## O que cada área disse

**CFO.** "Contratei para automatizar o boleto." Para ele, o atraso vem caindo. Em janeiro, 76% do
valor saía depois do vencimento; em setembro, 16%. "Já pagamos o mesmo boleto duas vezes. Desde
então eu aprovo tudo." Abaixo de R$ 5 mil ele assina sem olhar; acima de R$ 100 mil quer ver cada
caso.

**Controller.** Paga-se em média R$ 543 mil por mês sem mercadoria correspondente, e nada volta.
"O jurídico diz que aceitar a nota é aceitar o pedido." A credencial da captura de notas na SEFAZ
está no login de um analista terceirizado. No começo de setembro, com fornecedores ameaçando
suspender entregas, o controller entrou na operação e trabalhou manualmente por uma semana, com
uma equipe dedicada, para pôr em dia os pagamentos vencidos. O processo não mudou. Conferir uma
nota de 80 itens leva mais de 1h30. "Quando a gente olha a nota, a mercadoria já entrou." Nada
escreve no ERP sem passar por homologação, e o ambiente de homologação é uma cópia de março.

**Gerente de compras e comercial.** Item sem cadastro trava a ordem, mas a mercadoria entra mesmo
assim. "Não quero briga com fornecedor bom." A nota quase sempre chega antes da mercadoria, mas
ninguém a olha antes da doca. "Se eu soubesse antes, planejava a equipe e recusava na hora." O WMS
não converte caixa em unidade.

## Anexo 1 · Volume

| Indicador | Média mensal | Faixa jan–set |
| --- | --- | --- |
| Notas fiscais de mercadoria | 11,4 mil (1,9 mil no CD, 9,5 mil nas lojas) | 10,2 a 12,5 mil |
| Valor das notas | R$ 34,8 milhões | R$ 30,7 a 47,5 milhões |
| Valor médio por nota | R$ 11,8 mil no CD, R$ 1,3 mil na loja | — |
| Margem bruta média | Cerca de 32% | — |

## Anexo 2 · As quatro perdas

| Perda | Como se mede | Média mensal | Faixa jan–set |
| --- | --- | --- | --- |
| P1 · Pagar errado | Pago sem mercadoria correspondente, menos o recuperado | R$ 543 mil | R$ 136 mil a R$ 1,8 milhão |
| P2 · Pagar atrasado | Juros e multas a fornecedores | R$ 122 mil | R$ 23 mil a R$ 420 mil |
| P3 · Ruptura por atraso | Disponibilidade perdida em fornecedores que bloquearam entrega | 1,2 ponto percentual | 0 a 4,6 pontos |
| P4 · Custo de operar | Time de conciliação e pagamento | R$ 45 mil | — |

As perdas variam muito de mês a mês. Abril concentrou quase 40% do P1 do período.

## Anexo 3 · Processo

| Indicador | Média | Faixa ou tendência |
| --- | --- | --- |
| Notas com match automático | 0,7% no CD, 0,4% na loja | Estável |
| Dias da nota ao lançamento da fatura | 14 no CD, 8 na loja | 4 a 21 |
| Valor pago após o vencimento | 41% | 76% em janeiro e 16% em setembro. Setembro reflete uma semana de força-tarefa do controller |
| Valor pago por boleto | 66% | 64% a 68% |
| Valor recuperado de fornecedores | Zero | Zero em todos os meses |
| Ordens complementares | 5% a 7% dos pedidos | Estimativa do time |
| Notas sem ordem de compra | Cerca de 4% | Estimativa do time |
| Conferência manual de uma nota de 80 itens | Mais de 1h30 | Estimativa do time |

## Anexo 4 · Exceções

| # | Exceção | Ordem | Nota | Recebido | Efeito |
| --- | --- | --- | --- | --- | --- |
| 1 | Falta física | x + y + z | x + y + z | x + y | Paga z sem receber |
| 2 | Item trocado | x + y + z | x + y + a | x + y + a | Exige ordem complementar |
| 3 | Quantidade menor | x + y + z | x + y + z | x + y + 0,75z | Paga integral |
| 4 | Unidade de medida | 12 unidades | 1 caixa | 1 caixa | Preço diverge cerca de 300% |
| 5 | Nota sem ordem | — | nota | recebido | Ninguém sabe quem comprou |
| 6 | Duplicidade | ordem | duas notas ou dois boletos | recebido | Paga duas vezes |
| 7 | Pago fora do fluxo | — | nota tardia | recebido na loja | Quebra a conciliação bancária |
| 8 | Item sem cadastro | ordem travada | nota | recebido sob pressão comercial | Não integra no ERP |

## Anexo 5 · Sistemas

| Sistema | Papel | Atrito |
| --- | --- | --- |
| Forecast | Gera os planos de compra | 20% dos pedidos ainda sobem por CSV manual |
| Hub de inventário | Consolida estoque e integra os demais | Integra só no sentido hub → ERP |
| WMS do CD | Recebimento com coletor | Não converte unidade; conferência nota × físico manual |
| App de loja | Recebimento pelo celular | Divergência sobe por WhatsApp |
| ERP | Contábil, fiscal e financeiro | Cadastro por planilha importada; baixa de boleto um a um |
| Captura de NF | Busca as notas na SEFAZ | Não cruza com a ordem antes da entrega |

## Anexo 6 · Acessos e credenciais

Situação ao fim da segunda semana. É o ponto de partida do checklist da tarde
([`../../templates/checkpoint-2-access-checklist.md`](../../templates/checkpoint-2-access-checklist.md)).

| Acesso | Para quê | Situação | Quem libera |
| --- | --- | --- | --- |
| Exportação de títulos e pagamentos do ERP | Lista do dia e histórico de pagos | Liberado: CSV diário enviado por e-mail pelo time do controller, com o dado de ontem | Controller |
| Usuário de leitura no ERP, produção | Ordens, notas lançadas, fornecedores | Pedido no kickoff, sem previsão. O controller exige termo de confidencialidade por pessoa | Controller |
| Escrita no ERP | Lançar, baixar, emitir nota de devolução | Não pedido. Nada escreve sem homologação, e a homologação é uma cópia de março | Controller |
| Captura de notas na SEFAZ | Ler a nota antes da entrega | Existe, mas a credencial é o login nominal de um analista terceirizado | Controller, área fiscal |
| Agenda de doca dos CDs | Saber o que chega e quando | Não pedido. Uma planilha compartilhada por CD | Gerente de compras e comercial |
| WMS do CD | Conferir o físico recebido | Não pedido. Só há relatório diário | Gerente de compras e comercial, com o controller |
| Recebimento e divergências das lojas | O que as lojas receberam | Sem acesso estruturado. Divergência corre em grupos de WhatsApp por loja | Gerente de compras e comercial |
| Ordens que sobem por CSV | O que foi pedido fora do fluxo automático | Não pedido. O CSV manual não tem dono fixo | Gerente de compras e comercial |
| Caixa de e-mail do contas a pagar | Notas e boletos que chegam por e-mail | Não pedido. Tem dados pessoais de fornecedores pessoa física | Controller |
| Banco e extratos | Conciliar o pagamento | Não pedido. O plano atual do banco não tem API; pagamento um a um | CFO |
| Onde a solução roda | Hospedagem e dados | Em aberto. O controller aceita hospedar na Barte se os dados fiscais ficarem no Brasil e houver contrato de operador de dados | Controller e CFO |

## Frentes que o time já discutiu

O time interno levantou quatro frentes possíveis para as oito semanas. Não há consenso sobre a
ordem.

| Frente | O que faria |
| --- | --- |
| Check antecipado e devolução | Confrontar a nota com a ordem antes de a mercadoria chegar; a doca recebe, recebe parcial ou recusa, e a divergência vira recusa ou nota de devolução no ERP |
| Conciliação ordem × nota × recebido | Tratar as exceções 1 a 6 depois do recebimento, com conversão de unidade |
| Priorização de caixa e aprovação | Lista do dia automática, regras de prioridade, alçadas e pagamento em lote |
| Cadastro e ordem complementar | Atacar as exceções 2, 5 e 8 na origem; depende de três áreas |

## O que o grupo decide

Para o checkpoint 1, sábado às 12h
([`../../templates/checkpoint-1-diagnosis.md`](../../templates/checkpoint-1-diagnosis.md)):

1. Atender o pedido do CFO como veio, reenquadrá-lo ou atender uma parte e reenquadrar o resto.
   Com qual dado vocês sustentam a escolha?
2. Qual número o projeto vai mover, qual é o valor atual e como medir com uma variação mensal tão
   grande?
3. O atraso de setembro caiu porque o controller e uma equipe dedicada passaram uma semana pondo
   os vencidos em dia. O que acontece com o atraso quando essa força-tarefa sai? Quanto essa
   semana custou? Qual número usar como linha de base?
4. Em que ordem atacar as frentes, por retorno, prazo até o primeiro valor e esforço? Em quanto
   tempo o cliente sente o primeiro ganho?
5. Quem decide, quem paga e quem é afetado? Como vocês levam a conversa ao CFO?

---

A Já Chegou é uma empresa fictícia. Os números partem de projetos reais da Barte, com volumes
alterados.
