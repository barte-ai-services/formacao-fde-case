"""Ponto de partida do agente de check antecipado da Já Chegou, rodando no Claude Agent SDK.

Um agente, três skills (classificar, propor a ação na doca, encaminhar), tools por MCP.
O prompt de sistema é agente/instrucoes.md. As skills ficam no plugin local agente/plugin/, no
formato Agent Skills: o modelo vê o nome e a descrição de cada uma e só carrega o SKILL.md
quando decide usá-la (tool `Skill`).
O trabalho do grupo no domingo é melhorar as skills com a camada de contexto de sábado e medir
cada versão com o eval.

Uso:
    cp .env.example .env                      # e preencha ANTHROPIC_API_KEY
    uv run python agente/rodar_agente.py --nota NF-001 --verbose
    uv run python agente/rodar_agente.py --todas --limite 10
    uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shlex
import sys
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from claude_agent_sdk import (  # noqa: E402
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

MAX_TURNOS = 30
PLUGIN = RAIZ / "agente" / "plugin"
NOME_PLUGIN = "domingo"
SKILLS = ("classificar", "propor-acao-na-doca", "encaminhar")
SERVIDOR_MCP = "ja-chegou"
REGISTRAR = f"mcp__{SERVIDOR_MCP}__registrar_proposta"

GABARITO = RAIZ / "dados" / "gabarito"
SAIDAS = RAIZ / "saidas"
SEGREDOS = RAIZ / ".env"
FERRAMENTAS_DE_ESCRITA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

Consulta = Callable[..., AsyncIterator[Any]]


def comparador(pasta_plugin: Path = PLUGIN) -> Path:
    return pasta_plugin / "skills" / "classificar" / "scripts" / "comparar_itens.py"


# ---------- o guarda ----------

def _dentro(caminho: Path, pasta: Path) -> bool:
    return caminho == pasta or pasta in caminho.parents


def _resolver(bruto: str) -> Path:
    caminho = Path(bruto)
    return (caminho if caminho.is_absolute() else RAIZ / caminho).resolve()


def _proibido_ler(caminho: Path) -> bool:
    return _dentro(caminho, GABARITO.resolve()) or caminho == SEGREDOS.resolve()


def _bash_permitido(comando: str, script: Path) -> bool:
    """Só o comparador de itens, numa nota, sem encadear outro comando."""
    if re.search(r"[;&|`$<>\n]", comando):
        return False
    try:
        partes = shlex.split(comando)
    except ValueError:
        return False
    prefixos = (["uv", "run", "python"], ["python"], ["python3"])
    for prefixo in prefixos:
        if partes[: len(prefixo)] == prefixo and len(partes) == len(prefixo) + 2:
            alvo, nota = partes[len(prefixo)], partes[-1]
            return _resolver(alvo) == script.resolve() and re.fullmatch(r"NF-\d{3}", nota) is not None
    return False


def decidir(ferramenta: str, entrada: dict, script: Path) -> str | None:
    """Devolve o motivo da recusa, ou None se a chamada pode seguir."""
    if ferramenta in FERRAMENTAS_DE_ESCRITA:
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if not alvo or not _dentro(_resolver(alvo), SAIDAS.resolve()):
            return "o agente só escreve em saidas/"
        return None
    if ferramenta == "Bash":
        comando = entrada.get("command", "")
        if "gabarito" in comando or not _bash_permitido(comando, script):
            return "o Bash só roda o comparador de itens da skill classificar, numa nota"
        return None
    for chave in ("file_path", "path", "notebook_path"):
        if entrada.get(chave) and _proibido_ler(_resolver(entrada[chave])):
            return "o gabarito e o .env não são lidos pelo agente"
    if "gabarito" in json.dumps(entrada, ensure_ascii=False) and ferramenta in {"Read", "Glob", "Grep"}:
        return "o gabarito não é lido pelo agente"
    return None


def criar_guarda(script: Path):
    """Hook PreToolUse: nega leitura do gabarito, escrita fora de saidas/ e Bash fora do comparador."""

    async def guarda(entrada_hook: dict, tool_use_id: str | None, contexto: Any) -> dict:
        motivo = decidir(entrada_hook.get("tool_name", ""), entrada_hook.get("tool_input") or {}, script)
        if motivo is None:
            return {}
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": motivo}}

    return guarda


# ---------- as opções do SDK ----------

def montar_opcoes(origem: str, saida: str, modelo: str | None = None, pasta_plugin: Path | None = None) -> ClaudeAgentOptions:
    plugin = (pasta_plugin or PLUGIN).resolve()
    ambiente_mcp = {"FDE_ORIGEM": origem, "FDE_ARQUIVO_PROPOSTAS": saida}
    for chave in ("FDE_DADOS", "FDE_SAIDAS"):
        if os.environ.get(chave):
            ambiente_mcp[chave] = os.environ[chave]
    return ClaudeAgentOptions(
        model=modelo or os.environ.get("AGENT_MODEL", "claude-sonnet-5-5"),
        system_prompt=(RAIZ / "agente" / "instrucoes.md").read_text(encoding="utf-8"),
        cwd=str(RAIZ),
        # Nada do disco: nem .claude/settings.json (e os plugins que ele habilita), nem CLAUDE.md.
        setting_sources=[],
        strict_mcp_config=True,
        plugins=[{"type": "local", "path": str(plugin)}],
        skills=[f"{NOME_PLUGIN}:{s}" for s in SKILLS],
        mcp_servers={SERVIDOR_MCP: {"type": "stdio", "command": sys.executable,
                                     "args": [str(RAIZ / "mcp_server" / "servidor.py")], "env": ambiente_mcp}},
        tools=["Skill", "Read", "Bash"],
        allowed_tools=[f"mcp__{SERVIDOR_MCP}__*", "Read", f"Bash(uv run python {comparador(plugin)} *)"],
        permission_mode="dontAsk",
        hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[criar_guarda(comparador(plugin))])]},
        max_turns=MAX_TURNOS,
    )


# ---------- o laço ----------

def _texto(conteudo: Any) -> str:
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        return "\n".join(c.get("text", "") for c in conteudo if isinstance(c, dict))
    return ""


def _proposta_do_resultado(conteudo: Any) -> dict | None:
    try:
        dado = json.loads(_texto(conteudo))
    except json.JSONDecodeError:
        return None
    dado = dado.get("result", dado) if isinstance(dado, dict) else {}
    return dado.get("proposta") if isinstance(dado, dict) and dado.get("registrada") else None


def _mostrar(bloco: ToolUseBlock) -> None:
    if bloco.name == "Skill":
        print(f"  ◆ skill {bloco.input.get('skill') or bloco.input.get('command') or bloco.input}")
    else:
        print(f"  · {bloco.name.removeprefix(f'mcp__{SERVIDOR_MCP}__')}"
              f"({json.dumps(bloco.input, ensure_ascii=False)[:90]})")


async def analisar_nota(consulta: Consulta, opcoes: ClaudeAgentOptions, nota_id: str, verbose: bool = False) -> dict | None:
    """Roda o agente numa nota. Devolve a proposta que `registrar_proposta` aceitou, ou None."""
    pedido = (f"Faça o check antecipado da nota {nota_id}. Use as tools para reunir as evidências, "
              "aplique as três skills e termine registrando a proposta com registrar_proposta.")
    registros: set[str] = set()
    proposta = None
    async for mensagem in consulta(prompt=pedido, options=opcoes):
        if isinstance(mensagem, AssistantMessage):
            for bloco in mensagem.content:
                if isinstance(bloco, ToolUseBlock):
                    if verbose:
                        _mostrar(bloco)
                    if bloco.name == REGISTRAR:
                        registros.add(bloco.id)
        elif isinstance(mensagem, UserMessage) and isinstance(mensagem.content, list):
            for bloco in mensagem.content:
                if isinstance(bloco, ToolResultBlock) and bloco.tool_use_id in registros:
                    proposta = _proposta_do_resultado(bloco.content) or proposta
        elif isinstance(mensagem, ResultMessage) and verbose and mensagem.is_error:
            print(f"  ! o agente terminou com erro: {mensagem.subtype}")
    return proposta


def _notas_pendentes(limite: int | None) -> list[str]:
    from jachegou.base import Base
    notas = list(Base().notas)
    return notas[:limite] if limite else notas


async def principal(args, consulta: Consulta) -> int:
    opcoes = montar_opcoes(args.origem, args.saida, pasta_plugin=args.skills)
    notas = _notas_pendentes(args.limite) if args.todas else [args.nota]
    sem_proposta = 0
    for nota_id in notas:
        print(f"{nota_id}…")
        p = await analisar_nota(consulta, opcoes, nota_id, verbose=args.verbose)
        if p:
            print(f"  {p['classificacao']} · {p['acao_doca']} · {p['encaminhamento']}")
        else:
            sem_proposta += 1
            print("  sem proposta registrada")
    print(f"\nPropostas em saidas/{args.saida}. Meça com: uv run python eval/avaliar.py saidas/{args.saida} --comparar saidas/baseline.jsonl")
    return 1 if sem_proposta else 0


def main(argv=None, consulta: Consulta | None = None) -> int:
    """`consulta` é o ponto de injeção para teste sem rede: por padrão, `claude_agent_sdk.query`."""
    ap = argparse.ArgumentParser(description="Agente de check antecipado da Já Chegou")
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--nota", help="uma nota, por exemplo NF-001")
    grupo.add_argument("--todas", action="store_true", help="todas as notas pendentes")
    ap.add_argument("--limite", type=int, help="com --todas, analisa só as N primeiras")
    ap.add_argument("--skills", type=Path, help="pasta do plugin com as skills (padrão: agente/plugin)")
    ap.add_argument("--saida", default="propostas.jsonl", help="arquivo em saidas/ onde as propostas são gravadas")
    ap.add_argument("--origem", default="agente", help="rótulo gravado em cada proposta, por exemplo o nome do grupo")
    ap.add_argument("--verbose", action="store_true", help="mostra cada tool chamada e cada skill invocada")
    args = ap.parse_args(argv)
    if consulta is None:
        from claude_agent_sdk import query
        from dotenv import load_dotenv
        load_dotenv(RAIZ / ".env")
        consulta = query
    return asyncio.run(principal(args, consulta))


if __name__ == "__main__":
    sys.exit(main())
