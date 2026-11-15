import React from "react";
import { Easing, interpolate } from "remotion";
import { loadFont as loadTitulo } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadTexto } from "@remotion/google-fonts/Inter";

export const { fontFamily: fonteTitulo } = loadTitulo("normal", {
  weights: ["500", "700"],
  subsets: ["latin"],
});
export const { fontFamily: fonteTexto } = loadTexto("normal", {
  weights: ["400", "600"],
  subsets: ["latin"],
});

export const cor = {
  escuro: "#14213D",
  claro: "#F7F5F0",
  areia: "#ECE6DA",
  laranja: "#C2561B",
  laranjaClaro: "#F2B48C",
  texto: "#3E4A5E",
  textoClaro: "#C9D3E3",
  linha: "#D6CEBE",
  verde: "#2F7D5B",
  branco: "#FFFFFF",
};

const suave = Easing.bezier(0.16, 1, 0.3, 1);

/** Opacidade e deslocamento de entrada, a partir do frame `inicio`. */
export const entra = (frame: number, inicio: number, dur = 18) => ({
  opacity: interpolate(frame, [inicio, inicio + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: suave,
  }),
  translate: interpolate(frame, [inicio, inicio + dur], ["0px 28px", "0px 0px"], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: suave,
  }),
});

/** Texto digitado aos poucos, começando no frame `inicio`. */
export const digita = (texto: string, frame: number, inicio: number, porFrame = 1.2) => {
  const n = Math.max(0, Math.floor((frame - inicio) * porFrame));
  return texto.slice(0, n);
};

export const Eyebrow: React.FC<{ children: React.ReactNode; claro?: boolean; cor?: string }> = ({
  children,
  claro,
  cor: corFixa,
}) => (
  <div
    style={{
      fontFamily: fonteTitulo,
      fontWeight: 700,
      fontSize: 30,
      letterSpacing: 4,
      textTransform: "uppercase",
      color: corFixa ?? (claro ? cor.laranjaClaro : cor.laranja),
    }}
  >
    {children}
  </div>
);

export const Titulo: React.FC<{ children: React.ReactNode; claro?: boolean; tamanho?: number }> = ({
  children,
  claro,
  tamanho = 84,
}) => (
  <div
    style={{
      fontFamily: fonteTitulo,
      fontWeight: 700,
      fontSize: tamanho,
      lineHeight: 1.05,
      letterSpacing: -1.5,
      color: claro ? cor.claro : cor.escuro,
    }}
  >
    {children}
  </div>
);

/** Balão do analista, com o texto sendo digitado. */
export const FalaVoce: React.FC<{ texto: string; frame: number; inicio: number }> = ({ texto, frame, inicio }) => {
  const visivel = digita(texto, frame, inicio);
  const cursor = visivel.length < texto.length && frame >= inicio;
  return (
    <div style={{ ...entra(frame, inicio - 6, 10), alignSelf: "flex-end" }}>
      <div
        style={{
          background: cor.escuro,
          color: cor.claro,
          fontFamily: fonteTexto,
          fontSize: 40,
          padding: "22px 36px",
          borderRadius: 32,
          borderBottomRightRadius: 8,
          minHeight: 48,
        }}
      >
        {visivel}
        <span style={{ opacity: cursor ? 1 : 0, color: cor.laranjaClaro }}>|</span>
      </div>
    </div>
  );
};

/** Balão do Claude. */
export const FalaClaude: React.FC<{ frame: number; inicio: number; children: React.ReactNode }> = ({
  frame,
  inicio,
  children,
}) => (
  <div
    style={{
      ...entra(frame, inicio),
      alignSelf: "flex-start",
      background: cor.branco,
      border: `2px solid ${cor.linha}`,
      borderRadius: 28,
      borderBottomLeftRadius: 8,
      padding: "30px 36px",
      fontFamily: fonteTexto,
      fontSize: 34,
      lineHeight: 1.45,
      color: cor.texto,
      maxWidth: 1500,
    }}
  >
    {children}
  </div>
);

/** Janela de conversa que ocupa a cena. */
export const Janela: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      flex: 1,
      background: cor.areia,
      borderRadius: 24,
      border: `2px solid ${cor.linha}`,
      padding: 40,
      display: "flex",
      flexDirection: "column",
      gap: 28,
      overflow: "hidden",
    }}
  >
    {children}
  </div>
);

export const Cena: React.FC<{ children: React.ReactNode; fundo?: string }> = ({ children, fundo = cor.claro }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: fundo,
      padding: "90px 120px",
      display: "flex",
      flexDirection: "column",
      gap: 36,
      fontFamily: fonteTexto,
    }}
  >
    {children}
  </div>
);
