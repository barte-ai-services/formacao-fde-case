# Grupo 2

- **Nome do grupo:** Grupo 2
- **Integrantes:** Bruno Filho, Daniel Rivelino, Danillo Andrade, Leonardo Helal e Marcelo Calazans (PM)
- **Fork líder:** https://github.com/bruno-filho/formacao-fde-case
- **Contas:** a preencher (organização no Supabase e conta na Cloudflare; veja [CONTAS.md](../CONTAS.md))

> O código do servidor `ja-chegou-analista` (`mcp_server/analista.py`, a tela `mcp_server/ui/fila.html`, a skill `decidir-fila` e os testes) está no fork líder, na `main`. Esta pasta traz a entrega do grupo.

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
