"""Testes do agente no Claude Agent SDK, das skills e do comparador. Offline: não chamam a API."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from claude_agent_sdk import (  # noqa: E402
    AssistantMessage,
    ResultMessage,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from agente import rodar_agente  # noqa: E402

PLUGIN = RAIZ / "agente" / "plugin"
SKILLS = ["classificar", "propor-acao-na-doca", "encaminhar"]
COMPARADOR = PLUGIN / "skills" / "classificar" / "scripts" / "comparar_itens.py"


# ---------- as skills ----------

def _frontmatter(caminho: Path) -> dict[str, str]:
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    assert m, f"{caminho} sem frontmatter YAML"
    campos = {}
    for linha in m.group(1).splitlines():
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip()
    return campos


@pytest.mark.parametrize("skill", SKILLS)
def test_skill_no_formato_agent_skills(skill):
    """#40/AC-1: cada skill é uma pasta com SKILL.md e frontmatter name e description."""
    campos = _frontmatter(PLUGIN / "skills" / skill / "SKILL.md")
    assert campos.get("name") == skill
    descricao = campos.get("description", "")
    assert len(descricao) > 60, "a descrição diz o que a skill faz e quando usar"
    assert "Use " in descricao


def test_plugin_tem_manifesto_e_so_as_tres_skills():
    manifesto = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifesto["name"] == rodar_agente.NOME_PLUGIN
    assert sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir()) == sorted(SKILLS)
    assert not (RAIZ / "agente" / "skills").exists(), "as skills antigas em .md soltas foram removidas"


# ---------- o comparador ----------

def _comparar(nota_id: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(COMPARADOR), nota_id], capture_output=True, text=True, cwd=RAIZ, check=False)


def test_comparador_imprime_a_tabela_item_a_item():
    """#40/AC-2: o comparador roda sozinho numa nota e põe nota, ordem e doca lado a lado."""
    r = _comparar("NF-002")
    assert r.returncode == 0, r.stderr
    assert "Ordem: OC-2026-41937" in r.stdout
    assert "Contagem: RC-9111" in r.stdout
    linhas = [x for x in r.stdout.splitlines() if x.startswith("| F04-")]
    assert len(linhas) == 3
    assert "| F04-003 | Shampoo 350 ml | 128 UN | — | 128 UN |" in r.stdout


def test_comparador_nao_converte_unidade_nem_classifica():
    """#40/AC-2: mostra o fato (unidades diferentes) e não devolve classificação nem ação."""
    r = _comparar("NF-010")
    assert r.returncode == 0, r.stderr
    assert "unidades diferentes" in r.stdout
    assert not re.search(r"\b(E[1-8]|match|receber|recusar|regra|analista|coordenacao|diretoria|bloqueio)\b", r.stdout)


def test_comparador_recusa_nota_inexistente():
    r = _comparar("NF-999")
    assert r.returncode == 1
    assert "não encontrada" in r.stderr


def test_comparador_nao_le_o_gabarito():
    assert "gabarito/" not in COMPARADOR.read_text(encoding="utf-8")


# ---------- as opções do SDK ----------

def test_opcoes_do_sdk_tem_as_tres_skills_o_mcp_e_nenhuma_setting_do_disco():
    """#40/AC-3 e AC-4: plugin local com as três skills, MCP ja-chegou por stdio, setting_sources=[]."""
    o = rodar_agente.montar_opcoes("grupo-1", "teste.jsonl", modelo="modelo-x")
    assert o.setting_sources == []
    assert o.strict_mcp_config is True
    assert o.plugins == [{"type": "local", "path": str(PLUGIN.resolve())}]
    assert o.skills == [f"domingo:{s}" for s in SKILLS]
    assert o.cwd == str(RAIZ)
    assert o.model == "modelo-x"
    assert o.system_prompt == (RAIZ / "agente" / "instrucoes.md").read_text(encoding="utf-8")
    mcp = o.mcp_servers["ja-chegou"]
    assert mcp["type"] == "stdio"
    assert mcp["args"] == [str(RAIZ / "mcp_server" / "servidor.py")]
    assert mcp["env"]["FDE_ORIGEM"] == "grupo-1"
    assert mcp["env"]["FDE_ARQUIVO_PROPOSTAS"] == "teste.jsonl"
    assert set(o.tools) == {"Skill", "Read", "Bash"}
    assert "mcp__ja-chegou__*" in o.allowed_tools
    assert [r for r in o.allowed_tools if r.startswith("Bash")] == [f"Bash(uv run python {COMPARADOR.resolve()} *)"]
    assert o.permission_mode == "dontAsk"
    assert len(o.hooks["PreToolUse"]) == 1


def test_modelo_padrao_vem_de_agent_model(monkeypatch):
    monkeypatch.delenv("AGENT_MODEL", raising=False)
    assert rodar_agente.montar_opcoes("a", "b.jsonl").model == "claude-sonnet-5-5"
    monkeypatch.setenv("AGENT_MODEL", "outro")
    assert rodar_agente.montar_opcoes("a", "b.jsonl").model == "outro"


# ---------- o guarda ----------

def _decisao(ferramenta: str, entrada: dict) -> str | None:
    hook = rodar_agente.montar_opcoes("a", "b.jsonl").hooks["PreToolUse"][0].hooks[0]
    saida = asyncio.run(hook({"hook_event_name": "PreToolUse", "tool_name": ferramenta, "tool_input": entrada},
                             "t1", None))
    return saida.get("hookSpecificOutput", {}).get("permissionDecision")


