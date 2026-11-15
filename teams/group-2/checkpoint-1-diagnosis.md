# Checkpoint 1: diagnóstico e prioridade

> **Momento:** checkpoint 1, sábado, 14/11, depois do roleplay e do dossiê.
>
> **Onde entregar:** no fork do líder do grupo, em `teams/group-2/checkpoint-1-diagnosis.md`, por pull request.
>
> **Fontes usadas:** "Dossiê" é o dossiê pós-reunião do Pack 2 (fonte principal dos números, medidos de jan a set); "Gemini hh:mm:ss" é o minuto da reunião de sábado no resumo do Gemini (fonte do que foi dito); "Briefing" é o briefing do Pack 1; "Suposição do grupo" é conta ou inferência nossa, ainda sem dado do cliente.

---

## Grupo

- Grupo: Grupo 2
- Integrantes: Bruno Filho, Daniel Rivelino, Danillo Andrade, Leonardo Helal e Marcelo Calazans (PM)

## 1. O problema

- O que o cliente disse que é o problema: o contas a pagar lança, paga e baixa cerca de 400 boletos por dia à mão, e a empresa paga juros e multa por atraso. "Contratei para automatizar o boleto" (CFO, Dossiê; Gemini 00:19:59, 00:21:20).
- O que o grupo entende que é o problema: o recebimento do CD só tem duas saídas, aceitar ou recusar a carga inteira, e aceita para não haver ruptura. Ao aceitar, a Já Chegou assume a nota como veio, com item a mais ou a menos: para o jurídico, "aceitar a nota é aceitar o pedido" (Dossiê). O erro é do fornecedor, mas a conta e o retrabalho ficam com a Já Chegou, e a divergência só aparece na doca, quando já não há tempo de resolver na origem. A correção manual depois do aceite segura o pagamento e gera os juros que o CFO quer eliminar.
- Onde, no caminho do pedido de compra até o pagamento, ele aparece: no recebimento do CD, que confere a nota física só na hora de descarregar, sem validação no sistema (Gemini 00:04:15), e decide entre aceitar ou recusar tudo (Gemini 00:05:58). Depois, na conferência e correção manual, que leva 14 dias da nota ao lançamento no CD e segura o pagamento (Dossiê, Anexo 3).
- Quem sente a dor (por papel: CFO, controller, compras, outro): CFO (juros, margem e aprovação de cada pagamento), controller e os 5 analistas terceirizados (fila manual, provisão no fechamento), compras (doca sem aviso, ruptura quando o fornecedor bloqueia entrega).
- Evidência (dossiê ou reunião): 41% do valor é pago depois do vencimento, com R$ 122 mil por mês de juros e multa (Dossiê, Anexos 2 e 3). Em janeiro, 76% do valor saiu depois do vencimento (Dossiê, Anexo 3). Pagar errado custa R$ 543 mil por mês, e o recuperado é zero em todos os meses (Dossiê, Anexos 2 e 3). Só 0,7% das notas do CD batem sozinhas com a ordem (Dossiê, Anexo 3).

## 2. O número a mover

### Qual perda

- [x] Pagar errado
- [ ] Pagar atrasado
- [ ] Ruptura de estoque
- [ ] Custo de operar

### Baseline e meta

| Campo | Valor | Fonte |
| --- | --- | --- |
| Indicador (como a perda é medida) | P1: pago sem mercadoria correspondente, menos o recuperado, em R$ e como taxa sobre o valor das notas | Dossiê, Anexo 2 |
| Baseline (valor hoje) | R$ 543 mil por mês, ou 1,56% dos R$ 34,8 milhões em notas; recuperado zero | Dossiê, Anexos 1 a 3; taxa é conta do grupo |
| Período do baseline | Média de jan a set, com faixa de R$ 136 mil a R$ 1,8 milhão; abril concentrou quase 40% do período | Dossiê, Anexo 2 |
| Quem assina o baseline | Controller, dono do processo, e CFO, antes de mudar qualquer coisa | A combinar |
| Meta | Reduzir em 50% a perda líquida (pago sem mercadoria menos o recuperado do fornecedor), sem a ruptura passar de 1,2 ponto e sem mudar a regra de aceitar a carga | Suposição do grupo; ruptura em Dossiê, Anexo 2 |
| Prazo da meta | Quick win até a semana 4, com o ajuste de cada nota registrado; meta cheia de P1 em 8 semanas | Dossiê; Briefing |
| Indicador do quick win | Valor pago depois do vencimento: baseline de 41%, com R$ 122 mil por mês de juros e multa. Meta: reduzir 90% dos atrasos até a semana 4, para cerca de 4% do valor e cerca de R$ 12 mil por mês de juros | Baseline no Dossiê, Anexos 2 e 3; meta é projeção do grupo, a validar no piloto |

