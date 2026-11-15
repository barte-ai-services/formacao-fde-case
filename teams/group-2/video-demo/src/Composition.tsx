import React from "react";
import { Composition } from "remotion";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Abertura } from "./demo/Abertura";
import { Fila } from "./demo/Fila";
import { Abrir } from "./demo/Abrir";
import { Decidir } from "./demo/Decidir";
import { Limites } from "./demo/Limites";
import { Fechamento } from "./demo/Fechamento";

const FPS = 30;
const TRANSICAO = 12;

const cenas = [
  { nome: "Abertura", dur: 4 * FPS, C: Abertura },
  { nome: "Fila", dur: 7 * FPS, C: Fila },
  { nome: "Abrir", dur: 8 * FPS, C: Abrir },
  { nome: "Decidir", dur: 8 * FPS, C: Decidir },
  { nome: "Limites", dur: 6 * FPS, C: Limites },
  { nome: "Fechamento", dur: 5 * FPS, C: Fechamento },
];

const DURACAO = cenas.reduce((s, c) => s + c.dur, 0) - TRANSICAO * (cenas.length - 1);

export const DemoAnalista: React.FC = () => (
  <TransitionSeries>
    {cenas.map(({ nome, dur, C }, i) => (
      <React.Fragment key={nome}>
        {i > 0 ? (
          <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSICAO })} />
        ) : null}
        <TransitionSeries.Sequence durationInFrames={dur} name={nome}>
          <C />
        </TransitionSeries.Sequence>
      </React.Fragment>
    ))}
  </TransitionSeries>
);

export const MyComposition = () => (
  <Composition id="DemoAnalista" component={DemoAnalista} durationInFrames={DURACAO} fps={FPS} width={1920} height={1080} />
);
