"""Acesso à base sintética da Já Chegou. Lê só os dados operacionais; nunca o gabarito."""

from __future__ import annotations

import json
import os
from functools import cached_property
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS_PADRAO = RAIZ / "dados"

CLASSIFICACOES = ["match", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
ACOES = ["receber", "receber_parcial", "recusar"]
NIVEIS = ["regra", "analista", "coordenacao", "diretoria", "bloqueio"]


class Base:
    def __init__(self, pasta: Path | str | None = None):
        self.pasta = Path(pasta or os.environ.get("FDE_DADOS") or DADOS_PADRAO)

    def _ler(self, nome: str):
        return json.loads((self.pasta / nome).read_text(encoding="utf-8"))

    @cached_property
    def fornecedores(self) -> dict[str, dict]:
        return {f["fornecedor_id"]: f for f in self._ler("fornecedores.json")}

    @cached_property
    def produtos(self) -> list[dict]:
        return self._ler("produtos.json")

    @cached_property
    def por_sku(self) -> dict[str, dict]:
        return {p["sku"]: p for p in self.produtos}

    @cached_property
    def por_codigo_fornecedor(self) -> dict[str, dict]:
        return {p["codigo_fornecedor"]: p for p in self.produtos}

    @cached_property
    def ordens(self) -> dict[str, dict]:
        return {o["ordem_id"]: o for o in self._ler("ordens.json")}

    @cached_property
    def notas(self) -> dict[str, dict]:
        return {n["nota_id"]: n for n in self._ler("notas.json")}

    @cached_property
    def recebimentos(self) -> list[dict]:
        return self._ler("recebimentos.json")

    @cached_property
    def notas_lancadas(self) -> list[dict]:
        return self._ler("notas_lancadas.json")

    @cached_property
    def pagamentos(self) -> list[dict]:
        return self._ler("pagamentos.json")

    @cached_property
    def regua(self) -> dict:
        return self._ler("regua.json")

    @cached_property
    def excecoes(self) -> dict:
        return self._ler("excecoes.json")

    # ---------- consultas ----------
    def recebimento_da_nota(self, nota: dict) -> dict | None:
        for r in self.recebimentos:
            if r["nota_chave"] == nota["chave"]:
                return r
        return None

    def recebimentos_sem_nota(self, fornecedor_id: str, destino: str) -> list[dict]:
        return [r for r in self.recebimentos
                if r["nota_chave"] is None and r["fornecedor_id"] == fornecedor_id and r["destino"] == destino]

    def ordens_do_fornecedor(self, fornecedor_id: str, destino: str | None = None, status: str | None = None) -> list[dict]:
        return [o for o in self.ordens.values()
                if o["fornecedor_id"] == fornecedor_id
                and (destino is None or o["destino"] == destino)
                and (status is None or o["status"] == status)]

    def lancadas_do_fornecedor(self, fornecedor_id: str) -> list[dict]:
        return [n for n in self.notas_lancadas if n["fornecedor_id"] == fornecedor_id]

    def pagamentos_fora_do_fluxo(self, fornecedor_id: str, destino: str | None = None) -> list[dict]:
        return [p for p in self.pagamentos
                if p["fornecedor_id"] == fornecedor_id and (destino is None or p["destino"] == destino)]
