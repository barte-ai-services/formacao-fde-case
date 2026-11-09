"""Check that this machine has what the Formação FDE needs.

Run it with ``python3 scripts/check_setup.py``. It uses only the Python
standard library and keeps Python 3.8 syntax, so it works before uv or a
recent Python is installed. Output is in pt-BR because students read it.

Exit code: 0 when every required item passes, 1 otherwise.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Callable, List, NamedTuple, Optional, Sequence, Tuple

MIN_PYTHON = (3, 12)
PROBE_TIMEOUT_SECONDS = 15

OK = "OK"
MISSING = "FALTA"

Which = Callable[[str], Optional[str]]
Runner = Callable[[Sequence[str]], Optional[str]]


class Probes(NamedTuple):
    """The three ways the checker looks at the machine, injected together."""

    which: Which
    run: Runner
    version_info: Sequence[int]


class CheckResult(NamedTuple):
    label: str
    status: str
    detail: str
    required: bool

    @property
    def failed(self) -> bool:
        return self.required and self.status == MISSING

    def render(self) -> str:
        return f"[{self.status}] {self.label}: {self.detail}"


def run_command(command: Sequence[str]) -> Optional[str]:
    """Run a version probe and return the first line of its output, or None if it fails."""
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    output = (completed.stdout or completed.stderr).strip()
    return output.splitlines()[0] if output else ""


def _setup_hint(section: str) -> str:
    return f'veja SETUP.md, seção "{section}".'


def _probe(probes: Probes, command: Sequence[str]) -> Tuple[bool, Optional[str]]:
    """Return (found on PATH, first output line or None when the call failed)."""
    if probes.which(command[0]) is None:
        return False, None
    return True, probes.run(command)


def check_required_tool(
    probes: Probes, label: str, command: Sequence[str], section: str
) -> CheckResult:
    found, version = _probe(probes, command)
    if not found:
        detail = f"não encontrado. Instale e rode este script de novo; {_setup_hint(section)}"
        return CheckResult(label, MISSING, detail, required=True)
    if version is None:
        detail = (
            f"encontrado, mas `{' '.join(command)}` não respondeu. "
            f"Reinstale; {_setup_hint(section)}"
        )
        return CheckResult(label, MISSING, detail, required=True)
    return CheckResult(label, OK, version, required=True)


def check_github(probes: Probes) -> CheckResult:
    section = "GitHub CLI"
    found, version = _probe(probes, ["gh", "--version"])
    if not found:
        detail = (
            "GitHub CLI (gh) não encontrado. Ele é obrigatório: é com ele que o Git "
            f"faz login no GitHub. Instale e rode este script de novo; {_setup_hint(section)}"
        )
        return CheckResult("GitHub", MISSING, detail, required=True)
    if version is None:
        detail = f"encontrado, mas `gh --version` não respondeu. Reinstale; {_setup_hint(section)}"
        return CheckResult("GitHub", MISSING, detail, required=True)
    if probes.run(["gh", "auth", "status"]) is None:
        detail = (
            f"{version}, mas você ainda não entrou na sua conta. "
            f"Rode `gh auth login` e depois `gh auth setup-git`; {_setup_hint(section)}"
        )
        return CheckResult("GitHub", MISSING, detail, required=True)
    return CheckResult("GitHub", OK, f"{version} (conta conectada)", required=True)


def check_python(probes: Probes) -> CheckResult:
    running = ".".join(str(part) for part in probes.version_info[:3])
    wanted = ".".join(str(part) for part in MIN_PYTHON)
    if tuple(probes.version_info[:2]) >= MIN_PYTHON:
        return CheckResult("Python", OK, f"{running} (este interpretador)", required=True)
    uv_python = None
    if probes.which("uv") is not None:
        uv_python = probes.run(["uv", "python", "find", f">={wanted}"])
    if uv_python:
        detail = f"este interpretador é {running}, mas o uv já tem Python >= {wanted} ({uv_python})"
        return CheckResult("Python", OK, detail, required=True)
    detail = (
        f"este interpretador é {running} e o uv não tem Python >= {wanted}. "
        f"Rode `uv python install {wanted}`; {_setup_hint('uv e Python 3.12')}"
    )
    return CheckResult("Python", MISSING, detail, required=True)


def run_checks(probes: Probes) -> List[CheckResult]:
    return [
        check_required_tool(probes, "Git", ["git", "--version"], "Git"),
        check_github(probes),
        check_required_tool(probes, "Claude Code", ["claude", "--version"], "Claude Code"),
        check_python(probes),
        check_required_tool(probes, "uv", ["uv", "--version"], "uv e Python 3.12"),
    ]


def verdict(results: Sequence[CheckResult]) -> str:
    failures = sum(1 for result in results if result.failed)
    if failures == 0:
        return "Tudo pronto: sua máquina tem o necessário para a Formação FDE."
    missing = "Falta 1 item obrigatório" if failures == 1 else f"Faltam {failures} itens obrigatórios"
    return (
        f"{missing}. Siga as instruções acima e o SETUP.md, "
        f"e rode `python3 scripts/check_setup.py` de novo."
    )


MACHINE = Probes(which=shutil.which, run=run_command, version_info=tuple(sys.version_info[:3]))


def main(
    *,
    probes: Probes = MACHINE,
    platform: str = sys.platform,
    out: Callable[[str], None] = print,
) -> int:
    out("Conferindo a sua máquina para a Formação FDE...")
    if platform == "win32":
        out(
            "[AVISO] Windows: no Windows, use o WSL 2 com Ubuntu e rode este script "
            f"dentro do terminal do Ubuntu; {_setup_hint('Windows (WSL 2)')}"
        )
    results = run_checks(probes)
    for result in results:
        out(result.render())
    out("")
    out(verdict(results))
    return 1 if any(result.failed for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
