"""Lista os plugins do Ahrena que o case liga e que o Claude Code ainda não tem.

    claude plugin list --json | python3 ahrena_faltando.py <pasta do case>

Lê os plugins `<nome>@ahrena` ligados no `.claude/settings.json` do case e a
lista do Claude Code na entrada. Um plugin conta quando está instalado e
habilitado para a pessoa inteira (escopo `user`) ou para a pasta do case.
Imprime os nomes que faltam, separados por espaço; não imprime nada quando não
falta nenhum. Sai 2 quando não consegue ler a lista do Claude Code.
"""

from __future__ import annotations

import json
import os
import sys


def ligados(case: str) -> list[str]:
    caminho = os.path.join(case, ".claude", "settings.json")
    with open(caminho, encoding="utf-8") as arquivo:
        plugins = json.load(arquivo).get("enabledPlugins", {})
    return [nome for nome, ligado in plugins.items() if ligado is True and nome.endswith("@ahrena")]


def instalados(lista: list[dict], case: str) -> set[str]:
    pasta = os.path.realpath(case)
    achados = set()
    for plugin in lista:
        if not plugin.get("enabled"):
            continue
        projeto = plugin.get("projectPath")
        if plugin.get("scope") == "user" or (projeto and os.path.realpath(projeto) == pasta):
            achados.add(plugin.get("id", ""))
    return achados


def main() -> int:
    case = sys.argv[1]
    try:
        lista = json.load(sys.stdin)
        plugins = ligados(case)
    except (OSError, ValueError):
        return 2
    if not isinstance(lista, list):
        return 2
    tem = instalados(lista, case)
    print(" ".join(nome.removesuffix("@ahrena") for nome in plugins if nome not in tem))
    return 0


if __name__ == "__main__":
    sys.exit(main())
