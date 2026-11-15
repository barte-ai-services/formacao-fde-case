import React from "react";
import { useCurrentFrame } from "remotion";
import { Cena, cor, entra, Eyebrow, FalaClaude, FalaVoce, fonteTitulo, Janela, Titulo } from "./ui";

const linhas = [
  { nota: "NF-035", fornecedor: "Congelados Polar Sul", tipo: "E3", acao: "Receber uma parte", valor: "R$ 17.330" },
  { nota: "NF-079", fornecedor: "Bebidas Rio Claro", tipo: "E4", acao: "Recusar", valor: "R$ 16.031" },
  { nota: "NF-050", fornecedor: "Bebidas Rio Claro", tipo: "E2", acao: "Receber uma parte", valor: "R$ 15.071" },
  { nota: "NF-041", fornecedor: "Limpeza Brilho", tipo: "OK", acao: "Receber tudo", valor: "R$ 14.604" },
];

const colunas = "190px 470px 110px 360px 1fr";

export const Fila: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Cena>
      <div style={entra(frame, 0)}>
        <Eyebrow>1 · Ver a fila</Eyebrow>
      </div>
      <div style={entra(frame, 4)}>
        <Titulo>O que tem pra mim hoje?</Titulo>
      </div>
      <Janela>
        <FalaVoce texto="Mostra a minha fila" frame={frame} inicio={20} />
        <FalaClaude frame={frame} inicio={50}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 20, marginBottom: 18 }}>
            <span style={{ fontFamily: fonteTitulo, fontWeight: 700, fontSize: 72, color: cor.laranja }}>34</span>
            <span style={{ fontSize: 36, color: cor.escuro }}>notas esperando você. As maiores:</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", width: 1360 }}>
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
              <span>Nota</span>
              <span>Fornecedor</span>
              <span>Tipo</span>
              <span>O robô sugere</span>
              <span style={{ textAlign: "right" }}>Valor</span>
            </div>
            {linhas.map((l, i) => (
              <div
                key={l.nota}
                style={{
                  ...entra(frame, 64 + i * 8, 14),
                  display: "grid",
                  gridTemplateColumns: colunas,
                  fontSize: 32,
                  color: cor.escuro,
                  padding: "8px 0",
                  borderBottom: `1px solid ${cor.linha}`,
                }}
              >
                <span style={{ fontWeight: 600 }}>{l.nota}</span>
                <span>{l.fornecedor}</span>
                <span>{l.tipo}</span>
                <span style={{ color: l.acao === "Recusar" ? cor.laranja : cor.escuro }}>{l.acao}</span>
                <span style={{ textAlign: "right" }}>{l.valor}</span>
              </div>
            ))}
          </div>
        </FalaClaude>
      </Janela>
    </Cena>
  );
};
