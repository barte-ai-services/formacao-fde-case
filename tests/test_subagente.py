"""Testes do subagente do Claude Code, das skills e da tool comparar_itens. Offline: não rodam o agente."""

from __future__ import annotations

import asyncio
import re
import sys
import tomllib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

AGENTE = RAIZ / ".claude" / "agents" / "auditor-de-notas.md"
SKILLS_DIR = RAIZ / ".claude" / "skills"
SKILLS = ["classificar-divergencia", "decidir-recebimento", "definir-aprovador"]
SERVIDOR = "ja-chegou"
FERRAMENTAS_DE_DISCO = {"Read", "Bash", "Write", "Edit", "MultiEdit", "NotebookEdit", "Glob", "Grep", "LSP", "PowerShell"}
RESPOSTA = re.compile(r"\b(E[1-8]|match|receber|receber_parcial|recusar|regra|analista|coordenacao|diretoria|bloqueio)\b")


def _frontmatter(caminho: Path) -> tuple[dict[str, str | list[str]], str]:
    """Lê o frontmatter YAML simples destes arquivos: `chave: valor` ou `chave:` seguida de itens `- x`."""
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    assert m, f"{caminho} sem frontmatter YAML"
    campos: dict[str, str | list[str]] = {}
    chave = None
    for linha in m.group(1).splitlines():
        if linha.startswith("  - ") and chave:
            lista = campos.setdefault(chave, [])
            assert isinstance(lista, list), f"{chave} mistura valor e lista"
            lista.append(linha[4:].strip())
            continue
        chave, _, valor = linha.partition(":")
        chave = chave.strip()
        if valor.strip():
            campos[chave] = valor.strip()
    return campos, m.group(2)


def _lista(valor: str | list[str] | None) -> list[str]:
    if valor is None:
        return []
    return valor if isinstance(valor, list) else [v.strip() for v in valor.split(",") if v.strip()]


def test_agente_tem_nome_descricao_e_corpo():
    campos, corpo = _frontmatter(AGENTE)
    assert campos["name"] == "auditor-de-notas"
    descricao = campos["description"]
    assert isinstance(descricao, str) and "Use " in descricao and len(descricao) > 60
    assert ": " not in descricao, "dois-pontos com espaço quebra o YAML do frontmatter"
    assert "registrar_proposta" in corpo, "o prompt de sistema é o corpo do arquivo"


SECOES = ["O que este agente é", "Antes de começar", "Entradas", "Procedimento", "Quando terminou",
          "Quando bloqueado", "Saída", "O que não faz", "Exemplo"]


def test_prompt_segue_o_esqueleto_de_agente():
    """O corpo tem as seções do esqueleto, nesta ordem, e o resumo de três linhas num template literal."""
    _, corpo = _frontmatter(AGENTE)
    assert re.findall(r"^## (.+)$", corpo, re.M) == SECOES
    assert "Você é o auditor de notas do check antecipado do contas a pagar da Já Chegou" in corpo
    for skill in SKILLS:
        assert f"`{skill}`" in corpo.split("## Entradas")[0], f"{skill} fora de antes de começar"
    blocos = re.findall(r"```text\n(.*?)\n```", corpo.split("## Saída")[1].split("## O que não faz")[0], re.S)
    assert [b.count("\n") + 1 for b in blocos] == [3, 3]
    assert blocos[0].startswith("Proposta registrada · ") and blocos[1].startswith("Proposta não registrada · ")
    assert corpo.count("<example>") >= 1


def test_agente_so_usa_as_tools_do_ja_chegou():
    """Sem Read, Bash, Write, Edit, Glob e Grep, o agente não alcança dados/gabarito/ nem escreve fora de saidas/."""
    campos, _ = _frontmatter(AGENTE)
    tools = _lista(campos.get("tools"))
    assert tools == [f"mcp__{SERVIDOR}__*"]
    assert not FERRAMENTAS_DE_DISCO & set(tools)
    assert "Skill" not in tools, "as skills entram pelo campo skills; sem Skill, o agente não invoca outras"
    assert "disallowedTools" not in campos and "permissionMode" not in campos


def test_agente_nao_carrega_os_claude_md():
    """O CLAUDE.md do projeto e o da conta do aluno não entram no contexto do subagente."""
    campos, _ = _frontmatter(AGENTE)
    assert campos.get("omitClaudeMd") == "true"


LACO = (
    'claude -p "Use o subagente auditor-de-notas para fazer o check antecipado da nota $nota e registrar a proposta." \\\n'
    '    --allowedTools "Agent" "mcp__ja-chegou__*"'
)


def test_laco_despacha_o_subagente_de_uma_sessao_normal():
    """O laço usa o caminho documentado: a sessão despacha o subagente, com o pedido antes do --allowedTools."""
    texto = (RAIZ / "DOMINGO.md").read_text(encoding="utf-8")
    assert LACO in texto
    comando = LACO.replace("\\\n", " ")
    assert comando.index('-p "') < comando.index("--allowedTools"), "--allowedTools aceita uma lista e engoliria o pedido"


