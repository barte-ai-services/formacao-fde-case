# Eval das travas do `ja-chegou-analista`

> Grupo 2 · 15/11. Prova, para o bloco Eval do pitch, de que as travas do servidor do analista estão no
> sistema e não só no prompt. Tudo aqui é resultado de teste rodado na `main`; nenhum teste foi escrito
> ou mudado para este documento.

Fontes: a issue [`01-decisao-no-claude.md`](issues/01-decisao-no-claude.md), o servidor
`mcp_server/analista.py`, os testes `tests/test_analista.py` e `tests/test_subagente.py`, e o mock do
motor em [`motor-mock/`](motor-mock/).

## Como reproduzir

```bash
uv run pytest tests/test_analista.py -v
uv run pytest tests/test_subagente.py -v -k "analista or decidir_fila"
uv run pytest teams/group-2/motor-mock -v
```

Resultado em 15/11: **33 de 33** em `test_analista.py`, **2 de 2** das travas do subagente em
`test_subagente.py` e **13 de 13** no mock do motor. Nenhuma falha.

## As travas do servidor

Os testes de `tests/test_analista.py` rodam offline, sobre a base real, com um arquivo de propostas
sintético que tem um caso de cada tipo (analista, coordenação, diretoria por fornecedor bloqueado,
bloqueio E6, regra, proposta recusada, proposta repetida).

| # | Trava (em português simples) | Teste que prova | Resultado |
|---|---|---|---|
| 1 | O nível de cada nota é recalculado pela régua e só sobe: uma proposta que o arquivo manda para `regra` entra na fila como `analista` se a régua pedir. | `test_encaminhamento_abaixo_da_regua_entra_com_o_minimo` | ✅ passou |
| 2 | Os dois servidores (`ja-chegou` e `ja-chegou-analista`) usam a mesma régua, sem cópia da lógica. | `test_os_dois_servidores_usam_a_mesma_regua` | ✅ passou |
| 3 | O filtro de nível não amplia a alçada: pedir `coordenacao` ou `diretoria` não mostra o que está acima do nível de quem decide. | `test_filtro_de_nivel_nao_amplia_acima_do_ambiente` | ✅ passou |
| 4 | Diretoria, bloqueio, regra e propostas recusadas ficam fora da fila. | `test_fila_deixa_fora_coordenacao_diretoria_bloqueio_regra_e_recusada` | ✅ passou |
| 5 | Diretoria nunca é decidida pelo servidor, nem por quem é coordenação (fornecedor bloqueado vira diretoria). | `test_decidir_recusa_sem_gravar[diretoria]`, `[diretoria_para_coordenacao]` | ✅ passou |
| 6 | Bloqueio (E6) nunca é decidido pelo servidor, nem por coordenação. | `test_decidir_recusa_sem_gravar[bloqueio]` | ✅ passou |
| 7 | Quem é analista não decide nota que a régua manda para coordenação. | `test_decidir_recusa_sem_gravar[acima_do_nivel]`; pelo cliente MCP, `test_servidor_mcp_expoe_as_tools_e_trava_a_alcada` | ✅ passou |
| 8 | Um nível de ambiente inválido (ex.: `FDE_ANALISTA_NIVEL=diretoria`) não decide nada. | `test_decidir_recusa_sem_gravar[nivel_do_ambiente_invalido]` | ✅ passou |
| 9 | Cada proposta é decidida uma vez: a decidida sai da fila e a segunda decisão é recusada. | `test_decidida_sai_da_fila_e_nao_aceita_segunda` | ✅ passou |
| 10 | Toda recusa devolve `gravada: false` com o motivo e não grava nada em `decisoes.jsonl`. São 14 casos: sem `FDE_ANALISTA_ID`, nota inexistente, nota sem proposta, acima do nível, diretoria (2), bloqueio, regra, proposta recusada, nível de ambiente inválido, decisão fora de `aprovar`/`alterar`, `alterar` sem ação, `alterar` com ação inválida, justificativa com menos de 10 caracteres. | `test_decidir_recusa_sem_gravar[*]` (14 parâmetros) | ✅ 14 de 14 |
| 11 | A decisão gravada traz quem decidiu, o nível dele, o nível da nota, a ação final e a proposta, a justificativa e a hora. | `test_decidir_grava_a_linha` | ✅ passou |
| 12 | Delegar ao motor é sempre simulação: grava só o pedido com `dry_run: true`, não grava decisão e nada sai da fila. | `test_delegar_ao_motor_so_grava_o_pedido` | ✅ passou |
| 13 | A simulação respeita a alçada e exige quem pede: coordenação não entra na simulação do analista e sem `FDE_ANALISTA_ID` nada é gravado. | `test_delegar_ao_motor_com_filtros_e_sem_id` | ✅ passou |
| 14 | O servidor expõe só as quatro tools previstas, e a trava vale chamando pelo protocolo MCP, não só pela função Python. | `test_servidor_mcp_expoe_as_tools_e_trava_a_alcada` | ✅ passou |
| 15 | O subagente `auditor-de-notas` não ganha tool de decisão: só tem `mcp__ja-chegou__*`, não carrega a skill `decidir-fila` e nem cita o `ja-chegou-analista`. | `tests/test_subagente.py::test_agente_nao_alcanca_o_servidor_do_analista` | ✅ passou |
| 16 | A skill `decidir-fila` escreve o que a sessão nunca faz: inventar número, decidir sem o analista pedir, contornar uma recusa. | `tests/test_subagente.py::test_skill_decidir_fila_diz_o_que_a_sessao_nunca_faz` | ✅ passou |

