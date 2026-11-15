import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, FalaClaude, FalaVoce, fonteTitulo, Janela, Titulo } from "./ui";

export const Decidir: React.FC = () => {
  const frame = useCurrentFrame();
  const contador = frame < 150 ? 34 : 33;
  const pulso = interpolate(frame, [150, 158, 172], [1, 1.25, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <Cena>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={entra(frame, 0)}>
            <Eyebrow>3 · Decidir</Eyebrow>
          </div>
          <div style={entra(frame, 4)}>
            <Titulo>Aprovar ou mudar a ação</Titulo>
          </div>
        </div>
        <div style={{ ...entra(frame, 8), display: "flex", alignItems: "baseline", gap: 14 }}>
          <span style={{ fontSize: 32, color: "#6B7488" }}>na fila</span>
          <span
            style={{
              fontFamily: fonteTitulo,
              fontWeight: 700,
              fontSize: 84,
              color: cor.laranja,
              display: "inline-block",
              scale: pulso,
            }}
          >
            {contador}
          </span>
        </div>
      </div>
      <Janela>
        <FalaVoce texto="Aprova a NF-035: faltaram 49 pizzas, recebe só o que chegou" frame={frame} inicio={16} />
        <FalaClaude frame={frame} inicio={74}>
          Vou gravar: <b>NF-035 · aprovar · receber uma parte</b>.<br />
          Motivo: “faltaram 49 pizzas, recebe só o que chegou”. Confirma?
        </FalaClaude>
        <FalaVoce texto="Sim" frame={frame} inicio={120} />
        <div
          style={{
            ...entra(frame, 142),
            alignSelf: "flex-start",
            display: "flex",
            alignItems: "center",
            gap: 18,
            background: cor.verde,
            color: cor.claro,
            fontSize: 36,
            fontWeight: 600,
            padding: "22px 34px",
            borderRadius: 20,
          }}
        >
          <span style={{ fontSize: 40 }}>✓</span> Decisão gravada. A NF-035 saiu da fila.
        </div>
      </Janela>
    </Cena>
  );
};
