"""Servidor MCP do caso Já Chegou: as tools do agente de check antecipado.

Leitura: notas pendentes, ordens, recebimentos, cadastro, fornecedores, notas já lançadas,
pagamentos fora do fluxo e a régua de alçadas.
Escrita: só `registrar_proposta`, que grava a proposta do agente em saidas/propostas.jsonl.

Não existe tool para aprovar, pagar, baixar ou escrever no ERP. A trava fica no sistema, não só
nas instruções do agente: `registrar_proposta` recusa encaminhamento abaixo do que a régua exige.

Rodar sozinho (stdio):  uv run python mcp_server/servidor.py
No Claude Code: o arquivo .mcp.json na raiz já aponta para este servidor.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from jachegou.base import ACOES, CLASSIFICACOES, NIVEIS, Base  # noqa: E402

base = Base()
SAIDAS = Path(os.environ.get("FDE_SAIDAS") or RAIZ / "saidas")

servidor = MCPServer(
    name="ja-chegou",
    instructions=(
        "Dados da Já Chegou para o check antecipado de notas fiscais de mercadoria. "
        "Leia a nota, a ordem, o recebimento e o cadastro antes de concluir. "
        "Termine cada nota com registrar_proposta. Não há como aprovar ou pagar: o agente só propõe."
    ),
)


def _resumo_nota(n: dict) -> dict:
    return {k: n[k] for k in ("nota_id", "numero", "serie", "fornecedor_id", "destino", "data_emissao",
                               "pedido_referenciado", "canal_entrada", "valor_total")} | {"itens": len(n["itens"])}


@servidor.tool()
def listar_notas_pendentes(destino: str | None = None, fornecedor_id: str | None = None) -> list[dict]:
    """Lista as notas de mercadoria que chegaram e ainda não passaram pelo check antecipado.

    Filtros opcionais: destino (ex.: CD-01, LJ-007) e fornecedor_id (ex.: F05)."""
    return [_resumo_nota(n) for n in base.notas.values()
            if (destino is None or n["destino"] == destino) and (fornecedor_id is None or n["fornecedor_id"] == fornecedor_id)]


@servidor.tool()
def ler_nota(nota_id: str) -> dict:
    """Lê uma nota fiscal pendente inteira: cabeçalho, número do pedido citado (pode vir vazio) e itens.

    Itens trazem codigo_fornecedor, sku (vazio quando o código do fornecedor não tem cadastro),
    quantidade, unidade (UN ou CX), preço unitário e valor."""
    n = base.notas.get(nota_id)
    if n is None:
        return {"erro": f"nota {nota_id} não encontrada"}
    return n


@servidor.tool()
def ler_ordem(ordem_id: str) -> dict:
    """Lê uma ordem de compra: fornecedor, destino, status (aberta, travada ou atendida), itens em unidade e preço por unidade."""
    o = base.ordens.get(ordem_id)
    return o if o else {"erro": f"ordem {ordem_id} não encontrada"}


@servidor.tool()
def buscar_ordens(fornecedor_id: str, destino: str | None = None, status: str | None = None) -> list[dict]:
    """Busca ordens de compra de um fornecedor, com filtro opcional por destino e status.

    Use quando a nota não cita o pedido: a ordem pode existir mesmo assim."""
    return base.ordens_do_fornecedor(fornecedor_id, destino, status)


@servidor.tool()
def ler_recebimento(nota_id: str) -> dict:
    """Lê a contagem da doca (CD) ou do app (loja) registrada para a nota, item a item.

    Devolve vazio se a mercadoria ainda não foi contada. O WMS registra na unidade da nota, sem converter caixa em unidade."""
    n = base.notas.get(nota_id)
    if n is None:
        return {"erro": f"nota {nota_id} não encontrada"}
    r = base.recebimento_da_nota(n)
    return r or {"situacao": "sem contagem registrada para esta nota"}


@servidor.tool()
def buscar_recebimentos_sem_nota(fornecedor_id: str, destino: str) -> list[dict]:
    """Recebimentos de um fornecedor num destino que ainda não estão ligados a nenhuma nota.

    Na loja, a mercadoria às vezes entra antes de a nota chegar."""
    return base.recebimentos_sem_nota(fornecedor_id, destino)


@servidor.tool()
def consultar_cadastro(sku: str | None = None, codigo_fornecedor: str | None = None, fornecedor_id: str | None = None) -> list[dict]:
    """Consulta o cadastro de produtos por SKU, pelo código do fornecedor ou pelo fornecedor.

    Cada produto traz a unidade base (UN) e quantas unidades vêm numa caixa (fator_caixa).
    Lista vazia significa que o item não tem cadastro."""
    return [p for p in base.produtos
            if (sku is None or p["sku"] == sku)
            and (codigo_fornecedor is None or p["codigo_fornecedor"] == codigo_fornecedor)
            and (fornecedor_id is None or p["fornecedor_id"] == fornecedor_id)]


@servidor.tool()
def ler_fornecedor(fornecedor_id: str) -> dict:
    """Lê o cadastro do fornecedor, inclusive se os pagamentos a ele estão bloqueados."""
    f = base.fornecedores.get(fornecedor_id)
    return f if f else {"erro": f"fornecedor {fornecedor_id} não encontrado"}


@servidor.tool()
def buscar_notas_lancadas(fornecedor_id: str, numero: int | None = None, pedido: str | None = None) -> list[dict]:
    """Notas do fornecedor que já foram lançadas no ERP ou pagas, com filtros opcionais por número e pedido citado."""
    return [n for n in base.lancadas_do_fornecedor(fornecedor_id)
            if (numero is None or n["numero"] == numero) and (pedido is None or n["pedido_referenciado"] == pedido)]


@servidor.tool()
def buscar_pagamentos_fora_do_fluxo(fornecedor_id: str, destino: str | None = None) -> list[dict]:
    """Pagamentos feitos fora do fluxo do contas a pagar (pix ou boleto avulso das lojas), ainda sem nota vinculada."""
    return base.pagamentos_fora_do_fluxo(fornecedor_id, destino)


@servidor.tool()
def ler_regua() -> dict:
    """Régua de alçadas e tolerâncias vigentes: quem decide cada caso e o que o agente pode fazer."""
    return base.regua


def nivel_minimo(classificacao: str, nota: dict) -> str:
    """O nível mais baixo que a régua aceita. O agente pode subir um caso, nunca descer."""
    r = base.regua
    if classificacao == "E6":
        return "bloqueio"
    if nota["valor_total"] > r["teto_coordenacao"] or base.fornecedores[nota["fornecedor_id"]]["bloqueado"]:
        return "diretoria"
    if classificacao in {"E5", "E7", "E8"}:
        return "coordenacao"
    if classificacao in {"E1", "E2", "E3", "E4"}:
        return "analista" if nota["valor_total"] <= r["teto_analista"] else "coordenacao"
    return "regra"


@servidor.tool()
def registrar_proposta(nota_id: str, classificacao: str, acao_doca: str, encaminhamento: str,
                       justificativa: str, valor_em_risco: float | None = None) -> dict:
    """Registra a proposta do agente para uma nota. É a única escrita disponível: nada é aprovado nem pago.

    classificacao: match, E1, E2, E3, E4, E5, E6, E7 ou E8.
    acao_doca: receber, receber_parcial (com nota de devolução) ou recusar.
    encaminhamento: regra, analista, coordenacao, diretoria ou bloqueio.
    justificativa: as evidências, em poucas linhas.
    valor_em_risco: quanto a Já Chegou pagaria a mais se a nota passasse como veio (opcional)."""
    nota = base.notas.get(nota_id)
    if nota is None:
        return {"registrada": False, "erro": f"nota {nota_id} não encontrada"}
    problemas = []
    if classificacao not in CLASSIFICACOES:
        problemas.append(f"classificacao deve ser uma de {CLASSIFICACOES}")
    if acao_doca not in ACOES:
        problemas.append(f"acao_doca deve ser uma de {ACOES}")
    if encaminhamento not in NIVEIS:
        problemas.append(f"encaminhamento deve ser um de {NIVEIS}")
    if not justificativa or len(justificativa.strip()) < 10:
        problemas.append("justificativa precisa citar as evidências")
    if not problemas:
        minimo = nivel_minimo(classificacao, nota)
        if NIVEIS.index(encaminhamento) < NIVEIS.index(minimo):
            problemas.append(f"a régua não permite encaminhar {classificacao} desta nota para '{encaminhamento}'; consulte a régua")
    if problemas:
        return {"registrada": False, "erro": "; ".join(problemas)}
    SAIDAS.mkdir(parents=True, exist_ok=True)
    proposta = {"nota_id": nota_id, "classificacao": classificacao, "acao_doca": acao_doca,
                "encaminhamento": encaminhamento, "valor_em_risco": valor_em_risco,
                "justificativa": justificativa.strip(), "origem": os.environ.get("FDE_ORIGEM", "agente"),
                "registrado_em": datetime.now().isoformat(timespec="seconds")}
    with open(SAIDAS / os.environ.get("FDE_ARQUIVO_PROPOSTAS", "propostas.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(proposta, ensure_ascii=False) + "\n")
    return {"registrada": True, "proposta": proposta}


if __name__ == "__main__":
    servidor.run("stdio")
