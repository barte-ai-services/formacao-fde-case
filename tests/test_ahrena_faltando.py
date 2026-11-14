"""formacao-fde-ops #56/AC-2: testes do verificador dos plugins do Ahrena."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "setup-fde" / "scripts"))

import ahrena_faltando  # noqa: E402


def escreve_settings(case: Path, conteudo: str) -> None:
    (case / ".claude").mkdir(parents=True, exist_ok=True)
    (case / ".claude" / "settings.json").write_text(conteudo, encoding="utf-8")


def roda(monkeypatch: pytest.MonkeyPatch, case: Path, entrada: str) -> int:
    monkeypatch.setattr(sys, "argv", ["ahrena_faltando.py", str(case)])
    monkeypatch.setattr(sys, "stdin", io.StringIO(entrada))
    return ahrena_faltando.main()


def test_ligados_so_conta_o_ahrena_com_true(tmp_path: Path) -> None:
    plugins = {"a@ahrena": True, "b@ahrena": False, "c@outro": True, "d@ahrena": "true"}
    escreve_settings(tmp_path, json.dumps({"enabledPlugins": plugins}))
    assert ahrena_faltando.ligados(str(tmp_path)) == ["a@ahrena"]


def test_instalados_escopo_user_conta(tmp_path: Path) -> None:
    lista = [{"id": "a@ahrena", "scope": "user", "enabled": True}]
    assert ahrena_faltando.instalados(lista, str(tmp_path)) == {"a@ahrena"}


def test_instalados_da_pasta_do_case_conta(tmp_path: Path) -> None:
    lista = [{"id": "a@ahrena", "scope": "project", "enabled": True, "projectPath": str(tmp_path)}]
    assert ahrena_faltando.instalados(lista, str(tmp_path)) == {"a@ahrena"}


def test_instalados_de_outra_pasta_nao_conta(tmp_path: Path) -> None:
    lista = [{"id": "a@ahrena", "scope": "project", "enabled": True, "projectPath": str(tmp_path / "outra")}]
    assert ahrena_faltando.instalados(lista, str(tmp_path)) == set()


def test_instalados_desabilitado_nao_conta(tmp_path: Path) -> None:
    lista = [{"id": "a@ahrena", "scope": "user", "enabled": False}]
    assert ahrena_faltando.instalados(lista, str(tmp_path)) == set()


def test_main_imprime_o_que_falta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    escreve_settings(tmp_path, json.dumps({"enabledPlugins": {"a@ahrena": True, "b@ahrena": True}}))
    entrada = json.dumps([{"id": "b@ahrena", "scope": "user", "enabled": True}])
    assert roda(monkeypatch, tmp_path, entrada) == 0
    assert capsys.readouterr().out.strip() == "a"


def test_main_sai_2_com_entrada_que_nao_e_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    escreve_settings(tmp_path, "{}")
    assert roda(monkeypatch, tmp_path, "nada disso") == 2


def test_main_sai_2_com_entrada_que_nao_e_lista(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    escreve_settings(tmp_path, "{}")
    assert roda(monkeypatch, tmp_path, "{}") == 2


def test_main_sai_2_com_settings_ilegivel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    escreve_settings(tmp_path, "<<<<<<< conflito")
    assert roda(monkeypatch, tmp_path, "[]") == 2


def test_main_sai_2_sem_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert roda(monkeypatch, tmp_path, "[]") == 2
