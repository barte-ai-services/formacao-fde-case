#!/usr/bin/env bash
# Confere a máquina para a Formação FDE e corrige o que um script consegue corrigir.
#
#   setup-fde.sh check          uma linha por item; sai 1 quando algum não está ok
#   setup-fde.sh fix [item...]  instala o que falta ou está velho, depois relata
#
# Cada item tem um de quatro status. `ok` não precisa de nada. `missing` e
# `outdated` são o que o `fix` corrige neste sistema. `manual` precisa de uma
# pessoa, e a linha traz o comando que ela roda; o `fix` nunca tenta.
#
# Escrito para o bash 3.2, que é o que vem no macOS.

set -u

UPSTREAM_REPO="barte-ai-services/formacao-fde-case"
UPSTREAM_URL="https://github.com/$UPSTREAM_REPO.git"
PYTHON_FLOOR="3.12"

ITEMS="git gh uv python claude git-identity gh-login case-clone uv-sync check-setup"

# O uv, o Python dele e o claude se instalam aqui, e um terminal aberto antes da
# instalação ainda não tem essa pasta no PATH.
PATH="$HOME/.local/bin:$PATH"
export PATH

HERE="$(cd "$(dirname "$0")" && pwd)"

have() { command -v "$1" >/dev/null 2>&1; }

detect_system() {
  case "$(uname -s)" in
    Darwin) if have brew; then echo macos; else echo macos-without-brew; fi ;;
    Linux) if have apt-get; then echo debian; else echo other; fi ;;
    *) echo other ;;
  esac
}

SYSTEM="$(detect_system)"

# A pasta do case: a variável FDE_CASE_DIR, ou a raiz do repositório onde este
# script mora, ou a raiz do repositório git da pasta atual. Vazio quando nenhuma
# delas é o case.
find_case_dir() {
  local dir
  if [ -n "${FDE_CASE_DIR:-}" ]; then echo "$FDE_CASE_DIR"; return; fi
  dir="$(cd "$HERE/../../../.." 2>/dev/null && pwd)"
  if [ -n "$dir" ] && [ -f "$dir/scripts/check_setup.py" ]; then echo "$dir"; return; fi
  dir="$(git rev-parse --show-toplevel 2>/dev/null)"
  if [ -n "$dir" ] && [ -f "$dir/scripts/check_setup.py" ]; then echo "$dir"; fi
}

CASE_DIR="$(find_case_dir)"

# O que o `fix` instala, por sistema. O resto é manual.
fixable_items() {
  local anywhere="uv python claude case-clone uv-sync"
  case "$SYSTEM" in
    macos | debian) echo "$anywhere git gh" ;;
    *) echo "$anywhere" ;;
  esac
}

can_fix() {
  case " $(fixable_items) " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

# O endereço de um repositório do GitHub sem .git no fim e em minúsculas.
normalize_url() {
  local url="${1%/}"
  echo "${url%.git}" | tr 'A-Z' 'a-z'
}

is_original() {
  case "$(normalize_url "$1")" in
    *github.com[:/]barte-ai-services/formacao-fde-case) return 0 ;;
    *) return 1 ;;
  esac
}

is_case_repo() {
  case "$(normalize_url "$1")" in
    *github.com[:/]*/formacao-fde-case) return 0 ;;
    *) return 1 ;;
  esac
}

# O comando que a pessoa roda para um item que o `fix` não resolve.
manual_hint() {
  case "$1" in
    brew) echo 'instale o Homebrew pelo https://brew.sh (ele pede a senha do Mac) e rode o fix de novo' ;;
    git-identity) echo 'git config --global user.name "Seu Nome" && git config --global user.email "seu-email@exemplo.com" (o mesmo e-mail da conta do GitHub)' ;;
    gh-login) echo 'gh auth login (GitHub.com, HTTPS, Login with a web browser) e depois gh auth setup-git' ;;
    check-setup) echo 'rode python3 scripts/check_setup.py na pasta do case e siga o que ele disser' ;;
    *) echo "não há instalador para este sistema; instale $1 do seu jeito, como no SETUP.md" ;;
  esac
}

needs_person() {
  STATUS=manual
  DETAIL="$(manual_hint "$1")"
}

check_case_clone() {
  local origin upstream
  if [ -z "$CASE_DIR" ]; then
    STATUS=manual
    DETAIL="gh repo fork $UPSTREAM_REPO --clone, e depois abra uma sessão nova do Claude Code na pasta formacao-fde-case"
    return
  fi
  origin="$(git -C "$CASE_DIR" remote get-url origin 2>/dev/null)"
  upstream="$(git -C "$CASE_DIR" remote get-url upstream 2>/dev/null)"
  if [ -z "$origin" ] || is_original "$origin"; then
    STATUS=manual
    DETAIL="gh repo fork --remote, dentro da pasta do case: o original vira upstream e o seu fork vira origin"
    return
  fi
  if ! is_case_repo "$origin"; then
    STATUS=manual
    DETAIL="o origin aponta para $origin, que não é um fork do formacao-fde-case"
    return
  fi
  DETAIL="$origin"
  if [ -z "$upstream" ]; then
    STATUS=missing
    DETAIL="$origin, sem upstream"
  elif ! is_original "$upstream"; then
    STATUS=manual
    DETAIL="git remote set-url upstream $UPSTREAM_URL (hoje aponta para $upstream)"
  fi
}