@pytest.mark.parametrize("arquivo", ["DOMINGO.md", "README.md"])
def test_documentacao_nao_roda_o_agente_como_sessao_principal(arquivo):
    """Com --agent, o preload das skills na sessão principal não está documentado; o laço não depende dele."""
    assert "--agent" not in (RAIZ / arquivo).read_text(encoding="utf-8")


def test_mcp_json_passa_origem_e_arquivo_ao_servidor():
    """O laço do DOMINGO.md troca o rótulo e o arquivo das propostas por variável de ambiente."""
    import json

    env = json.loads((RAIZ / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"][SERVIDOR]["env"]
    assert env == {"FDE_ORIGEM": "${FDE_ORIGEM:-agente}", "FDE_ARQUIVO_PROPOSTAS": "${FDE_ARQUIVO_PROPOSTAS:-propostas.jsonl}"}


def test_agente_carrega_as_tres_skills():
    campos, _ = _frontmatter(AGENTE)
    assert _lista(campos.get("skills")) == SKILLS
    for skill in SKILLS:
        assert (SKILLS_DIR / skill / "SKILL.md").is_file()


def test_agente_nao_cita_o_gabarito():
    assert "gabarito" not in AGENTE.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("skill", SKILLS)
def test_skill_no_formato_agent_skills(skill):
    """#40/AC-1: cada skill é uma pasta com SKILL.md e frontmatter name e description."""
    campos, corpo = _frontmatter(SKILLS_DIR / skill / "SKILL.md")
    assert campos.get("name") == skill
    descricao = campos.get("description", "")
    assert isinstance(descricao, str) and len(descricao) > 60, "a descrição diz o que a skill faz e quando usar"
    assert "Use " in descricao
    assert re.match(r"^[^.?]*\?", descricao), "a description abre com a pergunta que a skill responde"
    assert corpo.strip()
    assert re.search(r"^# Skill [123] — ", corpo, re.M), "o título numerado fica"


def test_so_as_tres_skills_e_nada_que_o_agente_nao_consiga_ler():
    """O agente não tem Read nem Bash: o que a skill precisa está no SKILL.md ou numa tool do ja-chegou."""
    assert sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir()) == sorted(SKILLS)
    for skill in SKILLS:
        assert [p.name for p in (SKILLS_DIR / skill).iterdir()] == ["SKILL.md"]


def test_classificar_divergencia_cita_a_tool_e_nao_um_script():
    texto = (SKILLS_DIR / "classificar-divergencia" / "SKILL.md").read_text(encoding="utf-8")
    assert "`comparar_itens`" in texto
    assert "uv run" not in texto and "scripts/" not in texto
    for codigo in ("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"):
        assert f"| {codigo} |" in texto


def test_o_harness_antigo_saiu():
    """O agente roda dentro do Claude Code: não há script nem SDK do agente no projeto."""
    assert not (RAIZ / "agente").exists()
    pyproject = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert not [d for d in pyproject["project"]["dependencies"] if d.startswith(("claude", "anthropic"))]


def _comparar(nota_id: str) -> str:
    """Chama a tool pelo cliente MCP, como o agente chama."""
    from mcp import Client

    from mcp_server import servidor as mod

    async def rodar() -> str:
        async with Client(mod.servidor) as c:
            nomes = {t.name for t in (await c.list_tools()).tools}
            assert "comparar_itens" in nomes
            r = await c.call_tool("comparar_itens", {"nota_id": nota_id})
            return r.content[0].text

    return asyncio.run(rodar())


def test_comparar_itens_poe_nota_ordem_e_doca_lado_a_lado():
    """#40/AC-2: numa nota real, a tool mostra os três documentos item a item."""
    saida = _comparar("NF-002")
    assert "Ordem: OC-2026-41937" in saida
    assert "Contagem: RC-9111" in saida
    linhas = [x for x in saida.splitlines() if x.startswith("| F04-")]
    assert len(linhas) == 3
    assert "| F04-003 | Shampoo 350 ml | 128 UN | — | 128 UN |" in saida


def test_comparar_itens_nao_classifica_nem_converte_unidade():
    """#40/AC-2: mostra o fato (unidades diferentes) e não devolve classificação, ação nem nível."""
    saida = _comparar("NF-010")
    assert "unidades diferentes" in saida
    assert not RESPOSTA.search(saida)


def test_comparar_itens_nao_devolve_resposta_em_nenhuma_nota():
    from jachegou.base import Base
    from jachegou.comparar import comparar

    base = Base()
    for nota_id in base.notas:
        assert not RESPOSTA.search(comparar(nota_id, base)), nota_id


def test_comparar_itens_sem_pedido_na_nota_nao_compara_com_ordem():
    """O que fazer quando a nota não cita o pedido é do grupo: a tool só diz o fato."""
    saida = _comparar("NF-007")
    assert "Ordem: a nota não cita pedido" in saida
    assert all("| — |" in x for x in saida.splitlines() if x.startswith("| F"))


def test_comparar_itens_nota_inexistente():
    assert _comparar("NF-999") == "nota NF-999 não encontrada"


def test_comparador_nao_le_o_gabarito():
    assert "gabarito/" not in (RAIZ / "jachegou" / "comparar.py").read_text(encoding="utf-8")
