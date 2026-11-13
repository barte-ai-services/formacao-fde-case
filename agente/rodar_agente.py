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
import sys
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from claude_agent_sdk import (  # noqa: E402
    AssistantMessage,
    ClaudeAgentOptions,
    HookCallback,
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

SAIDAS = RAIZ / "saidas"
FERRAMENTAS_DE_ESCRITA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
FERRAMENTAS_DE_LEITURA = {"Read", "Glob", "Grep"}
FERRAMENTAS_LIVRES = {"Skill"}

Consulta = Callable[..., AsyncIterator[Any]]
Mostrar = Callable[[ToolUseBlock], None]


def comparador(pasta_plugin: Path = PLUGIN) -> Path:
    return pasta_plugin / "skills" / "classificar" / "scripts" / "comparar_itens.py"


def _dentro(caminho: Path, pasta: Path) -> bool:
    return caminho == pasta or pasta in caminho.parents


def _resolver(bruto: str) -> Path:
    caminho = Path(bruto)
    return (caminho if caminho.is_absolute() else RAIZ / caminho).resolve()


def formas_do_comparador(script: Path) -> list[str]:
    """Os comandos aceitos para o comparador: o caminho absoluto e, dentro do repositório, o relativo."""
    absoluto = script.resolve()
    formas = [f"uv run python {absoluto}"]
    if _dentro(absoluto, RAIZ):
        formas.append(f"uv run python {absoluto.relative_to(RAIZ)}")
    return formas


def _bash_permitido(comando: str, script: Path) -> bool:
    """Só o comparador de itens numa nota, sem encadear outro comando."""
    if re.search(r"[;&|`$<>\n\\'\"]", comando):
        return False
    prefixo, _, nota = comando.strip().rpartition(" ")
    return prefixo in formas_do_comparador(script) and re.fullmatch(r"NF-\d{3}", nota) is not None


def decidir(ferramenta: str, entrada: dict, plugin: Path) -> str | None:
    """Devolve o motivo da recusa, ou None se a chamada pode seguir. Nega por padrão.

    Os dados vêm pelo MCP; do disco, o agente só lê o plugin (as references das skills).
    """
    if ferramenta in FERRAMENTAS_LIVRES or ferramenta.startswith(f"mcp__{SERVIDOR_MCP}__"):
        return None
    if ferramenta in FERRAMENTAS_DE_ESCRITA:
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        return None if alvo and _dentro(_resolver(alvo), SAIDAS.resolve()) else "o agente só escreve em saidas/"
    if ferramenta == "Bash":
        if _bash_permitido(entrada.get("command", ""), comparador(plugin)):
            return None
        return "o Bash só roda o comparador de itens da skill classificar, numa nota"
    if ferramenta in FERRAMENTAS_DE_LEITURA:
        alvo = entrada.get("file_path") or entrada.get("path") or ""
        if alvo and _dentro(_resolver(alvo), plugin.resolve()) and "gabarito" not in alvo.lower():
            return None
        return "o agente só lê os arquivos das skills; os dados vêm pelas tools do ja-chegou"
    return f"a ferramenta {ferramenta} não está liberada para o agente"


def criar_guarda(plugin: Path) -> HookCallback:
    """Hook PreToolUse: nega o que não é das skills, do MCP, do comparador ou escrita em saidas/."""

    async def guarda(entrada_hook: dict, tool_use_id: str | None, contexto: Any) -> dict:
        motivo = decidir(entrada_hook.get("tool_name", ""), entrada_hook.get("tool_input") or {}, plugin)
        if motivo is None:
            return {}
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": motivo}}

    return guarda


def montar_opcoes(origem: str, saida: str, modelo: str | None = None, pasta_plugin: Path | None = None) -> ClaudeAgentOptions:
    """Opções do agente: nada vem do disco, nem `.claude/settings.json` (e os plugins do Ahrena
    que ele habilita) nem `CLAUDE.md`; as skills entram só pelo plugin local."""
    plugin = (pasta_plugin or PLUGIN).resolve()
    ambiente_mcp = {"FDE_ORIGEM": origem, "FDE_ARQUIVO_PROPOSTAS": saida}
    for chave in ("FDE_DADOS", "FDE_SAIDAS"):
        if os.environ.get(chave):
            ambiente_mcp[chave] = os.environ[chave]
    return ClaudeAgentOptions(
        model=modelo or os.environ.get("AGENT_MODEL", "claude-sonnet-5-5"),
        system_prompt=(RAIZ / "agente" / "instrucoes.md").read_text(encoding="utf-8"),
        cwd=str(RAIZ),
        setting_sources=[],
        strict_mcp_config=True,
        plugins=[{"type": "local", "path": str(plugin)}],
        skills=[f"{NOME_PLUGIN}:{s}" for s in SKILLS],
        mcp_servers={SERVIDOR_MCP: {"type": "stdio", "command": sys.executable,
                                     "args": [str(RAIZ / "mcp_server" / "servidor.py")], "env": ambiente_mcp}},
        tools=["Skill", "Read", "Bash"],
        allowed_tools=[f"mcp__{SERVIDOR_MCP}__*", "Read",
                       *(f"Bash({forma} *)" for forma in formas_do_comparador(comparador(plugin)))],
        permission_mode="dontAsk",
        hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[criar_guarda(plugin)])]},
        max_turns=MAX_TURNOS,
    )


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


