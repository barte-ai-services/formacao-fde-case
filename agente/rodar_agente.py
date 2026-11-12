"""Ponto de partida do agente de check antecipado da Já Chegou.

Um agente, três skills (classificar, propor a ação na doca, encaminhar), tools por MCP.
O agente lê as instruções em agente/instrucoes.md e as skills em agente/skills/*.md.
O trabalho do grupo no domingo é melhorar as skills com a camada de contexto de sábado e medir
cada versão com o eval.

Uso:
    cp .env.example .env                      # e preencha ANTHROPIC_API_KEY
    uv run python agente/rodar_agente.py --nota NF-001
    uv run python agente/rodar_agente.py --todas --limite 10
    uv run python eval/avaliar.py saidas/propostas.jsonl --comparar saidas/baseline.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

MAX_TURNOS = 16


def montar_sistema(pasta_skills: Path | None = None) -> str:
    pasta = pasta_skills or RAIZ / "agente" / "skills"
    partes = [(RAIZ / "agente" / "instrucoes.md").read_text(encoding="utf-8")]
    for skill in sorted(pasta.glob("*.md")):
        partes.append(f"\n\n---\n\n{skill.read_text(encoding='utf-8')}")
    return "".join(partes)


def _campo(bloco, nome):
    return bloco.get(nome) if isinstance(bloco, dict) else getattr(bloco, nome, None)


def _para_dict(bloco) -> dict:
    if isinstance(bloco, dict):
        return bloco
    return bloco.model_dump(exclude_none=True)


def _texto_do_resultado(resultado) -> str:
    estruturado = getattr(resultado, "structured_content", None)
    if estruturado is not None:
        valor = estruturado.get("result", estruturado) if isinstance(estruturado, dict) else estruturado
        return json.dumps(valor, ensure_ascii=False)
    return "\n".join(getattr(c, "text", "") for c in resultado.content)


async def analisar_nota(llm, mcp, ferramentas: list[dict], sistema: str, modelo: str, nota_id: str, verbose: bool = False) -> dict | None:
    """Roda o agente numa nota até ele registrar a proposta. Devolve a proposta registrada, ou None."""
    mensagens = [{"role": "user", "content": (
        f"Faça o check antecipado da nota {nota_id}. Use as tools para reunir as evidências, "
        "aplique as três skills e termine registrando a proposta com registrar_proposta.")}]
    for _ in range(MAX_TURNOS):
        resposta = llm.messages.create(model=modelo, max_tokens=4096, system=sistema, tools=ferramentas, messages=mensagens)
        conteudo = [_para_dict(b) for b in resposta.content]
        mensagens.append({"role": "assistant", "content": conteudo})
        chamadas = [b for b in conteudo if b.get("type") == "tool_use"]
        if not chamadas:
            break
        resultados, proposta = [], None
        for c in chamadas:
            r = await mcp.call_tool(c["name"], c.get("input") or {})
            texto = _texto_do_resultado(r)
            if verbose:
                print(f"  · {c['name']}({json.dumps(c.get('input'), ensure_ascii=False)[:90]})")
            if c["name"] == "registrar_proposta":
                dado = json.loads(texto) if texto.startswith("{") else {}
                if dado.get("registrada"):
                    proposta = dado["proposta"]
            resultados.append({"type": "tool_result", "tool_use_id": c["id"], "content": texto,
                               "is_error": bool(getattr(r, "is_error", False))})
        mensagens.append({"role": "user", "content": resultados})
        if proposta:
            return proposta
    return None


async def principal(args) -> int:
    from dotenv import load_dotenv
    from mcp import Client, StdioServerParameters

    load_dotenv(RAIZ / ".env")
    if args.llm is None:
        import anthropic
        llm = anthropic.Anthropic()
    else:
        llm = args.llm
    modelo = os.environ.get("AGENT_MODEL", "claude-sonnet-5-5")
    ambiente = dict(os.environ) | {"FDE_ORIGEM": args.origem, "FDE_ARQUIVO_PROPOSTAS": args.saida}
    servidor = StdioServerParameters(command=sys.executable, args=[str(RAIZ / "mcp_server" / "servidor.py")], env=ambiente)
    sistema = montar_sistema(args.skills)
    async with Client(servidor) as mcp:
        lista = await mcp.list_tools()
        ferramentas = [{"name": t.name, "description": t.description or "", "input_schema": t.input_schema} for t in lista.tools]
        if args.todas:
            r = await mcp.call_tool("listar_notas_pendentes", {})
            notas = [n["nota_id"] for n in json.loads(_texto_do_resultado(r))]
            if args.limite:
                notas = notas[: args.limite]
        else:
            notas = [args.nota]
        sem_proposta = 0
        for nota_id in notas:
            print(f"{nota_id}…")
            p = await analisar_nota(llm, mcp, ferramentas, sistema, modelo, nota_id, verbose=args.verbose)
            if p:
                print(f"  {p['classificacao']} · {p['acao_doca']} · {p['encaminhamento']}")
            else:
                sem_proposta += 1
                print("  sem proposta registrada")
    print(f"\nPropostas em saidas/{args.saida}. Meça com: uv run python eval/avaliar.py saidas/{args.saida} --comparar saidas/baseline.jsonl")
    return 1 if sem_proposta else 0


def main(argv=None, llm=None) -> int:
    ap = argparse.ArgumentParser(description="Agente de check antecipado da Já Chegou")
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--nota", help="uma nota, por exemplo NF-001")
    grupo.add_argument("--todas", action="store_true", help="todas as notas pendentes")
    ap.add_argument("--limite", type=int, help="com --todas, analisa só as N primeiras")
    ap.add_argument("--skills", type=Path, help="pasta com as skills (padrão: agente/skills)")
    ap.add_argument("--saida", default="propostas.jsonl", help="arquivo em saidas/ onde as propostas são gravadas")
    ap.add_argument("--origem", default="agente", help="rótulo gravado em cada proposta, por exemplo o nome do grupo")
    ap.add_argument("--verbose", action="store_true", help="mostra cada tool chamada")
    args = ap.parse_args(argv)
    args.llm = llm
    return asyncio.run(principal(args))


if __name__ == "__main__":
    sys.exit(main())
