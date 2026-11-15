import React from "react";
import { useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, fonteTitulo, Titulo } from "./ui";

const passos = ["Ver", "Abrir", "Decidir", "Simular"];

export const Fechamento: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Cena fundo={cor.laranja}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 48 }}>
        <div style={entra(frame, 0)}>
          <Eyebrow cor="#FBE3D2">Já Chegou · A fila do analista</Eyebrow>
        </div>
        <div style={{ display: "flex", gap: 28 }}>
          {passos.map((p, i) => (
            <div
              key={p}
              style={{
                ...entra(frame, 8 + i * 8),
                fontFamily: fonteTitulo,
                fontWeight: 700,
                fontSize: 64,
                color: cor.claro,
                background: "rgba(20, 33, 61, 0.22)",
                padding: "20px 40px",
                borderRadius: 999,
              }}
            >
              {p}
            </div>
          ))}
        </div>
        <div style={entra(frame, 46)}>
          <Titulo claro tamanho={96}>
            Cada decisão com evidência
            <br />e dentro da alçada.
          </Titulo>
        </div>
      </div>
    </Cena>
  );
};
