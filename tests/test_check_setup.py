"""Offline tests for scripts/check_setup.py.

Every probe of the machine (command lookup, version calls, interpreter
version, platform) is injected, so no real tool is needed to run them.
"""

import ast
import re
import sys
import tomllib
from pathlib import Path

from scripts import check_setup

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_setup.py"

FULL_MACHINE = {
    "git": "git version 2.47.1",
    "gh": "gh version 2.63.0 (2024-11-27)",
    "claude": "2.1.0 (Claude Code)",
    "uv": "uv 0.9.0",
}
UV_PYTHON = "/home/student/.local/share/uv/python/cpython-3.12.8/bin/python3.12"


class FakeMachine:
    """A machine whose tools and answers are fixed by the test."""

    def __init__(self, tools=None, uv_python=UV_PYTHON, broken=(), gh_logged_in=True):
        self.tools = dict(FULL_MACHINE if tools is None else tools)
        self.uv_python = uv_python
        self.broken = set(broken)
        self.gh_logged_in = gh_logged_in

    def which(self, name):
        return f"/usr/bin/{name}" if name in self.tools else None

    def run(self, command):
        name = command[0]
        if name not in self.tools or name in self.broken:
            return None
        if command[1:3] == ["python", "find"]:
            return self.uv_python
        if command[1:3] == ["auth", "status"]:
            return "Logged in to github.com" if self.gh_logged_in else None
        return self.tools[name]


def run_main(machine, version_info=(3, 12, 8), platform="linux"):
    lines = []
    code = check_setup.main(
        probes=check_setup.Probes(machine.which, machine.run, version_info),
        platform=platform,
        out=lines.append,
    )
    return code, lines


def line_for(lines, label):
    matches = [line for line in lines if label in line]
    assert matches, f"no line mentions {label!r}: {lines}"
    return matches[0]


def test_reports_one_line_per_item_and_a_verdict_when_ready():
    """#15/AC-2: one pt-BR line per item (Git, GitHub, Claude Code, Python, uv) plus a verdict."""
    _, lines = run_main(FakeMachine())

    for label in ("Git", "GitHub", "Claude Code", "Python", "uv"):
        assert line_for(lines, label).startswith("[OK]")
    assert any("Tudo pronto" in line for line in lines)


def test_missing_required_tool_is_reported_missing_and_points_to_setup():
    """#15/AC-2: a missing tool is reported as FALTA with what to do and where in SETUP.md."""
    tools = dict(FULL_MACHINE)
    del tools["claude"]

    _, lines = run_main(FakeMachine(tools=tools))

    line = line_for(lines, "Claude Code")
    assert line.startswith("[FALTA]")
    assert "SETUP.md" in line
    assert any("Falta" in line and "obrigatório" in line for line in lines)


def test_missing_github_cli_is_reported_missing_and_points_to_setup():
    """#15/AC-2: no gh CLI is reported as FALTA, since gh is how Git logs in to GitHub."""
    tools = dict(FULL_MACHINE)
    del tools["gh"]

    _, lines = run_main(FakeMachine(tools=tools))

    line = line_for(lines, "GitHub")
    assert line.startswith("[FALTA]")
    assert "SETUP.md" in line


def test_github_cli_not_logged_in_tells_to_run_gh_auth_login():
    """#15/AC-2: gh installed but not logged in is FALTA with the hint to run `gh auth login`."""
    _, lines = run_main(FakeMachine(gh_logged_in=False))

    line = line_for(lines, "GitHub")
    assert line.startswith("[FALTA]")
    assert "gh auth login" in line


def test_native_windows_gets_a_hint_to_use_wsl():
    """#15/AC-2: on native Windows the checker tells the student to use WSL."""
    _, lines = run_main(FakeMachine(), platform="win32")

    assert any("WSL" in line for line in lines)


