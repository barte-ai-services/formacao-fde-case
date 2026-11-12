"""Testes da base de domingo, do servidor MCP e do laço do agente. Offline: não chamam a API."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from jachegou.base import ACOES, CLASSIFICACOES, NIVEIS, Base  # noqa: E402

DADOS = RAIZ / "dados"


@pytest.fixture(scope="module")
def base():
    return Base(DADOS)


GABARITO = DADOS / "gabarito" / "gabarito.json"


@pytest.fixture(scope="module")
def gabarito():
    if not GABARITO.exists():
        pytest.skip("o gabarito só chega no domingo")
    return json.loads(GABARITO.read_text(encoding="utf-8"))


def test_composicao(base, gabarito):
    assert 75 <= len(base.notas) <= 90
    assert {g["nota_id"] for g in gabarito} == set(base.notas)
    c = Counter(g["classificacao"] for g in gabarito)
    for e in ("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"):
        assert c[e] >= 8, f"{e} com menos de 8 notas"
    assert c["match"] >= 5


def test_gabarito_usa_os_valores_validos(gabarito):
    for g in gabarito:
        assert g["classificacao"] in CLASSIFICACOES
        assert g["acao_doca"] in ACOES
        assert g["encaminhamento"] in NIVEIS
        assert g["explicacao"]


def test_regua_do_servidor_bate_com_o_gabarito(base, gabarito, monkeypatch):
    monkeypatch.setenv("FDE_DADOS", str(DADOS))
    from mcp_server import servidor
    for g in gabarito:
        assert servidor.nivel_minimo(g["classificacao"], base.notas[g["nota_id"]]) == g["encaminhamento"]


def test_ids_das_notas_nao_revelam_o_tipo(base):
    assert all(re.fullmatch(r"NF-\d{3}", n) for n in base.notas)


# Montados por partes para este arquivo não conter os nomes que ele mesmo proíbe.
PROIBIDOS = [r"rap" + "pi", r"\bri" + r"za\b", r"\bpa" + r"x\b", r"sal" + "lve", r"\bco" + r"mp\b", r"mon" + "key"]


def test_sem_nomes_de_clientes_de_origem():
    for arquivo in list(DADOS.rglob("*.json")) + list(DADOS.rglob("*.csv")):
        texto = arquivo.read_text(encoding="utf-8").lower()
        for padrao in PROIBIDOS:
            assert not re.search(padrao, texto), f"{padrao} em {arquivo.name}"


def test_servidor_mcp_expoe_as_tools_e_trava_a_regua(tmp_path, monkeypatch):
    monkeypatch.setenv("FDE_SAIDAS", str(tmp_path))
    from mcp import Client
    from mcp_server import servidor as mod
    monkeypatch.setattr(mod, "SAIDAS", tmp_path)

    async def rodar():
        async with Client(mod.servidor) as c:
            nomes = {t.name for t in (await c.list_tools()).tools}
            assert {"ler_nota", "ler_ordem", "ler_recebimento", "consultar_cadastro", "registrar_proposta"} <= nomes
            assert not any(p in n for n in nomes for p in ("aprovar", "pagar", "baixar"))
            nota = json.loads((await c.call_tool("ler_nota", {"nota_id": "NF-001"})).content[0].text)
            assert nota["nota_id"] == "NF-001"
            recusa = await c.call_tool("registrar_proposta", {"nota_id": "NF-001", "classificacao": "E6", "acao_doca": "recusar",
                                                               "encaminhamento": "regra", "justificativa": "teste da trava da régua"})
            assert '"registrada": false' in recusa.content[0].text
            ok = await c.call_tool("registrar_proposta", {"nota_id": "NF-001", "classificacao": "E6", "acao_doca": "recusar",
                                                           "encaminhamento": "bloqueio", "justificativa": "teste da trava da régua"})
            assert '"registrada": true' in ok.content[0].text
    asyncio.run(rodar())
    linhas = [json.loads(x) for x in (tmp_path / "propostas.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(x["encaminhamento"], x.get("recusada")) for x in linhas] == [("regra", "regua"), ("bloqueio", None)]


class LLMFalso:
    """Simula o modelo: lê a nota e registra uma proposta. Testa o laço, não a inteligência."""

    def __init__(self):
        self.messages = self
        self.chamadas = 0

    def create(self, **kw):
        self.chamadas += 1
        nota_id = re.search(r"NF-\d{3}", kw["messages"][0]["content"]).group(0)
        if self.chamadas % 2 == 1:
            bloco = {"type": "tool_use", "id": f"t{self.chamadas}", "name": "ler_nota", "input": {"nota_id": nota_id}}
        else:
            bloco = {"type": "tool_use", "id": f"t{self.chamadas}", "name": "registrar_proposta",
                     "input": {"nota_id": nota_id, "classificacao": "E6", "acao_doca": "recusar",
                               "encaminhamento": "bloqueio", "justificativa": "simulação do laço do agente"}}
        return SimpleNamespace(content=[bloco], stop_reason="tool_use")


def test_laco_do_agente_registra_proposta_via_mcp(tmp_path, monkeypatch):
    monkeypatch.setenv("FDE_SAIDAS", str(tmp_path))
    from agente import rodar_agente
    codigo = rodar_agente.main(["--todas", "--limite", "2", "--saida", "teste.jsonl"], llm=LLMFalso())
    assert codigo == 0
    linhas = (tmp_path / "teste.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 2


def test_sistema_inclui_as_tres_skills():
    from agente.rodar_agente import montar_sistema
    s = montar_sistema()
    for titulo in ("Skill 1", "Skill 2", "Skill 3"):
        assert titulo in s


def test_recusa_da_regua_nao_revela_o_nivel(base, monkeypatch, tmp_path):
    """Se a recusa disser o nível mínimo, o agente se corrige sozinho e a skill 3 deixa de ser medida."""
    monkeypatch.setenv("FDE_DADOS", str(DADOS))
    from mcp_server import servidor
    monkeypatch.setattr(servidor, "SAIDAS", tmp_path)
    nota_id = next(n for n in base.notas if servidor.nivel_minimo("E5", base.notas[n]) != "regra")
    r = servidor.registrar_proposta(nota_id, "E5", "recusar", "regra", "teste da recusa pela régua")
    assert r["registrada"] is False
    assert "régua" in r["erro"]
    for nivel in ("analista", "coordenacao", "diretoria", "bloqueio"):
        assert nivel not in r["erro"]


def test_recusa_da_regua_fica_gravada(base, monkeypatch, tmp_path):
    monkeypatch.setenv("FDE_DADOS", str(DADOS))
    monkeypatch.setenv("FDE_ARQUIVO_PROPOSTAS", "teste.jsonl")
    from mcp_server import servidor
    monkeypatch.setattr(servidor, "SAIDAS", tmp_path)
    nota_id = next(n for n in base.notas if servidor.nivel_minimo("E5", base.notas[n]) != "regra")
    minimo = servidor.nivel_minimo("E5", base.notas[nota_id])
    servidor.registrar_proposta(nota_id, "E5", "recusar", "regra", "primeira tentativa, abaixo da régua")
    servidor.registrar_proposta(nota_id, "E5", "recusar", minimo, "segunda tentativa, no nível da régua")
    linhas = [json.loads(x) for x in (tmp_path / "teste.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [x.get("recusada") for x in linhas] == ["regua", None]


def test_eval_mede_o_encaminhamento_na_primeira_tentativa(tmp_path):
    from eval.avaliar import avaliar_arquivo
    gabarito = [{"nota_id": n, "chave": n, "classificacao": "E5", "acao_doca": "recusar", "encaminhamento": "coordenacao",
                 "valor_em_risco": 0.0, "explicacao": "-"} for n in ("NF-001", "NF-002")]
    linhas = [
        {"nota_id": "NF-001", "classificacao": "E5", "acao_doca": "recusar", "encaminhamento": "regra", "recusada": "regua"},
        {"nota_id": "NF-001", "classificacao": "E5", "acao_doca": "recusar", "encaminhamento": "coordenacao"},
        {"nota_id": "NF-002", "classificacao": "E5", "acao_doca": "recusar", "encaminhamento": "coordenacao"},
    ]
    arquivo = tmp_path / "propostas.jsonl"
    arquivo.write_text("\n".join(json.dumps(x) for x in linhas), encoding="utf-8")
    r = avaliar_arquivo(arquivo, gabarito)
    assert r["campos"]["encaminhamento"] == 2
    assert r["encaminhamento_primeira"] == 1
    assert r["notas_com_recusa"] == 1
