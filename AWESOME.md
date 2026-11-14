# Awesome tools para builders

As ferramentas que um FDE da Barte usa para construir e entregar, com os links que valem a pena. Quase todas têm plano gratuito para começar, e várias têm um servidor MCP oficial, o que deixa o Claude Code operar a ferramenta por você.

## Onde estamos

O que o curso já tem e o que ainda falta, em 14/11/2026.

| Ferramenta | Instalada pela `setup-fde` | Papel na arquitetura de referência | Situação no curso |
|---|---|---|---|
| **Claude Code** | sim | o agente: constrói e roda | pronto, com o Ahrena configurado no repositório |
| **Ahrena Framework** | sim, os plugins | o time de agentes que constrói e revisa | pronto: Athena orquestra e Argos revisa |
| **git e GitHub (`gh`)** | sim | fork, PRs, issues e Actions | pronto |
| **Python (com `uv`)** | sim | linguagem do kit e das tools | pronto |
| **Supabase** | sim, o CLI | banco, autenticação e storage | CLI pronto; o líder de cada grupo cria a conta ([teams/CONTAS.md](teams/CONTAS.md)) |
| **Cloudflare** | sim, o Wrangler (com Node.js e npm) | o servidor MCP num Worker | Wrangler pronto; o líder de cada grupo cria a conta ([teams/CONTAS.md](teams/CONTAS.md)) |
| **Docker** | sim (Colima no Mac) | sobe o Supabase local | pronto |
| **Resend** | não | e-mail: avisar quem aprova | fora do curso; candidato para notificações |
| **Stripe** | não | pagamentos | fora do curso; o caso não cobra ninguém |
| **Evolution API** | não | WhatsApp: pedir a aprovação onde a pessoa está | fora do curso; exige servidor próprio |
| **Temporal** | não | fluxos longos: esperar a aprovação e retomar | fora do curso; o próximo passo quando o fluxo ficar longo |

A leitura: a stack de build e publicação (Claude Code, GitHub, Supabase, Cloudflare) está instalada e documentada. As outras quatro resolvem problemas que o caso vai encontrar logo depois do primeiro agente: avisar alguém (Resend, Evolution API), esperar uma resposta que demora dias (Temporal) e cobrar (Stripe). Nenhuma delas é pré-requisito para o fim de semana.

## Claude Code

O ambiente onde o trabalho acontece: lê o repositório, roda comandos, usa MCPs, skills e subagentes.

