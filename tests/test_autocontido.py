"""O kit roda inteiro dentro do Claude Code: nada no repositório chama a API, o SDK ou o `claude -p`."""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
ESTE_ARQUIVO = Path(__file__).resolve().relative_to(RAIZ).as_posix()
FORA_DA_BUSCA = {"uv.lock", ESTE_ARQUIVO}
PROIBIDOS = ("claude -p", "import anthropic", "from anthropic", "claude_agent_sdk", "ANTHROPIC_API_KEY")
PACOTES_PROIBIDOS = ("anthropic", "claude-agent-sdk", "claude_agent_sdk")


def _arquivos_versionados() -> list[Path]:
    if shutil.which("git") is None:
        pytest.skip("git não está instalado: sem git ls-files, não há lista de arquivos versionados")
    resultado = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=False)
    if resultado.returncode != 0:
        pytest.skip(f"git ls-files falhou: {resultado.stderr.decode(errors='replace').strip()}")
    nomes = [n for n in resultado.stdout.decode("utf-8").split("\0") if n]
    return [RAIZ / n for n in nomes if n not in FORA_DA_BUSCA]


def _texto(caminho: Path) -> str | None:
    """O conteúdo do arquivo como texto, ou None se ele não existe no disco ou é binário."""
    try:
        dados = caminho.read_bytes()
    except (FileNotFoundError, IsADirectoryError):
        return None
    if b"\0" in dados:
        return None
    return dados.decode("utf-8", errors="replace")


def test_nenhum_arquivo_versionado_chama_api_sdk_ou_claude_p():
    achados = []
    for caminho in _arquivos_versionados():
        texto = _texto(caminho)
        if texto is None:
            continue
        for proibido in PROIBIDOS:
            if proibido in texto:
                achados.append(f"{caminho.relative_to(RAIZ).as_posix()}: {proibido}")
    assert not achados, "o kit roda dentro do Claude Code, sem API, SDK nem claude -p:\n" + "\n".join(achados)


def _nome_do_pacote(requisito: str) -> str:
    nome = requisito.strip()
    for separador in ("[", "<", ">", "=", "!", "~", ";", " "):
        nome = nome.split(separador)[0]
    return nome.lower().replace("_", "-")


def test_pyproject_nao_depende_de_anthropic_nem_do_sdk():
    pyproject = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    projeto = pyproject.get("project", {})
    requisitos = list(projeto.get("dependencies", []))
    for grupo in projeto.get("optional-dependencies", {}).values():
        requisitos += grupo
    for grupo in pyproject.get("dependency-groups", {}).values():
        requisitos += [r for r in grupo if isinstance(r, str)]
    proibidos = {p.replace("_", "-") for p in PACOTES_PROIBIDOS}
    assert not [r for r in requisitos if _nome_do_pacote(r) in proibidos]