Os outros testes de `test_analista.py` cobrem o caminho feliz (ordem da fila por valor em risco,
coordenação vendo a própria fila, filtro por destino, campos da linha, fallback para o baseline,
`ler_proposta`, `alterar` e `alterar` para a mesma ação virando `aprovar`) e passaram todos.

## Os 13 casos do mock do motor

O mock em `teams/group-2/motor-mock/` simula o motor de decisão do grupo 1 sobre
`propostas_exemplo.json`. Diferente do `delegar_ao_motor` do servidor (sempre simulação), o mock
também tem o modo real, em que aprova; por isso os casos provam onde ele para.

| # | Caso | Teste | Resultado |
|---|---|---|---|
| 1 | Aprova só o que está dentro dos critérios, com confiança de pelo menos 0,98. | `test_aprova_dentro_dos_criterios` | ✅ passou |
| 2 | Abaixo da confiança, devolve para a fila com recomendação. | `test_devolve_a_fila_abaixo_da_confianca_com_recomendacao` | ✅ passou |
| 3 | Fora dos critérios (valor acima do teto, E5) volta para a pessoa. | `test_fora_dos_criterios_volta_para_a_pessoa` | ✅ passou |
| 4 | Diretoria e bloqueio ficam fora do motor e não são decididos. | `test_diretoria_e_bloqueio_ficam_fora_do_motor` | ✅ passou |
| 5 | Se o classificador falha, a nota segue para a pessoa com "Revisar". | `test_falha_do_clef_segue_para_a_pessoa` | ✅ passou |
| 6 | Proposta já decidida não é reavaliada. | `test_proposta_ja_decidida_nao_e_reavaliada` | ✅ passou |
| 7 | A aprovação registra motor, confiança, versão do modelo e a delegação. | `test_aprovacao_registra_motor_confianca_e_versao` | ✅ passou |
| 8 | Simulação não aprova nada, só mostra o que aprovaria. | `test_simulacao_nao_aprova_nada` | ✅ passou |
| 9 | Com a delegação desligada para o nível, só simula. | `test_delegacao_desligada_so_simula` | ✅ passou |
| 10 | Motor desligado mostra "Motor indisponível" e não grava decisão. | `test_motor_desligado_mostra_indisponivel` | ✅ passou |
| 11 | Delegar duas vezes não aprova duas vezes. | `test_delegar_duas_vezes_nao_aprova_duas_vezes` | ✅ passou |
| 12 | O filtro por exceção só considera a classificação pedida. | `test_filtro_por_excecao` | ✅ passou |
| 13 | Os totais do relatório batem com as linhas. | `test_totais_batem_com_as_linhas` | ✅ passou |

## Em três linhas

- **Contra o que avaliamos:** 33 testes offline do `ja-chegou-analista` sobre a base real com propostas sintéticas de cada tipo (inclusive pelo cliente MCP), 2 testes do isolamento do subagente e da skill, e 13 casos do mock do motor.
- **Resultado:** 48 de 48 passaram; as 14 tentativas de decidir fora da regra ou da alçada foram recusadas sem gravar, e nenhuma delegação gravou decisão.
- **Onde o agente ainda pode errar:** a identidade e o nível vêm do ambiente sem login (quem põe `FDE_ANALISTA_NIVEL=coordenacao` decide coordenação); não há trava contra duas sessões decidindo a mesma nota ao mesmo tempo; e o que o modelo escreve (o resumo da divergência, a justificativa, chamar `decidir` só quando o analista pede) só é guiado pela skill, sem eval do modelo de ponta a ponta.