- [Documentação](https://code.claude.com/docs)
- [MCP no Claude Code](https://code.claude.com/docs/en/mcp): `claude mcp add` liga qualquer servidor desta lista
- [Skills](https://code.claude.com/docs/en/skills) e [subagentes](https://code.claude.com/docs/en/sub-agents): o formato do agente de domingo
- [Claude Code no GitHub Actions](https://github.com/anthropics/claude-code-action): o mesmo agente rodando num PR ou num cron
- [Claude Agent SDK](https://docs.claude.com/en/docs/agent-sdk/overview): quando o agente precisa virar um serviço

**Use quando:** sempre. É o ponto de partida de qualquer outra ferramenta daqui.

## Ahrena Framework

Regras, skills e agentes que transformam o Claude Code num time: a Athena planeja a issue e distribui o trabalho, os builders constroem camada a camada e o Argos revisa cada pull request antes do merge.

- [Repositório e instalação](https://github.com/ahrenatechnology/ahrena-framework)
- No curso, o `.claude/settings.json` já liga os plugins, e a skill `setup-fde` instala e confere. Para confirmar, abra uma sessão nova do Claude Code na pasta do case e rode `/agents`: a Athena precisa aparecer.

**Use quando:** o trabalho vira código que vai para produção: issue, plano, PRs revisados e merge na main.

## Supabase

Um banco Postgres que o Supabase mantém por você, com autenticação, storage, funções e uma API pronta em cima das tabelas.

- [Documentação](https://supabase.com/docs)
- [CLI](https://supabase.com/docs/guides/cli): `supabase start` sobe tudo local com Docker
- [Migrações](https://supabase.com/docs/guides/deployment/database-migrations): o esquema versionado no repositório
- [SDK de Python](https://github.com/supabase/supabase-py)
- [Servidor MCP](https://supabase.com/docs/guides/getting-started/mcp): o Claude Code consulta e altera o projeto

**Use quando:** o projeto precisa guardar dados do cliente, com login e regras de quem vê cada registro.

## Cloudflare

Workers rodam o seu código nos servidores da Cloudflare, perto de quem acessa, sem servidor para você manter. O Wrangler publica.

- [Workers](https://developers.cloudflare.com/workers/)
- [Wrangler](https://developers.cloudflare.com/workers/wrangler/): `wrangler deploy`, `wrangler secret put`
- [Servidor MCP remoto num Worker](https://developers.cloudflare.com/agents/guides/remote-mcp-server/): o caminho da arquitetura de referência
- [Workers em Python](https://developers.cloudflare.com/workers/languages/python/)
- [Servidores MCP da Cloudflare](https://github.com/cloudflare/mcp-server-cloudflare): o Claude Code operando a conta

**Use quando:** precisa publicar uma API, um MCP ou uma página sem cuidar de infraestrutura.

## Resend

API de e-mail transacional, simples de integrar.

- [Documentação](https://resend.com/docs)
- [SDK de Python](https://github.com/resend/resend-python)
- [React Email](https://react.email): os modelos de e-mail como componentes
- [Servidor MCP](https://github.com/resend/mcp-send-email)

**Use quando:** o agente precisa avisar uma pessoa: uma aprovação pendente, um resumo do dia, uma exceção.

## Stripe

Pagamentos, assinaturas e faturas, com modo de teste completo.

- [Documentação](https://docs.stripe.com)
- [Stripe CLI](https://docs.stripe.com/stripe-cli): `stripe listen` repassa para a sua máquina os avisos que o Stripe envia (os webhooks)
- [SDK de Python](https://github.com/stripe/stripe-python)
- [Servidor MCP e ferramentas para agentes](https://docs.stripe.com/mcp)

**Use quando:** o produto cobra o cliente. Desenvolva sempre no modo de teste, com as chaves de teste.

## Python

A linguagem do kit e das tools.

- [uv](https://docs.astral.sh/uv/): ambiente, dependências e versão do Python, num comando
- [Ruff](https://docs.astral.sh/ruff/): lint e formatação
- [pytest](https://docs.pytest.org): os testes do `make check`
- [Pydantic](https://docs.pydantic.dev): validar o que entra e o que sai
- [httpx](https://www.python-httpx.org): chamadas HTTP, síncronas ou assíncronas
- [FastAPI](https://fastapi.tiangolo.com): uma API em minutos
- [SDK de MCP em Python](https://github.com/modelcontextprotocol/python-sdk): escrever as suas próprias tools

**Use quando:** as tools, os scripts e os testes do projeto. É a linguagem do kit de domingo.

## Evolution API

API aberta para WhatsApp, que você hospeda.

- [Documentação](https://doc.evolution-api.com)
- [Repositório](https://github.com/EvolutionAPI/evolution-api)

**Use quando:** a pessoa que decide vive no WhatsApp. A Evolution API conecta de dois jeitos: pelo WhatsApp Web, que não é oficial e pode levar ao bloqueio do número, ou pela [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api), a oficial da Meta. Para produção, use a oficial.

## Temporal

Orquestração de fluxos duráveis: o código espera dias por um evento e retoma do ponto exato, mesmo se o servidor cair.

- [Documentação](https://docs.temporal.io)
- [SDK de Python](https://github.com/temporalio/sdk-python)
- [CLI](https://docs.temporal.io/cli): `temporal server start-dev` sobe um servidor local
- [Temporal Cloud](https://temporal.io/cloud)

**Use quando:** o processo tem esperas longas e passos que não podem se perder, como pedir uma aprovação, esperar a resposta e só então seguir para o pagamento.

## Para ir além

Ferramentas que fecham os buracos da arquitetura de referência quando o projeto cresce.

### Testar e observar o agente

- **[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):** abre o servidor MCP sem o Claude Code, lista as tools e chama uma por uma. **Use quando:** subir o MCP no Worker e ele não responder como esperado. Roda com `npx @modelcontextprotocol/inspector`.
- **[Langfuse](https://langfuse.com/docs):** rastreia cada chamada do agente, com prompt, tools, custo e tempo, e guarda os resultados dos evals. **Use quando:** precisar comparar uma versão do agente com a anterior.
- **[PostHog](https://posthog.com/docs):** métricas de uso do produto, gravação das sessões, ligar e desligar funções sem publicar de novo (feature flags) e acompanhamento das chamadas de LLM ([AI Observability](https://posthog.com/docs/ai-observability)). **Use quando:** pessoas de verdade começarem a usar o produto.
- **[Grafana](https://grafana.com/docs/grafana/latest/):** painéis de métricas e logs, com plano gratuito no [Grafana Cloud](https://grafana.com/products/cloud/). **Use quando:** a operação precisar acompanhar o agente em produção: volume, erros, tempo de resposta.

### Dados e segredos

- **[DuckDB](https://duckdb.org/docs/):** SQL direto sobre CSV, JSON e Parquet, sem servidor. **Use quando:** analisar as notas, os pedidos e os erros do eval no seu computador.
- **[1Password CLI](https://developer.1password.com/docs/cli/):** guarda as chaves fora do repositório. Com `op run`, o `.env` guarda só referências `op://`, e as chaves entram direto no comando. É pago: não tem plano gratuito, e um cofre dividido pelo grupo pede o plano Teams ou Business. **Use quando:** o grupo dividir chaves de API entre si e alguém já tiver o plano.

### Interface, integrações e APIs

- **[Playwright](https://playwright.dev/python/):** testa a interface ponta a ponta, num navegador de verdade. **Use quando:** o grupo tiver uma tela, como a de quem aprova.
- **[n8n](https://docs.n8n.io):** automações entre ferramentas, montadas visualmente. **Use quando:** o fluxo for curto e não justificar o Temporal.
- **[Bruno](https://docs.usebruno.com):** chama e versiona as chamadas de API no próprio repositório. As chaves ficam no `.env`, lidas como `{{process.env.NOME}}`, nunca escritas no arquivo da coleção. **Use quando:** testar as APIs do Supabase, do Resend ou do Stripe sem escrever código.

## Regra para todas

O fork é público. Chave de API, token e senha nunca entram em commit: ficam no `.env`, nos secrets do Worker ou nos secrets do repositório. O passo a passo está em [teams/CONTAS.md](teams/CONTAS.md).