def test_exits_zero_when_every_required_item_passes():
    """#15/AC-3: exit 0 when Git, a logged-in gh, Claude Code, Python >= 3.12 and uv are all present."""
    code, _ = run_main(FakeMachine())

    assert code == 0


def test_github_cli_not_logged_in_fails():
    """#15/AC-3: gh is required and must be logged in, so `gh auth status` failing exits 1."""
    code, _ = run_main(FakeMachine(gh_logged_in=False))

    assert code == 1


def test_exits_one_when_any_required_tool_is_missing():
    """#15/AC-3: exit 1 when Git, gh, Claude Code or uv is missing."""
    for missing in ("git", "gh", "claude", "uv"):
        tools = dict(FULL_MACHINE)
        del tools[missing]

        code, _ = run_main(FakeMachine(tools=tools))

        assert code == 1, missing


def test_tool_found_but_not_answering_counts_as_missing():
    """#15/AC-3: a tool on PATH whose --version fails is reported FALTA and exits 1."""
    code, lines = run_main(FakeMachine(broken={"git"}))

    assert code == 1
    assert line_for(lines, "Git:").startswith("[FALTA]")


def test_old_python_is_fine_when_uv_has_python_312():
    """#15/AC-3: an old python3 passes when uv already manages a Python >= 3.12."""
    code, lines = run_main(FakeMachine(), version_info=(3, 9, 6))

    assert code == 0
    assert line_for(lines, "Python").startswith("[OK]")


def test_old_python_without_uv_python_fails():
    """#15/AC-3: exit 1 when neither the interpreter nor uv offers Python >= 3.12."""
    code, lines = run_main(FakeMachine(uv_python=None), version_info=(3, 9, 6))

    assert code == 1
    line = line_for(lines, "Python")
    assert line.startswith("[FALTA]")
    assert "uv python install 3.12" in line


def test_imports_only_the_standard_library():
    """#15/AC-4: every top-level module the checker imports is in the standard library."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative imports need a package, not a bare script"
            modules.add(node.module.split(".")[0])

    assert modules
    assert modules <= set(sys.stdlib_module_names) | {"__future__"}


def test_parses_on_the_oldest_python3_students_may_have():
    """#15/AC-4: the checker's syntax works on Python 3.8, so it runs before uv is installed."""
    ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 8))


def test_default_runner_returns_output_or_none():
    """#15/AC-3: the real runner reports a version and turns a missing command into None."""
    assert check_setup.run_command([sys.executable, "--version"]).startswith("Python")
    assert check_setup.run_command(["formacao-fde-no-such-command"]) is None


def test_env_file_is_ignored_and_example_declares_the_variables():
    """#15/AC-5: .gitignore ignores .env and .env.example declares ANTHROPIC_API_KEY and AGENT_MODEL."""
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in [line.strip() for line in ignored]

    example = (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    keys = {line.split("=", 1)[0] for line in example if "=" in line and not line.startswith("#")}
    assert {"ANTHROPIC_API_KEY", "AGENT_MODEL"} <= keys


def test_every_setup_section_the_checker_points_to_exists():
    """#15/AC-2: each 'veja SETUP.md, seção "..."' pointer names a real SETUP.md heading."""
    _, lines = run_main(FakeMachine(tools={}, uv_python=None), version_info=(3, 9, 6), platform="win32")
    _, logged_out = run_main(FakeMachine(gh_logged_in=False))
    pointers = set(re.findall(r'seção "([^"]+)"', "\n".join(lines + logged_out)))
    headings = {
        line[3:].strip()
        for line in (ROOT / "SETUP.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    }

    assert pointers
    assert pointers <= headings, pointers - headings


def test_suite_runs_offline_without_an_api_key(monkeypatch):
    """#15/AC-1: pytest collects only tests/, no test imports anthropic at module level, and no key is needed."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]

    for test_file in sorted((ROOT / "tests").rglob("*.py")):
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        imported = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert "anthropic" not in imported, test_file

    code, _ = run_main(FakeMachine())
    assert code == 0
