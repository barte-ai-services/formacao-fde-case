"""Content checks for the case, challenge and templates (issue #16). Offline, stdlib + pytest."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIPPED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "outputs"}
TEXT_SUFFIXES = {".md", ".py", ".txt", ".csv", ".json", ".toml", ".yml", ".yaml", ".sh", ".cfg", ".ini", ""}

TEMPLATES = [
    "checkpoint-1-diagnosis.md",
    "checkpoint-2-access-checklist.md",
    "checkpoint-2-solution-design.md",
    "checkpoint-2-delivery-plan.md",
    "sunday-pitch.md",
    "portfolio-tutorial.md",
]

# #16/AC-4: built from parts so this file does not contain the name it guards against.
FORBIDDEN_CLIENT_NAME = "rap" + "pi"


def _repo_files():
    for path in REPO_ROOT.rglob("*"):
        relative = path.relative_to(REPO_ROOT)
        if any(part in SKIPPED_DIRS for part in relative.parts):
            continue
        if path.is_file():
            yield path


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", TEMPLATES)
def test_template_exists(name):
    """#16/AC-1: templates/ holds each of the six deliverable templates."""
    path = REPO_ROOT / "templates" / name
    assert path.is_file(), f"missing template: templates/{name}"
    assert path.read_text(encoding="utf-8").strip(), f"empty template: templates/{name}"


def test_challenge_refers_to_secret_only_through_placeholder():
    """#16/AC-2: challenge/README.md carries the placeholder marker for the kit secret."""
    assert "<<KIT_SECRET_PLACEHOLDER>>" in _read("challenge/README.md")


def test_no_planting_script_in_repository():
    """#16/AC-2: no planting script exists anywhere in the repository tree."""
    offenders = [str(p.relative_to(REPO_ROOT)) for p in _repo_files() if "plant" in p.name.lower()]
    assert offenders == [], f"planting script found in the repository: {offenders}"


def test_case_readme_states_dossier_release_and_sync_steps():
    """#16/AC-3: case/README.md gives the 10h30 dossier release and web and CLI sync steps."""
    text = _read("case/README.md")
    assert "10h30" in text
    assert "14/11" in text
    assert "upstream" in text
    assert "Sync fork" in text
    for command in ("git fetch upstream", "git merge upstream/main", "git push origin main"):
        assert command in text, f"missing sync step: {command}"


def test_no_real_client_name_in_repository():
    """#16/AC-4: no text file in the repository names the real client (anonymisation guard)."""
    offenders = []
    for path in _repo_files():
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if FORBIDDEN_CLIENT_NAME in text.lower():
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], f"real client name found in: {offenders}"