@pytest.mark.parametrize(("ferramenta", "entrada"), [
    ("Read", {"file_path": "dados/gabarito/gabarito.json"}),
    ("Read", {"file_path": str(RAIZ / "dados" / "gabarito" / "gabarito.json")}),
    ("Read", {"file_path": str(RAIZ / "dados" / "x" / ".." / "gabarito" / "gabarito.json")}),
    ("Read", {"file_path": ".env"}),
    ("Grep", {"pattern": "E6", "path": "dados/gabarito"}),
    ("Glob", {"pattern": "dados/gabarito/*"}),
    ("Bash", {"command": "cat dados/gabarito/gabarito.json"}),
    ("Bash", {"command": f"uv run python {COMPARADOR} NF-001; cat dados/gabarito/gabarito.json"}),
    ("Bash", {"command": f"uv run python {COMPARADOR} NF-001 && ls"}),
    ("Bash", {"command": "ls saidas"}),
    ("Bash", {"command": f"uv run python {COMPARADOR} $(cat .env)"}),
    ("Write", {"file_path": "agente/plugin/skills/classificar/SKILL.md", "content": "x"}),
    ("Write", {"file_path": "saidas/../dados/notas.json", "content": "x"}),
    ("Edit", {"file_path": str(RAIZ / "mcp_server" / "servidor.py"), "old_string": "a", "new_string": "b"}),
    ("NotebookEdit", {"notebook_path": "/tmp/x.ipynb", "new_source": "x"}),
])
def test_guarda_nega_gabarito_escrita_fora_de_saidas_e_bash_solto(ferramenta, entrada):
    """#40/AC-4: o agente não lê dados/gabarito/ (nem via Bash) e não escreve fora de saidas/."""
    assert _decisao(ferramenta, entrada) == "deny"


@pytest.mark.parametrize(("ferramenta", "entrada"), [
    ("Read", {"file_path": str(PLUGIN / "skills" / "classificar" / "references" / "excecoes.md")}),
    ("Read", {"file_path": "dados/notas.json"}),
    ("Bash", {"command": f"uv run python {COMPARADOR} NF-001"}),
    ("Bash", {"command": "uv run python agente/plugin/skills/classificar/scripts/comparar_itens.py NF-042"}),
    ("Write", {"file_path": "saidas/rascunho.md", "content": "x"}),
    ("mcp__ja-chegou__ler_nota", {"nota_id": "NF-001"}),
    ("Skill", {"skill": "domingo:classificar"}),
])
def test_guarda_deixa_passar_o_que_o_agente_precisa(ferramenta, entrada):
    assert _decisao(ferramenta, entrada) is None


# ---------- o laço ----------

def consulta_falsa(chamadas: list):
    """Simula o SDK: sobe o servidor MCP com a configuração das opções e chama as tools de verdade.

    Testa o laço e a configuração do MCP, não a inteligência."""

    async def consulta(*, prompt, options):
        from mcp import Client, StdioServerParameters

        chamadas.append(options)
        nota_id = re.search(r"NF-\d{3}", prompt).group(0)
        cfg = options.mcp_servers["ja-chegou"]
        servidor = StdioServerParameters(command=cfg["command"], args=cfg["args"], env=cfg["env"])
        yield AssistantMessage(content=[ToolUseBlock(id="s1", name="Skill", input={"skill": "domingo:classificar"})], model="falso")
        async with Client(servidor) as mcp:
            entrada = {"nota_id": nota_id, "classificacao": "E6", "acao_doca": "recusar",
                       "encaminhamento": "bloqueio", "justificativa": "simulação do laço do agente"}
            yield AssistantMessage(content=[ToolUseBlock(id="t1", name=rodar_agente.REGISTRAR, input=entrada)], model="falso")
            r = await mcp.call_tool("registrar_proposta", entrada)
            texto = r.content[0].text
            yield UserMessage(content=[ToolResultBlock(tool_use_id="t1", content=[{"type": "text", "text": texto}])])
        yield ResultMessage(subtype="success", duration_ms=1, duration_api_ms=1, is_error=False, num_turns=2, session_id="s")

    return consulta


def test_laco_do_agente_registra_proposta_via_mcp(tmp_path, monkeypatch, capsys):
    """#40/AC-3: o agente roda pelo SDK, invoca a skill e a proposta vem de registrar_proposta."""
    monkeypatch.setenv("FDE_SAIDAS", str(tmp_path))
    chamadas: list = []
    codigo = rodar_agente.main(["--todas", "--limite", "2", "--saida", "teste.jsonl", "--origem", "grupo-9", "--verbose"],
                               consulta=consulta_falsa(chamadas))
    assert codigo == 0
    linhas = [json.loads(x) for x in (tmp_path / "teste.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [x["origem"] for x in linhas] == ["grupo-9", "grupo-9"]
    assert len(chamadas) == 2 and chamadas[0].setting_sources == []
    saida = capsys.readouterr().out
    assert "◆ skill domingo:classificar" in saida
    assert "· registrar_proposta(" in saida
    assert "E6 · recusar · bloqueio" in saida


def test_sem_proposta_registrada_devolve_erro(capsys):
    async def consulta(*, prompt, options):
        yield ResultMessage(subtype="error_max_turns", duration_ms=1, duration_api_ms=1, is_error=True, num_turns=30, session_id="s")

    assert rodar_agente.main(["--nota", "NF-001"], consulta=consulta) == 1
    assert "sem proposta registrada" in capsys.readouterr().out
