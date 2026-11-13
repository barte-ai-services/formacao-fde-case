"""O kit roda inteiro dentro do Claude Code: nada no repositório chama a API, o SDK ou o `claude -p`."""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTE_ARQUIVO = Path(__file__).resolve().relative_to(RAIZ).as_posix()
FORA_DA_BUSCA = {"uv.lock", ESTE_ARQUIVO}
PROIBIDOS = re.compile(
    r"\bclaude\s+(-p|--print)\b"
    r"|\b(import|from)\s+anthropic\b"
    r"|claude[_-]agent[_-]sdk"
    r"|ANTHROPIC_API_KEY"
    r"|api\.anthropic\.com"
    r"|@anthropic-ai/"
)
PASTAS_FORA = {".git", ".venv", "__pycache__", ".pytest_cache", "saidas"}
LOCAIS_FORA = {".env"}  # o .env é local, nunca versionado: o aluno guarda nele o que quiser
PACOTES_PROIBIDOS = ("anthropic", "claude-agent-sdk", "claude_agent_sdk")


def _arquivos_do_disco() -> list[Path]:
    """Sem git, varre o disco: um checkout sem .git (um zip do repositório público) também fica travado."""
    return [c for c in RAIZ.rglob("*")
            if c.is_file()
            and not PASTAS_FORA & set(c.relative_to(RAIZ).parts)
            and c.relative_to(RAIZ).as_posix() not in FORA_DA_BUSCA | LOCAIS_FORA]


def _arquivos_versionados() -> list[Path]:
    """Os arquivos do `git ls-files`; sem git ou fora de um repositório, os arquivos do disco."""
    if shutil.which("git") is None:
        return _arquivos_do_disco()
    resultado = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=False)
    if resultado.returncode != 0:
        return _arquivos_do_disco()
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
        for achado in PROIBIDOS.finditer(texto):
            achados.append(f"{caminho.relative_to(RAIZ).as_posix()}: {achado.group(0)}")
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


def test_a_trava_pega_as_variantes():
    for proibido in ("claude -p x", "claude  --print x", "import anthropic", "from anthropic import X",
                     "claude-agent-sdk", "claude_agent_sdk", "ANTHROPIC_API_KEY", "https://api.anthropic.com/v1",
                     "@anthropic-ai/sdk"):
        assert PROIBIDOS.search(proibido), proibido
    for permitido in ("abra o Claude Code (`claude`)", "claude --version", "subagente do Claude Code"):
        assert not PROIBIDOS.search(permitido), permitido


def test_sem_git_a_busca_cai_para_o_disco(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    nomes = {c.relative_to(RAIZ).as_posix() for c in _arquivos_versionados()}
    assert "DOMINGO.md" in nomes and ".claude/commands/auditar-lote.md" in nomes
    assert ESTE_ARQUIVO not in nomes and "uv.lock" not in nomes
    assert not any(n.startswith((".git/", ".venv/")) for n in nomes)
