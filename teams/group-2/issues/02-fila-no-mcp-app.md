# Como analista, quero ver e decidir a fila numa tela dentro do chat

> Grupo 2 · domingo, 15/11. Empilhada sobre a issue 01 (PR #3, branch `group-2/decisao-no-claude`).
> Recorte mínimo para a demo do pitch.

## Objetivo

A fila de propostas aparece como uma tela dentro da conversa (um MCP App), e não só como texto.
O analista vê a tabela, abre uma proposta e clica em aprovar ou alterar a ação na doca. O clique
chama a mesma tool `decidir` do `ja-chegou-analista`, com as mesmas travas: a tela não decide nada
sozinha e não tem regra própria.

## O que muda

- No `mcp_server/analista.py`, uma tool nova, `mostrar_fila`, que devolve a fila (os mesmos dados de
  `listar_fila`) e aponta, no `_meta` da tool, para um recurso de UI (`ui://ja-chegou-analista/fila`).
- O recurso de UI é um HTML único (`mcp_server/ui/fila.html`), servido pelo servidor com o tipo de
  MCP App. Ele mostra:
  - a tabela da fila: nota, fornecedor, classificação, ação na doca proposta, encaminhamento e
    valor em risco, com o total no topo;
  - ao clicar numa linha, a proposta com a evidência (dados de `ler_proposta`);
  - os botões **Aprovar** e **Alterar ação** (com a ação nova e a justificativa), que chamam
    `decidir` pelo host. Se a tool recusar, a tela mostra o erro dela, sem contornar.
- A skill `decidir-fila` passa a abrir a fila com `mostrar_fila` quando o host mostra MCP Apps, e
  continua com `listar_fila` em texto quando não mostra.

## Critérios de aceite

- [ ] AC-1: `mostrar_fila` devolve os dados da fila e declara o recurso de UI; num host sem MCP Apps,
      o resultado em texto continua legível.
- [ ] AC-2: a tela só chama `ler_proposta` e `decidir`; nenhum número é calculado nela.
- [ ] AC-3: uma recusa de `decidir` aparece na tela com a mensagem da tool.
- [ ] AC-4: testes cobrem que `mostrar_fila` declara o recurso, que o recurso é servido com o tipo
      certo e que o HTML não traz chamada a outra tool.
- [ ] AC-5: `make check` passa (a falha antiga de `test_suite_do_script_passa` no Windows segue de fora).

## Para a demo

O Claude Code no terminal não desenha MCP Apps. A demo usa um host que desenha (o Claude Desktop, com
o servidor local configurado). O README do grupo diz como ligar.

## Fica para depois

Ordenação e filtros na tela, delegação ao motor pela tela, publicação na Cloudflare.