- Por que esta perda, e não as outras três: P1 é 4,5 vezes os juros (R$ 543 mil contra R$ 122 mil por mês) (Dossiê, Anexo 2). Ela também puxa o atraso: toda nota aceita com divergência exige correção manual antes de pagar, o que trava a aprovação e gera juros (Gemini 00:21:20, 00:29:52). Ruptura fica como limite da meta, não como alvo. Juros entram como o indicador do quick win porque são a dor que o CFO trouxe e a métrica que ele acompanha.
- Como medir apesar da variação mensal: em taxa (P1 sobre o valor das notas e percentual pago depois do vencimento), em média móvel, e separando abril e setembro. Setembro não serve de baseline para atraso: os 16% vieram de uma semana de força-tarefa do controller, e o processo não mudou (Dossiê).

## 3. A prioridade

| Frente | Perda que move | Retorno | Tempo até o primeiro valor (5 = mais rápido) | Esforço (5 = menor esforço) | Total | Depende de | Confiança |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Escuta e check antecipado das notas do CD: capturar a nota na SEFAZ assim que é emitida, cruzar com os pedidos vigentes, ajustar o pedido automaticamente quando há divergência e registrar o ajuste. O CFO recebe a fila pronta por vencimento, com alertas. Notas sem pedido ficam em análise manual | P2 (juros) e P1 | 5 | 5 | 4 | 14 | CSV diário de títulos (liberado), credencial de serviço na captura de NF, leitura e escrita de pedidos no ERP, com homologação atualizada | Alta |
| B. Cobrar formalmente do fornecedor a diferença registrada (abatimento na nota seguinte), no lugar da negociação verbal | P1 | 4 | 3 | 3 | 10 | O registro da diferença feito pela frente A e a regra do jurídico | Baixa: o recuperado hoje é zero |
| C. Corrigir o cadastro de conversão caixa × unidade, que gera divergência | P1 | 3 | 2 | 3 | 8 | Cadastro por planilha e WMS que não converte unidade | Média |
| D. Automatizar o lançamento de boletos, o pagamento e a baixa no ERP | P2 e P4 | 2 | 3 | 2 | 7 | API do banco, que não existe, e escrita no ERP | Baixa |

- Frente escolhida para começar: A, como quick win, atacando primeiro a dor do CFO: pagar em dia e parar de pagar juros. O quick win escuta as notas na SEFAZ, cruza cada uma com os pedidos vigentes e ajusta o pedido automaticamente quando há divergência, para os sistemas refletirem a realidade. O CFO recebe a fila pronta por vencimento, com alertas, e só aprova. Notas sem pedido ficam em análise manual: até 10%, segundo a reunião; cerca de 4%, segundo o Dossiê (Anexo 3). A regra de aceitar ou recusar a carga não muda: muda o momento em que a divergência é descoberta, da doca para a emissão da nota.
- Resultado esperado do quick win: 90% menos pagamentos atrasados. O valor pago depois do vencimento cai de 41% para cerca de 4%, e os juros e multa de R$ 122 mil para cerca de R$ 12 mil por mês, cerca de R$ 1,3 milhão em 12 meses. É projeção do grupo, a validar no piloto: assume que os juros caem na mesma proporção dos atrasos (ver H6).
- Por quê: entra pelo objetivo principal do CFO, que é parar de pagar juros (Gemini 00:21:20, 00:29:52; Dossiê). Hoje 41% do valor sai depois do vencimento, a conferência manual leva 14 dias da nota ao lançamento no CD e só 0,7% das notas do CD batem sozinhas com a ordem (Dossiê, Anexo 3). Com o pedido já ajustado quando a carga é aceita, a nota não fica parada e é paga em dia. Ao mesmo tempo, o registro de cada ajuste vira a base para cobrar o fornecedor e atacar os R$ 543 mil de P1. Não depende de integração bancária nem de mudar a regra de recebimento: usa a nota que a captura de NF já busca na SEFAZ, os pedidos do ERP e o CSV diário de títulos, já liberado (Dossiê, Anexo 6). A nota quase sempre chega antes da mercadoria (Dossiê), e o pagamento sai em média em 45 dias (Gemini 00:15:36), então há folga para ajustar antes de vencer. A principal dependência é a escrita no ERP: hoje nada escreve sem homologação, e a atual é uma cópia de março (Dossiê, Anexo 6).
- O que fica para depois, e por quê: o quick win abre caminho para as frentes mais robustas, nesta ordem.
  - **Semanas 1 a 4 (quick win):** semana 1, conectar a escuta à captura de NF, ler pedidos e títulos, rodar em sombra e fechar o baseline; semana 2, cruzar nota × pedido e testar em notas já lançadas; semana 3, ligar o ajuste automático do pedido, primeiro em homologação, e montar a fila do CFO por vencimento com alertas; semana 4, piloto no CD. O relatório semanal ao CFO mostra o valor pago depois do vencimento, os juros e os ajustes registrados.
  - **Semanas 5 a 8:** B, com a cobrança formal da diferença registrada, e o check entrando no fluxo de aprovação, incluindo o bloqueio de pagamento duplicado (Gemini 00:07:47; Dossiê, Anexo 4). C entra se a H1 se confirmar.
  - **Depois das 8 semanas:** D, porque o banco não tem API (Dossiê, Anexo 6) e automatizar antes só acelera um pagamento que pode estar errado. O processo de notas de devolução também fica para depois, sem detalhar agora: muda a regra de recebimento, o que já foi tentado e não andou (Gemini 00:18:22, 00:43:06). É a maior oportunidade seguinte: o quick win paga em dia, mas paga a nota como veio, e hoje são R$ 543 mil por mês pagos sem mercadoria correspondente (Dossiê, Anexo 2).

