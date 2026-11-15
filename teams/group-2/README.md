# Grupo 2

- **Nome do grupo:** Grupo 2
- **Integrantes:** Bruno Filho, Daniel Rivelino, Danillo Andrade, Leonardo Helal e Marcelo Calazans (PM)
- **Fork líder:** https://github.com/bruno-filho/formacao-fde-case
- **Contas:** a preencher (organização no Supabase e conta na Cloudflare; veja [CONTAS.md](../CONTAS.md))

> O código do servidor `ja-chegou-analista` (`mcp_server/analista.py`, a tela `mcp_server/ui/fila.html`, a skill `decidir-fila` e os testes) está no fork líder, na `main`. Esta pasta traz a entrega do grupo.

## Como ler esta entrega

Para o time da Barte e para os agentes de revisão. Leia nesta ordem:

1. **O artefato da entrega (comece por aqui):** [Plano do Grupo 2](https://claude.ai/artifact/KvAVTnMfaHMr1JdGcMo6e3). Mostra o que foi entregue, por quem e onde, como foi o domingo e como o agente do Grupo 2 se integra com o motor do Grupo 1 e o dossiê do Grupo 3.
2. **Os slides do pitch (suporte):** [Pitch Grupo 2 · Já Chegou](https://claude.ai/artifact/BfXML4crgrD4QUeCtAgB8r). O problema, o número, a solução, a demo, o eval e os próximos passos. O texto do roteiro está em [`sunday-pitch.md`](sunday-pitch.md).
3. **O vídeo da demo (o fluxo completo):** [`video-demo/demo-fila-analista.mp4`](video-demo/demo-fila-analista.mp4), 36 s, sem áudio. O analista vê a fila de 34 notas, abre a NF-035, aprova com motivo (a fila cai para 33) e esbarra nas travas de alçada. Os números vêm das tools do servidor; a conversa é uma reconstrução animada.

Os links do claude.ai exigem login na organização. Se um agente de revisão não conseguir abri-los, o mesmo conteúdo está nos arquivos desta pasta:

| O que | Arquivo |
| --- | --- |
| Diagnóstico do checkpoint 1 | [`checkpoint-1-diagnosis.md`](checkpoint-1-diagnosis.md) |
| Pitch de domingo | [`sunday-pitch.md`](sunday-pitch.md) |
| Roteiro da demo ao vivo | [`roteiro-demo.md`](roteiro-demo.md) |
| Eval das travas, 48 de 48 | [`eval.md`](eval.md) |
| As issues do agente | [`issues/`](issues/) |
| Mock do motor do Grupo 1, 13 casos | [`motor-mock/`](motor-mock/) |
| Vídeo e a fonte em Remotion | [`video-demo/`](video-demo/) |

**O código final e o teste técnico ficam com o time da Barte.** O servidor `ja-chegou-analista` (`mcp_server/analista.py`, a tela `mcp_server/ui/fila.html`, a skill `.claude/skills/decidir-fila/` e os testes `tests/test_analista.py` e `tests/test_fila_app.py`) está na `main` do fork líder, onde `make check` dá 111 testes passando e 3 pulados.

## A fila como MCP App (issue 02)

O Claude Code no terminal não desenha MCP Apps. Para ver a fila como tela, use um host que desenha, como o
Claude Desktop, com o servidor local no `claude_desktop_config.json` (troque o caminho pelo do seu clone):

```json
{
  "mcpServers": {
    "ja-chegou-analista": {
      "command": "uv",
      "args": ["run", "--directory", "/caminho/do/clone", "python", "mcp_server/analista.py"],
      "env": {"FDE_ANALISTA_ID": "analista-1", "FDE_ANALISTA_NIVEL": "analista"}
    }
  }
}
```

Reinicie o Claude Desktop e peça "mostra a minha fila na tela". A tool `mostrar_fila` abre a tela; os botões
chamam `decidir` com as mesmas travas.