check_uv_sync() {
  if [ -z "$CASE_DIR" ]; then STATUS=manual; DETAIL="depende do case-clone"; return; fi
  have uv || { STATUS=missing; DETAIL="depende do uv"; return; }
  (cd "$CASE_DIR" && uv sync --check) >/dev/null 2>&1 || STATUS=missing
}

check_check_setup() {
  if [ -z "$CASE_DIR" ]; then STATUS=manual; DETAIL="depende do case-clone"; return; fi
  if have python3; then
    (cd "$CASE_DIR" && python3 scripts/check_setup.py) >/dev/null 2>&1 && return
  elif have uv; then
    (cd "$CASE_DIR" && uv run python scripts/check_setup.py) >/dev/null 2>&1 && return
  fi
  needs_person check-setup
}

# Define STATUS e DETAIL de um item, lendo a máquina sem mudar nada.
inspect() {
  STATUS=ok
  DETAIL=""
  case "$1" in
    brew | git | gh | uv | claude) have "$1" || STATUS=missing ;;
    python) uv python find ">=$PYTHON_FLOOR" >/dev/null 2>&1 || STATUS=missing ;;
    git-identity)
      DETAIL="$(git config user.email 2>/dev/null)"
      [ -n "$DETAIL" ] && [ -n "$(git config user.name 2>/dev/null)" ] || needs_person git-identity ;;
    gh-login) gh auth status >/dev/null 2>&1 || needs_person gh-login ;;
    case-clone) check_case_clone ;;
    uv-sync) check_uv_sync ;;
    check-setup) check_check_setup ;;
    *) echo "item desconhecido: $1" >&2; exit 2 ;;
  esac
  case "$STATUS" in missing | outdated) ;; *) return 0 ;; esac
  can_fix "$1" && return 0
  STATUS=manual
  DETAIL="$(manual_hint "$1")"
}

all_items() {
  case "$SYSTEM" in macos*) echo "brew $ITEMS" ;; *) echo "$ITEMS" ;; esac
}

report() {
  local item failed=0
  for item in $(all_items); do
    inspect "$item"
    printf '%-9s%-14s%s\n' "$STATUS" "$item" "$DETAIL"
    [ "$STATUS" = ok ] || failed=1
  done
  return "$failed"
}

# Roda como root. Sem terminal, o sudo não tem onde pedir a senha: falha na hora
# e a pessoa roda o mesmo fix no terminal dela.
as_root() {
  if [ "$(id -u)" -eq 0 ]; then "$@"; return; fi
  if [ ! -t 0 ] && ! sudo -n true 2>/dev/null; then
    echo "o sudo pede a senha, e esta sessão não tem terminal para digitá-la" >&2
    return 1
  fi
  sudo "$@"
}

apt_install() {
  as_root apt-get update && as_root apt-get install -y "$@"
}

ensure_curl() {
  have curl && return 0
  [ "$SYSTEM" = debian ] && apt_install curl
}

# O repositório do GitHub CLI para o apt. A chave já vem no formato binário.
add_github_cli_repository() {
  local keyring=/etc/apt/keyrings/githubcli-archive-keyring.gpg
  ensure_curl || return 1
  as_root mkdir -p -m 755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | as_root tee "$keyring" >/dev/null \
    && as_root chmod go+r "$keyring" \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=$keyring] https://cli.github.com/packages stable main" \
      | as_root tee /etc/apt/sources.list.d/github-cli.list >/dev/null
}

install_on_macos() {
  case "$1" in
    git | gh) brew install "$1" ;;
  esac
}

install_on_debian() {
  case "$1" in
    git) apt_install git ;;
    gh) add_github_cli_repository && apt_install gh ;;
  esac
}

install() {
  case "$1" in
    uv) ensure_curl && curl -LsSf https://astral.sh/uv/install.sh | sh ;;
    python) uv python install "$PYTHON_FLOOR" ;;
    claude) ensure_curl && curl -fsSL https://claude.ai/install.sh | bash ;;
    case-clone) git -C "$CASE_DIR" remote add upstream "$UPSTREAM_URL" ;;
    uv-sync) (cd "$CASE_DIR" && uv sync) ;;
    *) "install_on_$SYSTEM" "$1" ;;
  esac
}

fix() {
  local item
  for item in "$@"; do
    inspect "$item"
    case "$STATUS" in missing | outdated) ;; *) continue ;; esac
    echo "corrigindo $item" >&2
    install "$item" >&2 || echo "não deu para corrigir $item" >&2
  done
}

case "${1:-}" in
  check) report ;;
  fix)
    shift
    if [ "$#" -eq 0 ]; then
      # shellcheck disable=SC2046  # a lista de itens se divide de propósito
      set -- $(all_items)
    fi
    fix "$@"
    report
    ;;
  *) echo "uso: setup-fde.sh check | fix [item...]" >&2; exit 2 ;;
esac
