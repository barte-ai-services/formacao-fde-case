import React from "react";
import { useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, fonteTitulo, Titulo } from "./ui";

const itens = [
  { titulo: "Diretoria e fornecedor bloqueado", texto: "Nem aparecem na fila. Se alguém tentar, o sistema recusa." },
  { titulo: "Acima do seu nível", texto: "Se a régua manda para o coordenador, o analista não decide." },
  { titulo: "Tudo registrado", texto: "Cada decisão grava quem decidiu, quando e por quê." },
];

export const Limites: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Cena fundo={cor.escuro}>
      <div style={entra(frame, 0)}>
        <Eyebrow claro>As travas</Eyebrow>
      </div>
      <div style={entra(frame, 4)}>
        <Titulo claro>O sistema protege a alçada</Titulo>
      </div>
      <div style={{ display: "flex", flexDirection: "column", marginTop: 20 }}>
        {itens.map((it, i) => (
          <div
            key={it.titulo}
            style={{
              ...entra(frame, 18 + i * 12),
              display: "flex",
              gap: 40,
              alignItems: "baseline",
              padding: "36px 0",
              borderTop: "2px solid #2E3D5C",
            }}
          >
            <span style={{ fontFamily: fonteTitulo, fontWeight: 700, fontSize: 56, color: cor.laranjaClaro, width: 70 }}>
              {i + 1}
            </span>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <span style={{ fontFamily: fonteTitulo, fontWeight: 700, fontSize: 52, color: cor.claro }}>{it.titulo}</span>
              <span style={{ fontSize: 38, color: cor.textoClaro }}>{it.texto}</span>
            </div>
          </div>
        ))}
      </div>
    </Cena>
  );
};
