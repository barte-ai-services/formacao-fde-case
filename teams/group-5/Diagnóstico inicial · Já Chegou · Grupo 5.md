# Diagnóstico inicial · Já Chegou · Grupo 5

Nov 14, 2026 · @Augusto Frazão

## Resumo

O CFO pediu para automatizar boletos e parar de pagar R$ 122 mil por mês em juros. O diagnóstico encontrou um segundo problema, três a quatro vezes maior: R$ 386 a 543 mil por mês pagos errado, sem mercadoria correspondente.

Os dois nascem no mesmo ponto. Só 0,45% das notas casam sozinhas com o pedido, então quase tudo vai para conferência manual. A fila atrasa o pagamento e gera os juros. E como ninguém confronta nota, pedido e recebimento antes do aceite, o erro passa e não volta.

A proposta é uma tratativa só, em fases: começar pelo que derruba os juros, que é a dor declarada, e usar a mesma camada de validação para medir e depois bloquear o pagar errado.

## Os dois problemas em números

|  | Pagar atrasado (dor declarada) | Pagar errado (achado do diagnóstico) |
| --- | --- | --- |
| Perda por mês | R$ 122 mil em juros e multas | R$ 543 mil com abril, R$ 386 mil sem abril |
| Variação | R$ 23 mil a R$ 420 mil | Nunca abaixo de R$ 136 mil |
| Peso nas perdas (R$ 665 mil/mês) | 18% | 82% |
| Reversível? | Sim, pagando no prazo | Não: aceitar a nota é aceitar o pedido, e nada foi recuperado de fornecedores |
| O cliente enxerga? | Sim, o CFO já levou ao conselho | Em parte: na reunião citaram R$ 440 mil e 10% recuperado; o dossiê mostra R$ 543 mil e zero |
| Fonte | Dossiê (Pack 2) | Dossiê (Pack 2) |

A soma, R$ 665 mil por mês, é 14,8 vezes o custo do time de contas a pagar (R$ 45 mil).

**Ressalva sobre duplicidade.** Os 45% vêm do raio-X das 80 notas, uma base sintética com 9 notas por tipo de exceção. Ela prova que o mecanismo existe, não mede frequência. No cliente real, a quebra do pagar errado por tipo ainda é pergunta aberta ao controller. Por isso este diagnóstico não afirma que duplicidade é 40% ou 45% do problema.

## Causa raiz

O problema não é o boleto nem o caixa: é a conferência da nota.

- **A fila gera os juros.** São 11,4 mil notas por mês para 5 analistas, cerca de 4 minutos por nota. Quando o controller fez uma semana de força-tarefa, o valor pago em atraso caiu de 76% para 16%. Se faltasse caixa, mais gente conferindo não teria resolvido.
- **A maior parte da fila é ruído de formato.** As divergências reais estimadas ficam perto de 11% das notas, mas 99% caem em conferência manual. O resto falha por caixa × unidade, tolerância de centavos ou pedido sem referência.
- **O pagar errado passa antes do pagamento.** A nota quase sempre chega antes da mercadoria, mas ninguém olha antes da doca. O CFO aprova todos os pagamentos e mesmo assim a perda continua: ele confere o pagamento, não a nota.

## Caminho proposto: uma tratativa, três fases

A fase 1 mira os juros, não a duplicidade. Bloquear duplicidade reduz o pagar errado, mas não esvazia a fila, então não move o número que o CFO cobra.

1. **Fase 1 · Match técnico (semanas 1 e 2).** O validador resolve sozinho o que é só formato: conversão de unidade pelo cadastro, tolerância de valor, pedido encontrado sem referência. Roda só em leitura, em modo proposta. Meta: tirar da fila as notas corretas para que cheguem ao pagamento antes do vencimento. Indicador: % do valor pago em atraso (base 41%) e juros (base R$ 122 mil).
2. **Fase 2 · Medir o pagar errado.** A mesma camada já cruza nota, pedido, recebimento e notas lançadas. Sem bloquear nada, ela passa a reportar o que teria barrado, por tipo. Isso entrega o número real de duplicidade, falta física e nota sem ordem, que hoje ninguém tem.
3. **Fase 3 · Bloquear antes do aceite.** Com a quebra por tipo em mãos, o CFO decide o que vira bloqueio. Duplicidade é a candidata natural a entrar primeiro: regra simples e perda de 100% do valor da nota.

