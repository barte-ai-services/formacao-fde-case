# Setup de um FDE

O deck apresentado no sábado, 14/11/2026, na Formação FDE: o setup da máquina, o Ahrena, o fork, o pull request e o que tem neste repositório.

- **Publicado em:** https://claude.ai/artifact/KEZ17v5sdpfCU3zvfCAxbr
- **Tipo:** um deck do tipo Slides do claude.ai, não uma página HTML solta. Por isso esta pasta não tem `artifact.json`, e as skills `versioning-artifacts` e `publishing-artifacts` não publicam este deck.

## O que tem aqui

| Caminho | O que é |
|---|---|
| `project/deck.json` | O índice: título, ordem dos slides, seções e fontes |
| `project/deck.css` | O estilo comum a todos os slides |
| `project/slides/*.html` | Um arquivo por slide, cada um com as notas de quem apresenta no `<aside>` |
| `assets/barte-logo.svg` | O logo da Barte usado no topo de cada slide |

A ordem dos slides está em `order`, no `deck.json`: capa, quem já usa o Claude, ferramentas, Ahrena, Git fork, fork ou sync do case, pull request e o que tem no repositório.

## Republicar a partir desta pasta

No Claude Code, peça a publicação no mesmo link, com a ferramenta `Artifact`:

- `url`: o link publicado acima;
- `root`: esta pasta, `artifacts/setup-de-um-fde`;
- `file_path`: `project/deck.json`, e os outros arquivos de `project/` em `files`.

O logo entra no deck como um arquivo enviado ao artefato, e os slides apontam para ele por `/_blob/<id>`. Num artefato novo, envie `assets/barte-logo.svg` primeiro e troque esse endereço nos slides pelo que o envio devolver.

As edições feitas direto no claude.ai não voltam para cá sozinhas. Depois de mexer no deck publicado, traga os arquivos de volta para esta pasta num pull request.