## 4. A reformulação do pedido do CFO

| | Texto |
| --- | --- |
| O pedido, como o CFO trouxe | Automatizar lançar, pagar e baixar os boletos sem digitação, e parar de pagar juros e multa (Briefing; Dossiê). |
| O pedido, como o grupo propõe | Parar de descobrir o erro do fornecedor na doca: conferir nota × pedido assim que a nota é emitida, para que a nota aceita já chegue com o pedido ajustado e seja paga em dia, e a diferença fique registrada para cobrar do fornecedor. A regra de aceitar a carga continua. |
| Por que a mudança move mais o número | A correção manual feita depois do aceite é o que segura o pagamento e gera juros: antecipá-la ataca os juros e, ao mesmo tempo, P1, que vale 4,5 vezes mais (R$ 543 mil contra R$ 122 mil por mês). Abrindo a perda em ramos, o pedido como veio cobre P2 e P4: R$ 167 mil de R$ 710 mil por mês. |
| Como o grupo vai apresentar isso ao CFO | Começar pela dor dele, com o número dele: R$ 122 mil por mês de juros e 41% do valor pago depois do vencimento. O quick win em até 4 semanas corta 90% dos pagamentos atrasados (projeção do grupo): de 41% para cerca de 4% do valor, e de R$ 122 mil para cerca de R$ 12 mil por mês em juros. Ele acompanha isso num relatório semanal, junto com os ajustes registrados, sem mexer na regra de recebimento que protege contra a ruptura. Depois, mostrar os R$ 543 mil pagos sem mercadoria correspondente, que nunca voltam. |

## 5. Hipóteses e o que falta saber

### Hipóteses

| # | Hipótese | Como confirmar | Se estiver errada, o que muda |
| --- | --- | --- | --- |
| H1 | Parte relevante da divergência no CD é erro de conversão caixa × unidade, já que o WMS não converte (Dossiê) | Classificar uma amostra de notas do CD nas exceções 1 a 8 do Dossiê (Anexo 4) | A frente C perde força e o foco fica no check e na cobrança |
| H2 | A maior parte dos juros vem de notas paradas na conferência e na correção manual (14 dias até o lançamento no CD) | Cruzar os títulos pagos com atraso, do CSV diário, com os dias da nota até o lançamento | Se o atraso vier da fila de boletos ou do saldo, o quick win se apoia na fila por vencimento e a frente D sobe na prioridade |
| H3 | Avisar compras antes do caminhão não aumenta a ruptura (1,2 ponto hoje) | Piloto com poucos fornecedores do CD, acompanhando a ruptura | O check só alerta, e a diferença segue para a cobrança (B) |
| H4 | O ajuste feito na emissão da nota cabe no prazo médio de 45 dias, sem gerar atraso | Comparar a data de emissão e de recebimento no CD com o vencimento de cada nota | O quick win precisa priorizar as notas de vencimento curto |
| H5 | O atraso de setembro (16%) não se sustenta sem a força-tarefa | Acompanhar outubro e novembro no CSV diário de títulos | Se se sustentar, o baseline de juros do quick win precisa ser revisto |
| H6 | Os atrasos se distribuem de forma parecida entre as notas, então tirar 90% delas da fila manual corta cerca de 90% dos atrasos e dos juros | Cruzar os títulos pagos com atraso com as notas sem pedido e com o saldo do dia | A redução fica abaixo de 90%, e a análise manual precisa de prioridade por vencimento |

### O que falta saber

