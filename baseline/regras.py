"""Baseline sem IA: as regras que um time de operação escreveria numa primeira tentativa.

É de propósito simples. Ele acerta a maior parte das notas e erra onde o sentido dos dados não
está escrito no campo: pedido sem número na nota, nota reemitida, unidade de caixa, tolerância de
preço, compra emergencial da loja e a régua de alçadas inteira.

Uso:
    uv run python baseline/regras.py              # grava saidas/baseline.jsonl
    uv run python eval/avaliar.py saidas/baseline.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from jachegou.base import Base  # noqa: E402


def classificar(base: Base, nota: dict) -> str:
    # 1. Duplicidade só pelo número da nota.
    for l in base.lancadas_do_fornecedor(nota["fornecedor_id"]):
        if l["numero"] == nota["numero"] and l["serie"] == nota["serie"]:
            return "E6"
    # 2. Sem número de pedido na nota, é nota sem ordem.
    if not nota["pedido_referenciado"]:
        return "E5"
    ordem = base.ordens.get(nota["pedido_referenciado"])
    if ordem is None:
        return "E5"
    # 3. Item sem SKU é item sem cadastro.
    if any(i["sku"] is None for i in nota["itens"]):
        return "E8"
    na_ordem = {i["sku"]: i for i in ordem["itens"]}
    # 4. SKU fora da ordem é item trocado.
    if any(i["sku"] not in na_ordem for i in nota["itens"]):
        return "E2"
    # 5. Preço unitário diferente é problema de unidade (sem conversão nem tolerância).
    if any(abs(i["preco_unitario"] - na_ordem[i["sku"]]["preco_unitario"]) > 0.001 for i in nota["itens"]):
        return "E4"
    # 6. Contagem da doca.
    receb = base.recebimento_da_nota(nota)
    if receb:
        recebido = {r["codigo_fornecedor"]: r["quantidade"] for r in receb["itens"]}
        for i in nota["itens"]:
            q = recebido.get(i["codigo_fornecedor"], 0)
            if q == 0:
                return "E1"
            if q < i["quantidade"]:
                return "E3"
    return "match"


ACAO = {"match": "receber", "E1": "receber_parcial", "E2": "receber_parcial", "E3": "receber_parcial",
        "E8": "receber_parcial", "E4": "recusar", "E5": "recusar", "E6": "recusar", "E7": "receber"}


def encaminhar(classificacao: str, valor: float) -> str:
    # Régua só por valor; não olha o tipo de exceção nem o fornecedor.
    if classificacao == "E6":
        return "bloqueio"
    if valor <= 5000:
        return "regra" if classificacao == "match" else "analista"
    if valor <= 20000:
        return "analista"
    if valor <= 100000:
        return "coordenacao"
    return "diretoria"


def main():
    base = Base()
    saida = RAIZ / "saidas" / "baseline.jsonl"
    saida.parent.mkdir(exist_ok=True)
    with open(saida, "w", encoding="utf-8") as f:
        for nota in base.notas.values():
            c = classificar(base, nota)
            f.write(json.dumps({
                "nota_id": nota["nota_id"], "classificacao": c, "acao_doca": ACAO[c],
                "encaminhamento": encaminhar(c, nota["valor_total"]), "valor_em_risco": None,
                "justificativa": "baseline de regras", "origem": "baseline"}, ensure_ascii=False) + "\n")
    print(f"Baseline gravado em {saida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
