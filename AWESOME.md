# Awesome tools para builders

As ferramentas que um FDE da Barte usa para construir e entregar, com os links que valem a pena. Quase todas têm plano gratuito para começar, e várias têm um servidor MCP oficial, o que deixa o Claude Code operar a ferramenta por você.

## Onde estamos

O que o curso já tem e o que ainda falta, em 14/11/2026.

| Ferramenta | Instalada pela `setup-fde` | Papel na arquitetura de referência | Situação no curso |
|---|---|---|---|
| **Claude Code** | sim | o agente: constrói e roda | pronto, com o Ahrena configurado no repositório |
| **Ahrena Framework** | sim, os plugins | o time de agentes que constrói e revisa | pronto: Athena orquestra e Argos revisa |
| **git e GitHub (`gh`)** | sim | fork, PRs, issues e Actions | pronto |
| **Python (com `uv`)** | sim | o backend (FastAPI e FastMCP), o kit e as tools | pronto |
| **Supabase** | sim, o CLI | banco, autenticação e storage | CLI pronto; o líder de cada grupo cria a conta ([teams/CONTAS.md](teams/CONTAS.md)) |
| **Cloudflare** | sim, o Wrangler (com Node.js e npm) | o front em Astro e o FastAPI, cada um num Worker | Wrangler pronto; o líder de cada grupo cria a conta ([teams/CONTAS.md](teams/CONTAS.md)) |
| **Docker** | sim (Colima no Mac) | sobe o Supabase local | pronto |
| **Astro com React** | não; vem no projeto com `npm create astro@latest` | a tela de quem aprova | pronto para usar: Node.js e npm já vêm na `setup-fde` |
| **FastMCP** | não; vem no projeto com `uv add fastmcp` | o servidor MCP, com login OAuth pelo Supabase | pronto para usar; o FastMCP Gateway pede conta na Prefect |
| **Resend** | não | e-mail: avisar quem aprova | na arquitetura de referência; a conta é opcional no fim de semana |
| **Barte** | não | pagamentos: cobrar, receber e pagar | fora do curso; o caso não cobra ninguém |
| **Evolution API** | não | WhatsApp: pedir a aprovação onde a pessoa está | fora do curso; exige servidor próprio |
| **Temporal** | não | fluxos longos: esperar a aprovação e retomar | fora do curso; o próximo passo quando o fluxo ficar longo |

A leitura: a stack de build e publicação (Claude Code, GitHub, Supabase, Cloudflare) está instalada e documentada. As outras quatro resolvem problemas que o caso vai encontrar logo depois do primeiro agente: avisar alguém (Resend, Evolution API), esperar uma resposta que demora dias (Temporal) e cobrar ou pagar (Barte). Nenhuma delas é pré-requisito para o fim de semana.

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
- [Workers em Python](https://developers.cloudflare.com/workers/languages/python/): onde roda o FastAPI da arquitetura de referência
- [FastAPI num Python Worker](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/)
- [Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/): rodar uma rotina num horário
- [Servidores MCP da Cloudflare](https://github.com/cloudflare/mcp-server-cloudflare): o Claude Code operando a conta

**Use quando:** precisa publicar uma API ou uma página sem cuidar de infraestrutura.

## Astro

Framework de front-end que monta as páginas no servidor e deixa interativas só as partes que precisam, como ilhas React. Publica num Worker da Cloudflare.

- [Documentação](https://docs.astro.build/en/getting-started/)
- [Deploy na Cloudflare](https://docs.astro.build/en/guides/deploy/cloudflare/): `npx astro add cloudflare` e `wrangler deploy`
- [Ilhas React](https://docs.astro.build/en/guides/integrations-guide/react/): `npx astro add react`
- [Astro com Supabase](https://docs.astro.build/en/guides/backend/supabase/): o login de quem aprova

**Use quando:** o agente precisa de uma interface: listar as propostas, mostrar a nota e registrar a decisão de uma pessoa.

## FastMCP

O jeito mais curto de escrever um servidor MCP em Python: uma função com `@mcp.tool` vira uma tool. Tem login OAuth pronto com o Supabase.

- [Documentação](https://gofastmcp.com)
- [Login com o Supabase](https://gofastmcp.com/integrations/supabase): OAuth 2.1, com o token de quem chamou em cada tool
- [FastMCP Gateway](https://gofastmcp.com/deployment/fastmcp-cloud): publica o servidor a partir do repositório
- [SDK de MCP em Python](https://github.com/modelcontextprotocol/python-sdk): o SDK oficial, por baixo

**Use quando:** o agente precisa ler e gravar no sistema do cliente em nome de quem o chamou.

## Resend

API de e-mail transacional, simples de integrar.

- [Documentação](https://resend.com/docs)
- [SDK de Python](https://github.com/resend/resend-python)
- [React Email](https://react.email): os modelos de e-mail como componentes
- [Servidor MCP](https://github.com/resend/mcp-send-email)

**Use quando:** o agente precisa avisar uma pessoa: uma aprovação pendente, um resumo do dia, uma exceção.

## Barte

A plataforma de pagamentos da casa: pedidos, links de pagamento, assinaturas, cartão com 3DS e antifraude, Pix e conta PJ, com sandbox para testar.

- [Documentação para desenvolvedores](https://docs.barte.com)
- [Referência da API](https://docs.barte.com/api-reference): compradores, pedidos, estornos e 3DS
- [Preparação do vendedor](https://docs.barte.com/guias/passo-a-passo-do-vendedor/1o-preparacao): token de API e webhooks
- [Pedidos, links de pagamento e assinaturas](https://docs.barte.com/guias/passo-a-passo-do-vendedor/2o-criando-pedidos-or-links-de-pagamento-or-assinaturas)
- [Cartões para testes](https://docs.barte.com/guias/inicio/cartoes-para-testes) e [métodos de pagamento](https://docs.barte.com/guias/inicio/metodos-de-pagamento)
- [Banking](https://docs.barte.com/banking): Pix com QR Code, transferências e os avisos por webhook
- [SDK web](https://docs.barte.com/sdks): captura os dados do cartão com segurança, sem que eles passem pelo seu servidor

**Use quando:** o produto cobra o cliente ou paga um fornecedor. Desenvolva sempre no sandbox, com as chaves de teste.

## Python

A linguagem do backend, do kit e das tools.

- [uv](https://docs.astral.sh/uv/): ambiente, dependências e versão do Python, num comando
- [Ruff](https://docs.astral.sh/ruff/): lint e formatação
- [pytest](https://docs.pytest.org): os testes do `make check`
- [Pydantic](https://docs.pydantic.dev): validar o que entra e o que sai
- [httpx](https://www.python-httpx.org): chamadas HTTP, síncronas ou assíncronas
- [FastAPI](https://fastapi.tiangolo.com): o `/api` da arquitetura de referência
- [FastMCP](https://gofastmcp.com): o servidor MCP da arquitetura de referência

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
- **[Bruno](https://docs.usebruno.com):** chama e versiona as chamadas de API no próprio repositório. As chaves ficam no `.env`, lidas como `{{process.env.NOME}}`, nunca escritas no arquivo da coleção. **Use quando:** testar as APIs do Supabase, do Resend ou da Barte sem escrever código.

## Regra para todas

O fork é público. Chave de API, token e senha nunca entram em commit: ficam no `.env`, nos secrets do Worker ou nos secrets do repositório. O passo a passo está em [teams/CONTAS.md](teams/CONTAS.md).
