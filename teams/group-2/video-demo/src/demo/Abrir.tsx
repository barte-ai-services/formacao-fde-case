import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, FalaClaude, FalaVoce, Janela, Titulo } from "./ui";

const itens = [
  { item: "Sorvete 1,5 L", nota: 244, pedido: 244, doca: "244" },
  { item: "Pão de queijo 1 kg", nota: 260, pedido: 260, doca: "260" },
  { item: "Pizza congelada 460 g", nota: 196, pedido: 196, doca: "147" },
];

const colunas = "560px 200px 200px 1fr";

export const Abrir: React.FC = () => {
  const frame = useCurrentFrame();
  const destaque = interpolate(frame, [110, 126], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Cena>
      <div style={entra(frame, 0)}>
        <Eyebrow>2 · Abrir uma nota</Eyebrow>
      </div>
      <div style={entra(frame, 4)}>
        <Titulo>Me explica essa nota</Titulo>
      </div>
      <Janela>
        <FalaVoce texto="Abre a NF-035" frame={frame} inicio={20} />
        <FalaClaude frame={frame} inicio={44}>
          <div style={{ fontSize: 30, color: "#6B7488", marginBottom: 14 }}>
            Congelados Polar Sul · CD-03 · nota, pedido e doca lado a lado
          </div>
          <div style={{ display: "flex", flexDirection: "column", width: 1400 }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: colunas,
                fontSize: 26,
                fontWeight: 600,
                color: "#6B7488",
                paddingBottom: 10,
                borderBottom: `2px solid ${cor.linha}`,
              }}
            >
              <span>Item</span>
              <span>Nota</span>
              <span>Pedido</span>
              <span>Doca</span>
            </div>
            {itens.map((l, i) => {
              const ultima = i === itens.length - 1;
              return (
                <div
                  key={l.item}
                  style={{
                    ...entra(frame, 58 + i * 8, 14),
                    display: "grid",
                    gridTemplateColumns: colunas,
                    fontSize: 34,
                    color: cor.escuro,
                    padding: "14px 12px",
                    margin: "0 -12px",
                    borderRadius: 10,
                    background: ultima ? `rgba(194, 86, 27, ${0.14 * destaque})` : "transparent",
                  }}
                >
                  <span>{l.item}</span>
                  <span>{l.nota}</span>
                  <span>{l.pedido}</span>
                  <span style={{ fontWeight: ultima ? 700 : 400, color: ultima ? cor.laranja : cor.escuro }}>
                    {l.doca}
                    {ultima ? <span style={{ opacity: destaque }}> · faltam 49</span> : null}
                  </span>
                </div>
              );
            })}
          </div>
          <div style={{ ...entra(frame, 130), fontSize: 34, marginTop: 22, color: cor.escuro }}>
            O robô sugere <b>receber só o que chegou</b>. Quem decide é o analista.
          </div>
        </FalaClaude>
      </Janela>
    </Cena>
  );
};
