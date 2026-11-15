import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, fonteTexto, Titulo } from "./ui";

export const Abertura: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Cena fundo={cor.escuro}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "flex-end", gap: 32 }}>
        <div
          style={{
            height: 12,
            background: cor.laranja,
            width: interpolate(frame, [0, 20], [0, 180], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        />
        <div style={entra(frame, 6)}>
          <Eyebrow claro>Já Chegou · Contas a pagar</Eyebrow>
        </div>
        <div style={entra(frame, 14)}>
          <Titulo claro tamanho={140}>
            A fila do analista
          </Titulo>
        </div>
        <div style={{ ...entra(frame, 26), fontFamily: fonteTexto, fontSize: 48, color: cor.textoClaro, maxWidth: 1600 }}>
          Conferir e decidir notas fiscais de mercadoria sem sair do Claude.
        </div>
      </div>
    </Cena>
  );
};
