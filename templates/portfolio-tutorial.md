# Tutorial: o trabalho do grupo como peça de portfólio

> **Momento:** domingo, 15/11, durante a construção e depois do pitch das 16h15.
>
> **Prazo:** a definir pela coordenação.
>
> **Onde entregar:** no fork do líder do grupo, em `teams/group-N/portfolio.md`, por pull request.
>
> `group-N` é a pasta do seu grupo: `group-1`, `group-2` e assim por diante.

O que o grupo fez no fim de semana pode virar uma peça de portfólio: algo que mostra a outra
pessoa **como** vocês trabalham como FDE (o processo) e **o que** entregaram (o resultado). Este
tutorial é rígido de propósito: siga os passos na ordem e preencha cada seção.

## Passo a passo

1. **Crie o arquivo.** No fork do líder, crie `teams/group-N/portfolio.md` e copie para ele a
   estrutura da seção "Estrutura da peça", mais abaixo.
2. **Junte o material.** Tenha abertos os arquivos que o grupo já entregou:
   - `teams/group-N/checkpoint-1-diagnosis.md`
   - `teams/group-N/checkpoint-2-access-checklist.md`
   - `teams/group-N/checkpoint-2-solution-design.md`
   - `teams/group-N/checkpoint-2-delivery-plan.md`
   - `teams/group-N/sunday-pitch.md`
   - o resultado do eval e o código que o grupo construiu
3. **Preencha uma seção por vez, na ordem.** Cada seção diz de qual arquivo tirar o conteúdo.
   Resuma, não copie: o leitor não esteve no evento.
4. **Ligue cada afirmação a uma evidência.** Um número, um trecho do eval, um link para um
   arquivo do repositório ou para um pull request.
5. **Revise em dupla.** Uma pessoa que não escreveu a seção lê e marca o que não entendeu.
6. **Abra o pull request** no fork do líder com o título `Portfólio do grupo N`.
7. **Confira** a lista do fim deste tutorial antes de pedir o merge.

## Regras

- Use os nomes do caso: Já Chegou e Terminal Sul. Pessoas só pelo papel (CFO, controller, compras).
- Nenhuma credencial, chave ou dado sensível no texto.
- Mostre o que deu errado e o que o grupo mudou. Um processo sem erro não convence.
- Escreva em frases curtas. Use tabelas e listas onde ajudarem.

---

## Estrutura da peça

Copie a partir daqui para `teams/group-N/portfolio.md`.

```markdown
# <Título: o resultado em uma frase>

Grupo: ____ · Integrantes: ____ · Formação FDE, 13 a 15/11/2026

## 1. Contexto
<!-- De onde tirar: case/briefing.md e a reunião com o cliente. -->
- Cliente: Já Chegou, varejista de entrega rápida (caso fictício).
- O processo: contas a pagar de ponta a ponta.
- O pedido do CFO: ____
- Quem participou do lado do cliente (por papel): ____

## 2. Diagnóstico
<!-- De onde tirar: checkpoint-1-diagnosis.md. -->
- O problema, como o grupo entendeu: ____
- A perda escolhida e o número a mover (baseline → meta): ____
- A reformulação do pedido, e por quê: ____
- A priorização das frentes (retorno, tempo até o primeiro valor, esforço): ____

## 3. Desenho
<!-- De onde tirar: checkpoint-2-solution-design.md e checkpoint-2-access-checklist.md. -->
- Fluxo atual → fluxo proposto (três a cinco passos cada): ____
- Onde entra o agente: ____
- Onde o humano decide (modo proposta e alçadas R$ 5 mil / R$ 20 mil / R$ 100 mil): ____
- Acessos necessários e principais riscos: ____

## 4. Construção
<!-- De onde tirar: o código do grupo e os pull requests. -->
- O que foi construído: ____
- Como funciona, em poucos passos: ____
- Decisões técnicas e por quê: ____
- Links para os pull requests principais: ____

## 5. Eval
<!-- De onde tirar: a execução do eval do grupo. -->
- Contra o que o agente foi avaliado: ____
- Resultado: ____
- Onde o agente erra e o que o grupo fez a respeito: ____

## 6. Resultado
<!-- De onde tirar: sunday-pitch.md e checkpoint-2-delivery-plan.md. -->
- O que muda para o cliente, ligado ao número a mover: ____
- O primeiro valor e quando ele chegaria: ____
- O que se repete na Terminal Sul: ____
- Próximos passos: ____

## 7. Aprendizados
- O que o grupo faria igual: ____
- O que o grupo faria diferente: ____
- O que cada integrante aprendeu, em uma frase: ____
```

## Conferência antes do merge

- [ ] As sete seções estão preenchidas, na ordem.
- [ ] O número a mover aparece no diagnóstico e no resultado.
- [ ] Toda afirmação importante tem evidência (número, eval, link).
- [ ] O eval mostra também os erros.
- [ ] Nenhum nome de pessoa, nenhuma credencial, nenhum dado sensível.
- [ ] Alguém que não escreveu leu tudo e entendeu.
- [ ] O arquivo está em `teams/group-N/portfolio.md` no fork do líder.
