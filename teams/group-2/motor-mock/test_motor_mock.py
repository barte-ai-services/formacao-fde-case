"""Casos de validação do mock do motor, com a resposta esperada de cada um.

Rode com: uv run pytest teams/group-2/motor-mock
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from motor_mock import Banco, Criterios, MotorMock, carregar_exemplos, relatorio  # noqa: E402


def delegar(dry_run=False, motor=None, criterios=None, **filtros):
    banco = Banco(carregar_exemplos())
    delegation_id = banco.gravar_delegacao("analista@jachegou.example", dry_run=dry_run, **filtros)
    motor = motor or MotorMock(criterios)
    motor.processar(banco)
    return banco, relatorio(banco, delegation_id, motor_ligado=motor.ligado)


def chaves(grupo):
    return {linha["invoice_access_key"] for linha in grupo}


def test_aprova_dentro_dos_criterios():
    _, rel = delegar()
    assert chaves(rel["approved"]) == {"NF-E4-OK", "NF-E1-OK"}
    assert all(linha["confidence"] >= 0.98 for linha in rel["approved"])


def test_devolve_a_fila_abaixo_da_confianca_com_recomendacao():
    _, rel = delegar()
    pend = {linha["invoice_access_key"]: linha for linha in rel["pending"]}
    assert pend["NF-E3-BAIXA"]["pending_reason"] == "below_confidence"
    assert pend["NF-E3-BAIXA"]["recommendation"] == "Aprovar"


def test_fora_dos_criterios_volta_para_a_pessoa():
    _, rel = delegar()
    pend = {linha["invoice_access_key"]: linha["pending_reason"] for linha in rel["pending"]}
    assert pend["NF-E4-ACIMA"] == "outside_criteria"
    assert pend["NF-E5"] == "outside_criteria"


def test_diretoria_e_bloqueio_ficam_fora_do_motor():
    banco, rel = delegar()
    fora = {linha["invoice_access_key"]: linha["motivo"] for linha in rel["skipped"]}
    assert fora["NF-DIRETORIA"] == "diretoria"
    assert fora["NF-BLOQUEIO"] == "bloqueio"
    assert not banco.propostas["NF-DIRETORIA"].get("decided")
    assert not banco.propostas["NF-BLOQUEIO"].get("decided")


def test_falha_do_clef_segue_para_a_pessoa():
    _, rel = delegar()
    pend = {linha["invoice_access_key"]: linha for linha in rel["pending"]}
    assert pend["NF-CLEF-FALHOU"]["recommendation"] == "Revisar"


def test_proposta_ja_decidida_nao_e_reavaliada():
    _, rel = delegar()
    fora = {linha["invoice_access_key"]: linha["motivo"] for linha in rel["skipped"]}
    assert fora["NF-JA-DECIDIDA"] == "já decidida"


def test_aprovacao_registra_motor_confianca_e_versao():
    banco, _ = delegar()
    d = next(x for x in banco.decisoes if x["invoice_access_key"] == "NF-E4-OK")
    assert (d["outcome"], d["decided_by"], d["mode"]) == ("approve", "clef", "delegated")
    assert d["model_version"] and d["delegation_id"] == "del-1"
    assert banco.propostas["NF-E4-OK"]["decided_by_engine"] is True


def test_simulacao_nao_aprova_nada():
    banco, rel = delegar(dry_run=True)
    assert rel["status"].startswith("Simulação")
    assert chaves(rel["approved"]) == {"NF-E4-OK", "NF-E1-OK"}
    assert not any(p.get("decided_by_engine") for p in banco.propostas.values())


def test_delegacao_desligada_so_simula():
    criterios = Criterios(delegacao_ligada={"analista": False})
    banco, rel = delegar(criterios=criterios)
    assert rel["approved"] == []
    pend = {linha["invoice_access_key"]: linha["pending_reason"] for linha in rel["pending"]}
    assert pend["NF-E4-OK"] == "delegation_off"
    assert not any(p.get("decided_by_engine") for p in banco.propostas.values())


def test_motor_desligado_mostra_indisponivel():
    banco, rel = delegar(motor=MotorMock(ligado=False))
    assert rel["status"] == "Motor indisponível"
    assert banco.decisoes == []


def test_delegar_duas_vezes_nao_aprova_duas_vezes():
    banco = Banco(carregar_exemplos())
    motor = MotorMock()
    banco.gravar_delegacao("analista@jachegou.example")
    motor.processar(banco)
    segunda = banco.gravar_delegacao("analista@jachegou.example")
    motor.processar(banco)
    rel = relatorio(banco, segunda)
    assert rel["approved"] == []
    aprovadas = [d for d in banco.decisoes if d["outcome"] == "approve"]
    assert len(aprovadas) == 2


def test_filtro_por_excecao():
    _, rel = delegar(classification=["E4"])
    todas = chaves(rel["approved"]) | chaves(rel["pending"]) | chaves(rel["skipped"])
    assert todas == {"NF-E4-OK", "NF-E4-ACIMA", "NF-CLEF-FALHOU", "NF-JA-DECIDIDA"}


def test_totais_batem_com_as_linhas():
    _, rel = delegar()
    assert rel["totals"]["approved"]["quantidade"] == 2
    assert rel["totals"]["approved"]["valor_em_risco"] == round(1418.56 + 860.00, 2)
