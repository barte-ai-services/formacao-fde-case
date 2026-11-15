"""Mock do motor de decisão do Grupo 1, para o Grupo 2 testar a delegação.

Segue o contrato da decisão do motor de decisão e o do pedido de delegação e
relatório. O Clef é simulado: a confiança vem do campo `clef_confidence` da
proposta de exemplo. Quando o motor real chegar, só essa fonte muda.

Rode `python motor_mock.py` para ver o relatório da delegação de exemplo.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

MODEL_VERSION = "clef-mock-0.1"
NIVEIS_FORA_DO_MOTOR = {"diretoria", "bloqueio"}


@dataclass
class Criterios:
    """Parâmetros do motor, que mudam sem deploy."""

    excecoes_delegaveis: set = field(default_factory=lambda: {"E1", "E3", "E4"})
    teto_valor_em_risco: float = 20_000.0
    teto_valor_da_nota: float = 100_000.0
    limite_confianca: dict = field(default_factory=lambda: {"analista": 0.98})
    delegacao_ligada: dict = field(default_factory=lambda: {"analista": True})


class Banco:
    """O banco, em memória: propostas, pedidos de delegação e decisões."""

    def __init__(self, propostas: list[dict]):
        self.propostas = {p["invoice_access_key"]: dict(p) for p in propostas}
        self.pedidos: list[dict] = []
        self.decisoes: list[dict] = []

    def gravar_delegacao(self, requested_by: str, invoice_access_keys=None,
                         classification=None, dry_run: bool = False) -> str:
        """O que `delegate_to_engine` faz: grava o pedido. Não chama o motor."""
        delegation_id = f"del-{len(self.pedidos) + 1}"
        self.pedidos.append({
            "delegation_id": delegation_id,
            "requested_by": requested_by,
            "invoice_access_keys": list(invoice_access_keys or []),
            "classification": list(classification or []),
            "dry_run": dry_run,
            "processado": False,
        })
        return delegation_id

    def pedido(self, delegation_id: str) -> dict:
        return next(p for p in self.pedidos if p["delegation_id"] == delegation_id)


def _decisao(proposta: dict, pedido: dict, outcome: str, decided_by: str, reason: str,
             mode: str, confidence: Optional[float] = None, pending_reason: Optional[str] = None,
             recommendation: Optional[str] = None) -> dict:
    return {
        "invoice_access_key": proposta["invoice_access_key"],
        "outcome": outcome,
        "decided_by": decided_by,
        "confidence": confidence,
        "model_version": MODEL_VERSION,
        "mode": mode,
        "reason": reason,
        "pending_reason": pending_reason,
        "recommendation": recommendation,
        "similar_cases": [],
        "delegation_id": pedido["delegation_id"],
    }


def avaliar(proposta: dict, pedido: dict, criterios: Criterios) -> Optional[dict]:
    """A cascata regra → Clef → pessoa para uma proposta. None = fora do motor."""
    nivel = proposta["level"]
    if proposta.get("decided") or nivel in NIVEIS_FORA_DO_MOTOR:
        return None

    mode = "shadow" if pedido["dry_run"] or not criterios.delegacao_ligada.get(nivel, False) else "delegated"

    # Nunca chegam ao Clef: duplicidade, fornecedor bloqueado e nota acima do teto.
    if (proposta["classification"] == "E6" or proposta.get("supplier_blocked")
            or proposta.get("invoice_value", 0) > criterios.teto_valor_da_nota):
        return _decisao(proposta, pedido, "pending", "rule", "Fora dos critérios do motor: vai para a pessoa.",
                        mode, pending_reason="outside_criteria")
    if (proposta["classification"] not in criterios.excecoes_delegaveis
            or proposta["amount_at_risk"] > criterios.teto_valor_em_risco):
        return _decisao(proposta, pedido, "pending", "rule",
                        f"{proposta['classification']} com R$ {proposta['amount_at_risk']:.2f} em risco está fora dos critérios.",
                        mode, pending_reason="outside_criteria")
    if nivel not in criterios.limite_confianca:
        return _decisao(proposta, pedido, "pending", "rule", f"O nível {nivel} não é delegável.",
                        mode, pending_reason="level_not_delegable")

    confianca = proposta.get("clef_confidence")
    if confianca is None:
        return _decisao(proposta, pedido, "pending", "person", "O Clef não respondeu; a proposta segue para a pessoa.",
                        mode, pending_reason="below_confidence", recommendation="Revisar")

    limite = criterios.limite_confianca[nivel]
    if confianca < limite:
        return _decisao(proposta, pedido, "pending", "clef",
                        f"Confiança {confianca:.2f} abaixo de {limite:.2f}. {proposta['evidence']}",
                        mode, confidence=confianca, pending_reason="below_confidence",
                        recommendation="Aprovar" if confianca >= 0.9 else "Revisar")
    if mode == "shadow" and not pedido["dry_run"]:
        return _decisao(proposta, pedido, "pending", "clef",
                        f"Delegação desligada para {nivel}: o motor só simula. {proposta['evidence']}",
                        mode, confidence=confianca, pending_reason="delegation_off", recommendation="Aprovar")
    return _decisao(proposta, pedido, "approve", "clef", proposta["evidence"], mode, confidence=confianca)


class MotorMock:
    def __init__(self, criterios: Optional[Criterios] = None, ligado: bool = True):
        self.criterios = criterios or Criterios()
        self.ligado = ligado

    def processar(self, banco: Banco) -> int:
        """Lê os pedidos ainda não processados e grava as decisões. Devolve quantos processou."""
        if not self.ligado:
            return 0
        feitos = 0
        for pedido in banco.pedidos:
            if pedido["processado"]:
                continue
            for proposta in _propostas_do_pedido(banco, pedido):
                decisao = avaliar(proposta, pedido, self.criterios)
                if decisao is None:
                    continue
                banco.decisoes.append(decisao)
                if decisao["outcome"] == "approve" and decisao["mode"] == "delegated":
                    banco.propostas[proposta["invoice_access_key"]]["decided"] = True
                    banco.propostas[proposta["invoice_access_key"]]["decided_by_engine"] = True
            pedido["processado"] = True
            feitos += 1
        return feitos


def _propostas_do_pedido(banco: Banco, pedido: dict) -> list[dict]:
    chaves = pedido["invoice_access_keys"] or list(banco.propostas)
    props = [banco.propostas[k] for k in chaves if k in banco.propostas]
    if pedido["classification"]:
        props = [p for p in props if p["classification"] in pedido["classification"]]
    return props


def _linha(proposta: dict, decisao: Optional[dict] = None) -> dict:
    linha = {k: proposta.get(k) for k in
             ("invoice_access_key", "number", "supplier_id", "classification", "dock_action", "amount_at_risk")}
    if decisao:
        linha.update({k: decisao[k] for k in ("confidence", "reason", "similar_cases")})
    return linha


def relatorio(banco: Banco, delegation_id: str, motor_ligado: bool = True) -> dict:
    """O que `delegate_to_engine` devolve ao analista, lido das decisões gravadas."""
    pedido = banco.pedido(delegation_id)
    base = {"delegation_id": delegation_id, "requested_by": pedido["requested_by"],
            "dry_run": pedido["dry_run"]}
    if not pedido["processado"]:
        base["status"] = "Motor indisponível" if not motor_ligado else "O motor está avaliando"
        return base

    decisoes = [d for d in banco.decisoes if d["delegation_id"] == delegation_id]
    por_chave = {d["invoice_access_key"]: d for d in decisoes}
    approved, pending, skipped = [], [], []
    for proposta in _propostas_do_pedido(banco, pedido):
        d = por_chave.get(proposta["invoice_access_key"])
        if d is None:
            motivo = "já decidida" if proposta.get("decided") else proposta["level"]
            skipped.append({**_linha(proposta), "motivo": motivo})
        elif d["outcome"] == "approve":
            approved.append(_linha(proposta, d))
        else:
            pending.append({**_linha(proposta, d), "pending_reason": d["pending_reason"],
                            "recommendation": d["recommendation"]})

    def total(grupo):
        return {"quantidade": len(grupo), "valor_em_risco": round(sum(x["amount_at_risk"] for x in grupo), 2)}

    base.update({
        "status": "Simulação da delegação · nada foi aprovado" if pedido["dry_run"] else "Delegação concluída",
        "evaluated": len(decisoes),
        "approved": approved,
        "pending": pending,
        "skipped": skipped,
        "totals": {"approved": total(approved), "pending": total(pending), "skipped": total(skipped)},
    })
    return base


def carregar_exemplos(caminho: Optional[Path] = None) -> list[dict]:
    caminho = caminho or Path(__file__).with_name("propostas_exemplo.json")
    return json.loads(caminho.read_text(encoding="utf-8"))


if __name__ == "__main__":
    banco = Banco(carregar_exemplos())
    dry = "--simular" in sys.argv
    delegacao = banco.gravar_delegacao("analista@jachegou.example", dry_run=dry)
    MotorMock().processar(banco)
    print(json.dumps(relatorio(banco, delegacao), ensure_ascii=False, indent=2))
