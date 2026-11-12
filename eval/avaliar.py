"""Eval contra o gabarito: acerto por campo e por tipo de exceção.

Uso:
    uv run python eval/avaliar.py saidas/propostas.jsonl
    uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl

Uma nota conta como acerto completo quando classificação, ação na doca e encaminhamento batem.
Notas sem proposta contam como erro. Se houver mais de uma proposta para a mesma nota, vale a última aceita.
O servidor também grava as tentativas que a régua recusou. Com elas, o eval mede o encaminhamento na primeira
tentativa de cada nota: um agente que só acerta depois de ser recusado não sabe a régua.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from jachegou.base import CLASSIFICACOES, Base  # noqa: E402

CAMPOS = ("classificacao", "acao_doca", "encaminhamento")


def ler_linhas(caminho: Path) -> list[dict]:
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


def ler_propostas(caminho: Path) -> dict[str, dict]:
    """A última proposta aceita de cada nota."""
    return {p["nota_id"]: p for p in ler_linhas(caminho) if not p.get("recusada")}


def ler_primeiras(caminho: Path) -> dict[str, dict]:
    """A primeira tentativa de cada nota, aceita ou recusada pela régua."""
    primeiras: dict[str, dict] = {}
    for p in ler_linhas(caminho):
        primeiras.setdefault(p["nota_id"], p)
    return primeiras


def avaliar_arquivo(caminho: Path, gabarito: list[dict]) -> dict:
    r = avaliar(ler_propostas(caminho), gabarito)
    primeiras = ler_primeiras(caminho)
    r["encaminhamento_primeira"] = sum(primeiras.get(g["nota_id"], {}).get("encaminhamento") == g["encaminhamento"]
                                       for g in gabarito)
    r["notas_com_recusa"] = len({p["nota_id"] for p in ler_linhas(caminho) if p.get("recusada")})
    return r


def avaliar(props: dict[str, dict], gabarito: list[dict]) -> dict:
    por_tipo = defaultdict(lambda: {"total": 0, "classificacao": 0, "completo": 0})
    campo_ok = {c: 0 for c in CAMPOS}
    completo = 0
    risco_ok = risco_n = 0
    confusao = defaultdict(int)
    erros = []
    for g in gabarito:
        p = props.get(g["nota_id"], {})
        t = por_tipo[g["classificacao"]]
        t["total"] += 1
        acertos = {c: p.get(c) == g[c] for c in CAMPOS}
        for c, ok in acertos.items():
            campo_ok[c] += ok
        t["classificacao"] += acertos["classificacao"]
        if all(acertos.values()):
            completo += 1
            t["completo"] += 1
        else:
            erros.append((g, p))
        confusao[(g["classificacao"], p.get("classificacao", "sem proposta"))] += 1
        if p.get("valor_em_risco") is not None:
            risco_n += 1
            risco_ok += abs(float(p["valor_em_risco"]) - g["valor_em_risco"]) <= 1.0
    n = len(gabarito)
    return {"n": n, "completo": completo, "campos": campo_ok, "por_tipo": dict(por_tipo),
            "risco": (risco_ok, risco_n), "confusao": dict(confusao), "erros": erros,
            "cobertura": sum(1 for g in gabarito if g["nota_id"] in props)}


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "—"


def relatorio(nome: str, r: dict, outro: tuple[str, dict] | None = None) -> str:
    n = r["n"]
    linhas = [f"# Eval · {nome}", "",
              f"Notas com proposta: {r['cobertura']} de {n}", "",
              "| Medida | " + nome + (f" | {outro[0]}" if outro else "") + " |",
              "| --- | --- |" + (" --- |" if outro else "")]

    def linha(rotulo, a, b):
        linhas.append(f"| {rotulo} | {a} |" + (f" {b} |" if outro else ""))

    o = outro[1] if outro else None
    linha("Acerto completo (as três skills)", pct(r["completo"], n), pct(o["completo"], n) if o else "")
    for c, rot in zip(CAMPOS, ("Skill 1 · classificação", "Skill 2 · ação na doca", "Skill 3 · encaminhamento")):
        linha(rot, pct(r["campos"][c], n), pct(o["campos"][c], n) if o else "")
    linha("Skill 3 · encaminhamento na primeira tentativa", pct(r["encaminhamento_primeira"], n),
          pct(o["encaminhamento_primeira"], n) if o else "")
    linha("Notas com recusa da régua", str(r["notas_com_recusa"]), str(o["notas_com_recusa"]) if o else "")
    ok, tot = r["risco"]
    linha("Valor em risco (até R$ 1 de diferença)", f"{ok} de {tot}" if tot else "não informado",
          (f"{o['risco'][0]} de {o['risco'][1]}" if o and o["risco"][1] else "não informado") if o else "")
    linhas += ["", "## Por tipo", "", "| Tipo | Notas | Classificação | Completo |" + (f" Completo · {outro[0]} |" if outro else ""),
               "| --- | --- | --- | --- |" + (" --- |" if outro else "")]
    for c in CLASSIFICACOES:
        t = r["por_tipo"].get(c)
        if not t:
            continue
        extra = f" {pct(o['por_tipo'][c]['completo'], t['total'])} |" if o else ""
        linhas.append(f"| {c} | {t['total']} | {pct(t['classificacao'], t['total'])} | {pct(t['completo'], t['total'])} |{extra}")
    trocas = sorted(((k, v) for k, v in r["confusao"].items() if k[0] != k[1]), key=lambda x: -x[1])
    if trocas:
        linhas += ["", "## Confusões mais comuns", ""]
        for (real, prev), v in trocas[:8]:
            linhas.append(f"- {real} classificada como {prev}: {v}")
    return "\n".join(linhas) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("propostas", type=Path)
    ap.add_argument("--comparar", type=Path, help="outro arquivo de propostas, por exemplo o baseline")
    ap.add_argument("--erros", action="store_true", help="lista as notas erradas")
    a = ap.parse_args()
    base = Base()
    arquivo = base.pasta / "gabarito" / "gabarito.json"
    if not arquivo.exists():
        raise SystemExit("O gabarito ainda não está em dados/gabarito/. Ele chega no domingo.")
    gabarito = json.loads(arquivo.read_text(encoding="utf-8"))
    r = avaliar_arquivo(a.propostas, gabarito)
    outro = ("baseline", avaliar_arquivo(a.comparar, gabarito)) if a.comparar else None
    texto = relatorio(a.propostas.stem, r, outro)
    print(texto)
    if a.erros:
        for g, p in r["erros"]:
            print(f"- {g['nota_id']} ({g['classificacao']}): esperado {g['classificacao']}/{g['acao_doca']}/{g['encaminhamento']}, "
                  f"veio {p.get('classificacao')}/{p.get('acao_doca')}/{p.get('encaminhamento')}")
    destino = RAIZ / "saidas" / f"relatorio_{a.propostas.stem}.md"
    destino.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