Se o controller confirmar que duplicidade pesa muito no real, o bloqueio pode subir para a fase 1 sem mudar a arquitetura.

## Solução: camada de validação antes do aceite

Cada nota é cruzada com o pedido de compra, a contagem da doca, as notas já lançadas e os pagamentos avulsos, assim que chega pela SEFAZ ou por e-mail.

| Resultado | Quando | O que acontece |
| --- | --- | --- |
| Verde | Bate, ou a diferença é só de formato ou está dentro da tolerância | Segue para lançamento sem conferência manual |
| Amarelo | Divergência real: falta física, quantidade menor, item trocado, nota sem ordem | Vai para a alçada certa (analista, coordenação ou diretoria) com prazo para resolver |
| Vermelho | Duplicidade ou fornecedor bloqueado | Não é lançada até alguém liberar |

**Ajuste em relação à discussão do grupo.** Falamos em cruzar antes do lançamento do pagamento. O ponto certo é antes do aceite da nota, na doca: para o jurídico do cliente, aceitar a nota é aceitar o pedido, e depois disso não há devolução.

No raio-X das 80 notas, cada fonte pegou um tipo de exceção que as outras não pegam. Comparar só o número da nota deixaria passar 4 das 9 duplicidades, que são reemissões com outro número. Fazer com fornecedor externo ou produto interno ainda está em aberto.

## Como abrir a segunda reunião

Começar pelo pedido dele e deixar o problema maior aparecer como descoberta, com a escolha na mão do CFO.

1. **Confirmar a dor.** "Na semana de força-tarefa, o atraso caiu de 76% para 16%. Os juros vêm da fila de conferência, não do caixa nem do boleto."
2. **Mostrar a fase 1.** Tirar da fila o que é só formato, em leitura, sem mexer no ERP.
3. **Testar a abertura.** "Cruzando os dados, apareceu um valor de três a quatro vezes os juros em pagamentos sem mercadoria correspondente. Faz sentido a gente medir isso junto, na mesma solução?"
4. **Parar e ouvir.** A resposta diz se ele não conhecia o tamanho ou se conhece e não quer visibilidade.

Cuidados: o cliente já citou R$ 440 mil na primeira reunião, então o tema não é surpresa total; a novidade é o tamanho e o zero de recuperação. Apresentar como oportunidade de processo, não como falha do controle dele. E falar em fases de uma tratativa, nunca em dois projetos.

## O que ainda não sabemos

| Pergunta | O que muda | Quem responde |
| --- | --- | --- |
| Quanto do pagar errado é duplicidade, falta física ou quantidade menor? | Se o bloqueio de duplicidade sobe para a fase 1 | Controller |
| O que aconteceu em abril (R$ 1,4 mi acima do normal)? | Se a base é R$ 386 mil ou R$ 543 mil | Controller |
| Quantas divergências são só de unidade ou formato? | O tamanho do ganho da fase 1 | Controller e compras |
| Como os juros são apurados? | A confiança na base de R$ 122 mil, que é só 0,85% do valor pago em atraso | Controller |
| O CFO conhece o tamanho do pagar errado? | O tom da segunda reunião | A própria reunião |

**Bloqueios da primeira entrega:** a credencial da SEFAZ está no login pessoal de um analista terceirizado; a homologação do ERP é uma cópia de março; o usuário de leitura no ERP não tem previsão; e falta definir onde a solução roda (dados fiscais no Brasil e contrato de operador de dados).

Fontes: dossiê do cliente (Pack 2), transcrição da primeira reunião, raio-X das 80 notas da pasta `dados/` e discussão do grupo de 14/11. A Já Chegou é uma empresa fictícia do caso.