def _ids_de_registro(mensagem: AssistantMessage) -> set[str]:
    return {b.id for b in mensagem.content if isinstance(b, ToolUseBlock) and b.name == REGISTRAR}


def _proposta_em(mensagem: UserMessage, registros: set[str]) -> dict | None:
    if not isinstance(mensagem.content, list):
        return None
    resultados = [b for b in mensagem.content if isinstance(b, ToolResultBlock) and b.tool_use_id in registros]
    return next((p for p in (_proposta_do_resultado(b.content) for b in resultados) if p), None)


def _calado(bloco: ToolUseBlock) -> None:
    return None


async def analisar_nota(consulta: Consulta, opcoes: ClaudeAgentOptions, nota_id: str, mostrar: Mostrar = _calado) -> dict | None:
    """Roda o agente numa nota. Devolve a proposta que `registrar_proposta` aceitou, ou None."""
    pedido = (f"Faça o check antecipado da nota {nota_id}. Use as tools para reunir as evidências, "
              "aplique as três skills e termine registrando a proposta com registrar_proposta.")
    registros: set[str] = set()
    proposta = None
    async for mensagem in consulta(prompt=pedido, options=opcoes):
        if isinstance(mensagem, AssistantMessage):
            for bloco in (b for b in mensagem.content if isinstance(b, ToolUseBlock)):
                mostrar(bloco)
            registros |= _ids_de_registro(mensagem)
        elif isinstance(mensagem, UserMessage):
            proposta = _proposta_em(mensagem, registros) or proposta
        elif isinstance(mensagem, ResultMessage) and mensagem.is_error:
            print(f"  ! o agente terminou com erro: {mensagem.subtype}")
    return proposta


def _notas_pendentes(limite: int | None) -> list[str]:
    from jachegou.base import Base
    notas = list(Base().notas)
    return notas[:limite] if limite else notas


async def principal(args: argparse.Namespace, consulta: Consulta) -> int:
    opcoes = montar_opcoes(args.origem, args.saida, pasta_plugin=args.skills)
    notas = _notas_pendentes(args.limite) if args.todas else [args.nota]
    sem_proposta = 0
    for nota_id in notas:
        print(f"{nota_id}…")
        p = await analisar_nota(consulta, opcoes, nota_id, mostrar=_mostrar if args.verbose else _calado)
        if p:
            print(f"  {p['classificacao']} · {p['acao_doca']} · {p['encaminhamento']}")
        else:
            sem_proposta += 1
            print("  sem proposta registrada")
    print(f"\nPropostas em saidas/{args.saida}. Meça com: uv run python eval/avaliar.py saidas/{args.saida} --comparar saidas/baseline.jsonl")
    return 1 if sem_proposta else 0


def main(argv: list[str] | None = None, consulta: Consulta | None = None) -> int:
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