| # | Pergunta | Para quem (por papel) | Por que importa |
| --- | --- | --- | --- |
| Q1 | Quanto dos R$ 543 mil de P1 é do CD e quanto é das lojas? | Controller | O CD tem 1,9 mil notas e cerca de 64% do valor (Dossiê, Anexo 1); define o alcance do check |
| Q2 | Quanto custou a semana de força-tarefa de setembro, e o atraso de outubro já voltou a subir? | Controller e CFO | Define o baseline de juros do quick win |
| Q3 | Quando saem a credencial de serviço da captura de NF, o usuário de leitura no ERP, com o termo de confidencialidade, e a escrita de pedidos com homologação atualizada? | Controller e área fiscal | Hoje a credencial é o login de um analista terceirizado e a homologação é uma cópia de março; sem isso, o check e o ajuste automático não começam |
| Q4 | Quanto tempo leva a correção no ERP de uma nota aceita com divergência, e quem faz? | Controller | Se for o que atrasa o pagamento, é onde o quick win reduz juros |
| Q5 | O fornecedor aceita cancelar e reemitir a nota antes da entrega, ou dar abatimento na nota seguinte? | Compras | Define se a divergência vista antes do caminhão pode ser resolvida na origem ou só cobrada depois |
| Q6 | O jurídico aceita recusa parcial ou nota de devolução quando a divergência é vista antes da doca? | Controller, com o jurídico | Define se o aceite parcial pode sair do "depois das 8 semanas" |
| Q7 | Por que abril concentrou quase 40% de P1? | Controller | Um evento único, como um fornecedor ou um item, muda o baseline |

## 6. Quem decide, quem paga, quem sente e quem libera

| Papel | O que quer | Decide, paga, sente ou libera | Posição sobre o pedido | O que precisamos dele |
| --- | --- | --- | --- | --- |
| CFO, sponsor | Parar de pagar juros, fechar o mês mais cedo e controlar cada saída de caixa | Decide e paga; libera o banco | Apoia o pedido como veio e acha que o atraso já está caindo | Decisão sobre o reenquadramento e patrocínio |
| Controller | Fechar sem provisão gorda e com menos fila manual | Sente e libera: ERP, captura de NF, CSV de títulos, caixa de e-mail | Apoia, mas exige homologação e termo de confidencialidade por pessoa | Acessos e baseline assinado |
| Gerente de compras e comercial | Produto na prateleira, receber rápido, não romper | Sente e libera: agenda de doca, WMS, ordens por CSV | Neutro: "não quero briga com fornecedor bom", mas quer saber antes | Agenda de doca e piloto com fornecedores |
| Jurídico | Proteger a posição fiscal e contratual | Libera a regra de recusa e devolução | Hoje trava: "aceitar a nota é aceitar o pedido" | Regra para recusa parcial |
| Analistas do contas a pagar (terceirizados) | Menos trabalho manual | Sentem; um deles detém a credencial da SEFAZ | Neutros | Troca da credencial nominal por uma de serviço |

- Conflito principal: compras e comercial ganham quando a mercadoria entra, e o financeiro absorve o custo da divergência depois (Dossiê). O check antecipado reduz o conflito porque compras fica sabendo antes e decide na doca, sem brigar com o fornecedor depois.
- Quem arbitra: o CFO, como sponsor e dono do caixa. A confirmar se alguém acima dele resolve um impasse entre compras e financeiro.

## 7. Termos com sentidos diferentes

| Termo | Como um cargo usa | Como outro cargo usa | Onde isso pesa |
| --- | --- | --- | --- |
| Aprovado | CFO: aprovou o pagamento na lista do dia | Na prática, abaixo de R$ 5 mil ele "assina sem olhar" (Dossiê) | Aprovado não quer dizer conferido |
| Aceitar | Doca: deixar a carga entrar | Jurídico: aceitar a nota é aceitar o pedido | Aceitar na doca vira obrigação de pagar a nota cheia |
| Recebido | Doca e WMS: caixas descarregadas | Controller: quantidade conferida contra a nota e a ordem | O WMS não converte caixa em unidade |
| Atrasado | CFO: o atraso vem caindo (16% em setembro) | Dossiê: 41% do valor na média de jan a set | O baseline muda conforme o mês escolhido |
| Divergência | Compras: o que não bate na doca | Controller: o que vira ordem complementar, criada por três áreas | Ninguém soma a divergência num lugar só |
| Pedido ou ordem | Forecast: plano de compra | ERP: ordem, sendo 20% subida por CSV manual | Nota sem ordem (cerca de 4%) não tem dono |

## Conferência antes de entregar

- [x] Uma perda marcada, com baseline, meta e fonte.
- [x] Quatro frentes pontuadas e uma escolhida, com o porquê.
- [x] Pedido do CFO reformulado (ou mantido, com justificativa).
- [x] Pelo menos três hipóteses e três perguntas abertas.
- [x] Quem decide, quem paga e quem sente, com o conflito principal.
- [x] Termos com sentidos diferentes entre os cargos.
- [x] Nenhuma pessoa citada pelo nome: só pelo papel.
