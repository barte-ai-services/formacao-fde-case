"""Põe lado a lado a nota, a ordem e a contagem da doca de uma nota, item a item.

Mostra o fato e não classifica: imprime, para cada código do fornecedor, a quantidade e o preço
na nota, na ordem e na contagem, com as diferenças de quantidade e de valor. Não converte caixa
em unidade e não sugere ação. Lê só a base operacional em `dados/` (por `jachegou.base`), nunca
o gabarito.

Uso:
    uv run python agente/plugin/skills/classificar/scripts/comparar_itens.py NF-001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(RAIZ))

from jachegou.base import Base  # noqa: E402

VAZIO = "—"
OUTRA_UNIDADE = "unidades diferentes"


def _dif_qtd(a: dict | None, b: dict | None) -> int | str | None:
    """Diferença de quantidade entre dois documentos, só quando estão na mesma unidade."""
    if not a or not b:
        return None
    if a["unidade"] != b["unidade"]:
        return OUTRA_UNIDADE
    return a["quantidade"] - b["quantidade"]


def _centavos(valor: float) -> float:
    """Arredonda para centavos e tira o zero negativo do ponto flutuante."""
    return round(valor, 2) + 0.0


def localizar_ordem(base: Base, nota: dict, recebimento: dict | None) -> tuple[dict | None, str]:
    """A ordem citada pela nota ou, sem ela, a ordem ligada ao recebimento. Não procura outras."""
    pedido = nota.get("pedido_referenciado")
    if pedido:
        ordem = base.ordens.get(pedido)
        return ordem, f"{pedido} (citada na nota)" if ordem else f"{pedido} (citada na nota, não encontrada)"
    if recebimento and recebimento.get("ordem_id"):
        ordem = base.ordens.get(recebimento["ordem_id"])
        if ordem:
            return ordem, f"{recebimento['ordem_id']} (ligada ao recebimento; a nota não cita pedido)"
    return None, "nenhuma (a nota não cita pedido e o recebimento não aponta ordem)"


def linhas_por_item(nota: dict, ordem: dict | None, recebimento: dict | None) -> list[dict]:
    """Uma linha por código do fornecedor que aparece na nota, na ordem ou na contagem."""
    na_nota = {i["codigo_fornecedor"]: i for i in nota["itens"]}
    na_ordem = {i["codigo_fornecedor"]: i for i in (ordem or {}).get("itens", [])}
    na_doca = {i["codigo_fornecedor"]: i for i in (recebimento or {}).get("itens", [])}
    codigos = list(dict.fromkeys([*na_nota, *na_ordem, *na_doca]))
    linhas = []
    for codigo in codigos:
        n, o, d = na_nota.get(codigo), na_ordem.get(codigo), na_doca.get(codigo)
        descricao = next(x["descricao"] for x in (n, o, d) if x)
        linhas.append({
            "codigo": codigo,
            "descricao": descricao,
            "nota": n,
            "ordem": o,
            "doca": d,
            "dif_qtd_nota_ordem": _dif_qtd(n, o),
            "dif_qtd_nota_doca": _dif_qtd(n, d),
            "dif_preco_nota_ordem": _centavos(n["preco_unitario"] - o["preco_unitario"]) if n and o else None,
            "dif_valor_nota_ordem": _centavos(n["valor"] - o["quantidade"] * o["preco_unitario"]) if n and o else None,
        })
    return linhas


def _qtd(item: dict | None) -> str:
    return f"{item['quantidade']} {item['unidade']}" if item else VAZIO


def _preco(item: dict | None) -> str:
    return f"{item['preco_unitario']:.2f}" if item else VAZIO


def _dif(valor: float | int | str | None, decimais: int = 0) -> str:
    if valor is None:
        return VAZIO
    if isinstance(valor, str):
        return valor
    return f"{valor:+.{decimais}f}" if decimais else f"{valor:+d}"


def formatar(nota: dict, rotulo_ordem: str, recebimento: dict | None, linhas: list[dict]) -> str:
    contagem = (f"{recebimento['recebimento_id']} ({recebimento['canal']}, {recebimento['data']})"
                if recebimento else "nenhuma contagem registrada para esta nota")
    saida = [
        f"Nota {nota['nota_id']} · fornecedor {nota['fornecedor_id']} · destino {nota['destino']} · "
        f"valor total {nota['valor_total']:.2f}",
        f"Ordem: {rotulo_ordem}",
        f"Contagem: {contagem}",
        "",
        "| Código | Descrição | Qtd nota | Qtd ordem | Qtd doca | Nota − ordem | Nota − doca "
        "| Preço nota | Preço ordem | Dif. preço | Dif. valor (nota − ordem) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for x in linhas:
        saida.append(
            f"| {x['codigo']} | {x['descricao']} | {_qtd(x['nota'])} | {_qtd(x['ordem'])} | {_qtd(x['doca'])} "
            f"| {_dif(x['dif_qtd_nota_ordem'])} | {_dif(x['dif_qtd_nota_doca'])} "
            f"| {_preco(x['nota'])} | {_preco(x['ordem'])} | {_dif(x['dif_preco_nota_ordem'], 2)} "
            f"| {_dif(x['dif_valor_nota_ordem'], 2)} |"
        )
    saida += [
        "",
        "Quantidades na unidade de cada documento, sem conversão: quando as unidades diferem, "
        "a diferença de quantidade não é calculada. "
        "Diferença de valor: valor do item na nota menos quantidade × preço da ordem.",
    ]
    return "\n".join(saida)


def comparar(nota_id: str, base: Base | None = None) -> str:
    base = base or Base()
    nota = base.notas.get(nota_id)
    if nota is None:
        raise KeyError(f"nota {nota_id} não encontrada")
    recebimento = base.recebimento_da_nota(nota)
    ordem, rotulo = localizar_ordem(base, nota, recebimento)
    return formatar(nota, rotulo, recebimento, linhas_por_item(nota, ordem, recebimento))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Nota, ordem e contagem da doca lado a lado, item a item")
    ap.add_argument("nota_id", help="a nota, por exemplo NF-001")
    args = ap.parse_args(argv)
    try:
        print(comparar(args.nota_id))
    except KeyError as erro:
        print(erro.args[0], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
