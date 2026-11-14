"""Testes da skill setup-fde (formacao-fde-ops#50). Offline: a suíte do script roda numa caixa de areia de dublês."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / ".claude" / "skills" / "setup-fde"
SCRIPT = SKILL / "scripts" / "setup-fde.sh"
SUITE = SKILL / "scripts" / "test-setup-fde.sh"
GATILHOS = ("configura o meu setup", "setup de FDE", "o que falta instalar", "meu ambiente não funciona")
PROIBIDOS = re.compile(r"aws|terraform|docker|colima|ghcr|cfn-lint|session-manager", re.I)
PEDIDO = "configura o meu setup de FDE"
INSTALAR_CLAUDE = "curl -fsSL https://claude.ai/install.sh | bash"


def _frontmatter(caminho: Path) -> tuple[dict[str, str], str]:
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    assert m, f"{caminho} sem frontmatter YAML"
    campos = {}
    for linha in m.group(1).splitlines():
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip()
    return campos, m.group(2)


def test_skill_tem_nome_e_descricao_que_disparam():
    """#50/AC-1: o SKILL.md existe, se chama setup-fde e a descrição tem os pedidos da turma."""
    campos, corpo = _frontmatter(SKILL / "SKILL.md")
    assert set(campos) == {"name", "description"}
    assert campos["name"] == "setup-fde"
    descricao = campos["description"]
    assert ": " not in descricao, "dois-pontos com espaço quebra o YAML do frontmatter"
    for gatilho in GATILHOS:
        assert gatilho in descricao, gatilho
    assert corpo.strip()


@pytest.mark.skipif(shutil.which("bash") is None, reason="a suíte do script precisa do bash")
def test_suite_do_script_passa():
    """#50/AC-2, AC-3 e AC-6: a suíte do script roda no make check."""
    resultado = subprocess.run(["bash", str(SUITE)], capture_output=True, text=True, check=False)
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert resultado.stdout.strip().endswith("all passed")


def test_script_tem_check_e_fix():
    """#50/AC-2 e AC-3: o script tem os dois comandos e os itens do case."""
    texto = SCRIPT.read_text(encoding="utf-8")
    assert "check) report" in texto and "fix)" in texto
    for item in ("git", "gh", "uv", "python", "claude", "git-identity", "gh-login", "case-clone", "uv-sync", "check-setup", "ahrena"):
        assert re.search(rf"\b{re.escape(item)}\b", texto), item


def test_nenhum_item_fala_do_que_e_do_time():
    """#50/AC-4: a skill não fala de nuvem, de contêiner nem de registro de imagens."""
    achados = []
    for caminho in SKILL.rglob("*"):
        if caminho.is_file():
            for achado in PROIBIDOS.finditer(caminho.read_text(encoding="utf-8")):
                achados.append(f"{caminho.relative_to(RAIZ).as_posix()}: {achado.group(0)}")
    assert not achados, "\n".join(achados)


def test_skill_nunca_faz_login_nem_pede_segredo():
    """#50/AC-5: a regra de segurança está no SKILL.md, e o script não roda login."""
    _, corpo = _frontmatter(SKILL / "SKILL.md")
    assert "Nunca faça um login pela pessoa" in corpo
    assert "Nunca peça para colar um token, uma senha ou uma chave na conversa" in corpo
    codigo = [linha for linha in SCRIPT.read_text(encoding="utf-8").splitlines() if not linha.lstrip().startswith("#")]
    chamadas = [linha for linha in codigo if re.search(r"^\s*[^'\"]*\bgh auth (login|refresh)\b", linha)]
    assert not chamadas, chamadas


@pytest.mark.parametrize("arquivo", ["README.md", "SETUP.md"])
def test_documentacao_aponta_para_a_skill(arquivo):
    """#50/AC-7 e AC-8: instala o Claude Code, pede o setup na pasta do case, e sem o prazo de quinta."""
    texto = (RAIZ / arquivo).read_text(encoding="utf-8")
    assert PEDIDO in texto
    assert INSTALAR_CLAUDE in texto
    assert "12/11" not in texto


def test_settings_liga_a_athena_e_o_argos() -> None:
    """formacao-fde-ops#56/AC-1: o case liga os plugins de que o CLAUDE.md depende, e o bloco do Ahrena está no CLAUDE.md."""
    plugins = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))["enabledPlugins"]
    for plugin in ("ahrena-engineering-development", "ahrena-engineering-code-review", "ahrena-engineering-data"):
        assert plugins.get(f"{plugin}@ahrena") is True, plugin
    claude = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- ahrena:agency:start -->" in claude and "ahrena-engineering-development:athena" in claude


def test_setup_explica_o_ahrena() -> None:
    """formacao-fde-ops#56/AC-5: o SETUP.md diz o que é o Ahrena e como confirmar com /agents e a Athena."""
    texto = (RAIZ / "SETUP.md").read_text(encoding="utf-8")
    assert "## O Ahrena no Claude Code" in texto
    assert "`/agents`" in texto and "athena" in texto


def test_settings_local_fica_fora_do_git() -> None:
    """formacao-fde-ops#56/AC-3: o fix instala no escopo local, e o settings.local.json não entra no fork."""
    assert ".claude/settings.local.json" in (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_agents_md_tem_a_diretiva_do_ahrena() -> None:
    """formacao-fde-ops#65/AC-1: o AGENTS.md tem o bloco que o instalador do Ahrena escreve, como o CLAUDE.md."""
    for arquivo in ("AGENTS.md", "CLAUDE.md"):
        texto = (RAIZ / arquivo).read_text(encoding="utf-8")
        assert "<!-- ahrena:agency:start -->" in texto and "<!-- ahrena:agency:end -->" in texto, arquivo
