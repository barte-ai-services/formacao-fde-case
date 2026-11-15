# Vídeo demo: a fila do analista

Um vídeo curto (36 s, 1080p, sem áudio) para mostrar ao cliente como o analista do contas a pagar da Já Chegou
usa o servidor `ja-chegou-analista` dentro do Claude: ver a fila, abrir uma nota, decidir e as travas de alçada.

**Assistir:** [`demo-fila-analista.mp4`](demo-fila-analista.mp4)

## O que aparece

| Cena | Tempo | O que mostra |
| --- | --- | --- |
| Abertura | 4 s | A fila do analista, Já Chegou · Contas a pagar |
| Ver a fila | 7 s | “Mostra a minha fila”: 34 notas e as quatro maiores |
| Abrir uma nota | 8 s | “Abre a NF-035”: nota, pedido e doca lado a lado; faltam 49 pizzas na doca |
| Decidir | 8 s | Aprovar com motivo, confirmação, decisão gravada; a fila cai de 34 para 33 |
| As travas | 6 s | Diretoria e bloqueio fora, nada acima do nível, tudo registrado |
| Fechamento | 5 s | Ver · Abrir · Decidir · Simular |

Os números vêm das tools `listar_fila` e `ler_proposta` (fila de 15/11/2026, propostas da linha de base).
A conversa é uma reconstrução animada, não uma gravação de tela: a decisão da cena 4 não foi gravada em
`saidas/decisoes.jsonl`.

## Editar e gerar de novo

O vídeo é feito em [Remotion](https://www.remotion.dev). Cada cena é um arquivo em `src/demo/`; a ordem e o
tempo de cada uma ficam em `src/Composition.tsx`.

```bash
cd teams/group-2/video-demo
npm i
npx remotion studio                                    # pré-visualizar
npx remotion render DemoAnalista demo-fila-analista.mp4
```
