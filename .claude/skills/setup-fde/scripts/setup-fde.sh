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
# formacao-fde-ops #57: o Claude Code instala os plugins do Ahrena num clone
# parcial com a rede bloqueada, e o git 2.34 do Ubuntu 22.04 cai com segfault
# no checkout desse clone. Abaixo deste git, os plugins não instalam.
GIT_FLOOR="2.45"
AHRENA_MARKETPLACE="ahrenatechnology/ahrena-framework"

# formacao-fde-ops #58: O Wrangler pede um Node.js ainda com suporte. O `fix` instala a LTS de NODE_MAJOR.
NODE_FLOOR=22
NODE_MAJOR=24
# formacao-fde-ops #58: versões fixas e conferidas. Subir uma é trocar o número e, no Supabase, os dois hashes do checksums.txt do release.
WRANGLER_VERSION="4.162.0"
SUPABASE_VERSION="3.1.0"
SUPABASE_SHA256_AMD64="dbe9fd66771337fc198727da86b9d3551302f87a7091cd8781be2a4cd0c8ac4d"
SUPABASE_SHA256_ARM64="e49b2ab2f4fb428f4e033174d6d9747dd93c95d1504142ba5090699b1ecd2563"

# formacao-fde-ops #58: o colima só existe no macOS, e o all_items tira ele dos outros sistemas.
ITEMS="git gh node uv python docker colima docker-daemon supabase wrangler claude git-identity gh-login supabase-login wrangler-login case-clone uv-sync check-setup ahrena"

# formacao-fde-ops #58: o uv, o Python dele, o claude, o supabase do Linux e o wrangler se instalam aqui,
# formacao-fde-ops #58: e um terminal aberto antes da instalação ainda não tem essa pasta no PATH.
PATH="$HOME/.local/bin:$PATH"
export PATH

HERE="$(cd "$(dirname "$0")" && pwd)"

have() { command -v "$1" >/dev/null 2>&1; }

# No macOS, o git e o python3 de /usr/bin são atalhos para as ferramentas de
# linha de comando da Apple: sem elas, chamar qualquer um abre uma janela de
# instalação. Por isso nada chama o git antes de saber que ele funciona.
git_works() {
  case "$SYSTEM" in
    macos*) xcode-select -p >/dev/null 2>&1 && git --version >/dev/null 2>&1 ;;
    *) have git ;;
  esac
}

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
  git_works || return 0
  dir="$(git rev-parse --show-toplevel 2>/dev/null)"
  if [ -n "$dir" ] && [ -f "$dir/scripts/check_setup.py" ]; then echo "$dir"; fi
}

CASE_DIR="$(find_case_dir)"

# formacao-fde-ops #58: o que o `fix` instala, por sistema. O resto é manual.
fixable_items() {
  local anywhere="uv python claude case-clone uv-sync ahrena"
  case "$SYSTEM" in
    macos) echo "$anywhere git gh node docker colima docker-daemon supabase wrangler" ;;
    debian) echo "$anywhere git gh node docker supabase wrangler" ;;
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
    brew) echo 'instale o Homebrew pelo https://brew.sh (ele pede a senha do Mac e instala as ferramentas da Apple) e rode o fix de novo' ;;
    git) case "$SYSTEM" in
        macos*) echo 'xcode-select --install (aceite a janela da Apple), ou instale o Homebrew, e rode o fix de novo' ;;
        *) echo 'não há instalador para este sistema; instale o git do seu jeito, como no SETUP.md' ;;
      esac ;;
    git-identity) echo 'git config --global user.name "Seu Nome" && git config --global user.email "seu-email@exemplo.com" (o mesmo e-mail da conta do GitHub)' ;;
    gh-login) echo 'gh auth login (GitHub.com, HTTPS, Login with a web browser) e depois gh auth setup-git' ;;
    supabase-login) echo 'supabase login (abre o navegador; entre com a sua conta do Supabase)' ;;
    wrangler-login) echo 'wrangler login (abre o navegador; entre com a sua conta da Cloudflare e clique em Allow)' ;;
    docker-daemon) echo 'sudo systemctl start docker && sudo usermod -aG docker "$USER", e depois feche e abra o terminal (no WSL: wsl --shutdown no PowerShell e abra o Ubuntu de novo)' ;;
    check-setup) echo 'rode python3 scripts/check_setup.py na pasta do case e siga o que ele disser' ;;
    git-outdated) case "$SYSTEM" in
        macos*) echo "o git da Apple é mais velho que o $GIT_FLOOR; instale o Homebrew e rode o fix de novo, que ele instala o git do Homebrew" ;;
        *) echo "este sistema não tem um git $GIT_FLOOR ou mais novo no instalador; instale um do seu jeito e rode o fix de novo" ;;
      esac ;;
    *) echo "não há instalador para este sistema; instale $1 do seu jeito, como no SETUP.md" ;;
  esac
}

needs_person() {
  STATUS=manual
  DETAIL="$(manual_hint "$1")"
}

check_case_clone() {
  local origin upstream
  git_works || { STATUS=manual; DETAIL="depende do git"; return; }
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

# formacao-fde-ops #57: a versão do git, como 2.34, e se ela chega ao piso.
git_version() { git --version 2>/dev/null | awk '{print $3}'; }

version_at_least() {
  awk -v have="$1" -v want="$2" 'BEGIN {
    split(have, h, "."); split(want, w, ".")
    for (i = 1; i <= 2; i++) { if (h[i] + 0 > w[i] + 0) exit 0; if (h[i] + 0 < w[i] + 0) exit 1 }
    exit 0 }'
}

# formacao-fde-ops #57: no Ubuntu o git novo vem do PPA git-core; no Debian, não há.
is_ubuntu() { grep -qsE '^(ID|ID_LIKE)=.*ubuntu' "${OS_RELEASE:-/etc/os-release}"; }

check_git() {
  local version
  git_works || { STATUS=missing; return; }
  version="$(git_version)"
  DETAIL="$version"
  version_at_least "$version" "$GIT_FLOOR" && return
  DETAIL="$version, abaixo do $GIT_FLOOR que os plugins do Ahrena pedem"
  case "$SYSTEM" in
    macos) STATUS=outdated ;;
    debian) if is_ubuntu; then STATUS=outdated; else needs_person git-outdated; fi ;;
    *) needs_person git-outdated ;;
  esac
}

# Um uv sem o `uv sync --check` é velho demais para o uv-sync.
check_uv() {
  have uv || { STATUS=missing; return; }
  uv sync --help 2>/dev/null | grep -q -- '--check' && return
  STATUS=outdated
  DETAIL="$(uv --version 2>/dev/null), sem o uv sync --check"
}

update_uv() {
  uv self update || { [ "$SYSTEM" = macos ] && brew upgrade uv; }
}

# formacao-fde-ops #58: O Node.js com o npm, numa versão que o Wrangler aceita.
check_node() {
  local version major
  have node && have npm || { STATUS=missing; return; }
  version="$(node --version 2>/dev/null)"
  major="${version#v}"
  major="${major%%.*}"
  DETAIL="$version"
  case "$major" in '' | *[!0-9]*) major=0 ;; esac
  [ "$major" -ge "$NODE_FLOOR" ] && return
  STATUS=outdated
  DETAIL="$version, o Wrangler pede o $NODE_FLOOR ou mais novo"
}

# formacao-fde-ops #58: O motor do Docker responde. No Mac é o Colima; no Linux, o serviço do Docker Engine.
check_docker_daemon() {
  have docker || { STATUS=manual; DETAIL="depende do docker"; return; }
  docker info >/dev/null 2>&1 || STATUS=missing
}

# formacao-fde-ops #58: O wrangler vem do npm, então espera o Node.js.
check_wrangler() {
  have wrangler && return
  STATUS=missing
  have npm || DETAIL="depende do node"
}

# formacao-fde-ops #58: os logins leem a conta pela internet. A pessoa faz o login; o fix nunca tenta.
check_supabase_login() {
  have supabase || { STATUS=manual; DETAIL="depende do supabase"; return; }
  supabase projects list >/dev/null 2>&1 || needs_person supabase-login
}

check_wrangler_login() {
  local out
  have wrangler || { STATUS=manual; DETAIL="depende do wrangler"; return; }
  out="$(wrangler whoami 2>&1)" || { needs_person wrangler-login; return; }
  case "$out" in *"not authenticated"*) needs_person wrangler-login ;; esac
}

check_uv_sync() {
  if [ -z "$CASE_DIR" ]; then STATUS=manual; DETAIL="depende do case-clone"; return; fi
  have uv || { STATUS=missing; DETAIL="depende do uv"; return; }
  (cd "$CASE_DIR" && uv sync --check) >/dev/null 2>&1 || STATUS=missing
}

check_check_setup() {
  if [ -z "$CASE_DIR" ]; then STATUS=manual; DETAIL="depende do case-clone"; return; fi
  git_works || { STATUS=manual; DETAIL="depende do git"; return; }
  if have python3; then
    (cd "$CASE_DIR" && python3 scripts/check_setup.py) >/dev/null 2>&1 && return
  elif have uv; then
    (cd "$CASE_DIR" && uv run python scripts/check_setup.py) >/dev/null 2>&1 && return
  fi
  needs_person check-setup
}

# formacao-fde-ops #57: o Python que lê JSON é o python3, ou o do uv sem ele.
run_python() {
  if have python3 && git_works; then
    python3 "$@"
  elif have uv; then
    uv run --no-project --quiet python "$@"
  else
    return 127
  fi
}

# formacao-fde-ops #57: os plugins do Ahrena que o settings.json do case liga,
# instalados e habilitados no Claude Code. AHRENA_MISSING guarda os que faltam.
check_ahrena() {
  AHRENA_MISSING=""
  if [ -z "$CASE_DIR" ]; then STATUS=manual; DETAIL="depende do case-clone"; return; fi
  have claude || { STATUS=manual; DETAIL="depende do claude"; return; }
  if ! AHRENA_MISSING="$(claude plugin list --json 2>/dev/null | run_python "$HERE/ahrena_faltando.py" "$CASE_DIR" 2>/dev/null)"; then
    STATUS=manual
    DETAIL="não deu para ler os plugins do Claude Code; rode claude plugin list e confira os ahrena-*"
    return
  fi
  [ -n "$AHRENA_MISSING" ] || return 0
  DETAIL="faltam: $AHRENA_MISSING"
  if ! version_at_least "$(git_version)" "$GIT_FLOOR"; then
    STATUS=manual
    DETAIL="$DETAIL; depende do git $GIT_FLOOR ou mais novo"
    return
  fi
  STATUS=missing
}

# formacao-fde-ops #57: instala no escopo local, que grava no
# .claude/settings.local.json, fora do git, e deixa o settings.json do fork quieto.
install_ahrena() {
  local plugin failed=0
  claude plugin marketplace list 2>/dev/null | grep -q "$AHRENA_MARKETPLACE" \
    || claude plugin marketplace add "$AHRENA_MARKETPLACE" || return 1
  for plugin in $AHRENA_MISSING; do
    (cd "$CASE_DIR" && claude plugin install "$plugin@ahrena" --scope local) || failed=1
  done
  return "$failed"
}

# formacao-fde-ops #57: Define STATUS e DETAIL de um item, lendo a máquina sem mudar nada.
inspect() {
  STATUS=ok
  DETAIL=""
  case "$1" in
    brew | gh | docker | supabase | claude) have "$1" || STATUS=missing ;;
    node) check_node ;;
    # formacao-fde-ops #58: uma máquina em que o docker já responde roda outro motor, e fica com ele.
    colima) have colima || docker info >/dev/null 2>&1 || STATUS=missing ;;
    docker-daemon) check_docker_daemon ;;
    wrangler) check_wrangler ;;
    supabase-login) check_supabase_login ;;
    wrangler-login) check_wrangler_login ;;
    git) check_git ;;
    uv) check_uv ;;
    python) uv python find ">=$PYTHON_FLOOR" >/dev/null 2>&1 || STATUS=missing ;;
    git-identity)
      git_works || { STATUS=manual; DETAIL="depende do git"; return 0; }
      DETAIL="$(git config user.email 2>/dev/null)"
      [ -n "$DETAIL" ] && [ -n "$(git config user.name 2>/dev/null)" ] || needs_person git-identity ;;
    gh-login) gh auth status >/dev/null 2>&1 || needs_person gh-login ;;
    case-clone) check_case_clone ;;
    uv-sync) check_uv_sync ;;
    check-setup) check_check_setup ;;
    ahrena) check_ahrena ;;
    *) echo "item desconhecido: $1" >&2; exit 2 ;;
  esac
  case "$STATUS" in missing | outdated) ;; *) return 0 ;; esac
  can_fix "$1" && return 0
  STATUS=manual
  DETAIL="$(manual_hint "$1")"
}

all_items() {
  case "$SYSTEM" in
    macos*) echo "brew $ITEMS" ;;
    *) echo "$ITEMS" | sed 's/ colima / /' ;;
  esac
}

report() {
  local item failed=0
  for item in $(all_items); do
    inspect "$item"
    printf '%-9s%-16s%s\n' "$STATUS" "$item" "$DETAIL"
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

# formacao-fde-ops #58: O repositório da NodeSource para o apt, com a LTS de NODE_MAJOR. O Ubuntu traz um Node.js velho demais para o Wrangler. A chave vem em texto, e o apt lê o .asc.
add_nodesource_repository() {
  local keyring=/etc/apt/keyrings/nodesource.asc
  ensure_curl || return 1
  as_root mkdir -p -m 755 /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | as_root tee "$keyring" >/dev/null \
    && as_root chmod go+r "$keyring" \
    && echo "deb [signed-by=$keyring] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
      | as_root tee /etc/apt/sources.list.d/nodesource.list >/dev/null
}

# formacao-fde-ops #58: o repositório do Docker Engine para o apt, no lugar do get.docker.com, que roda um script remoto como root.
add_docker_repository() {
  local keyring=/etc/apt/keyrings/docker.asc os=debian codename
  is_ubuntu && os=ubuntu
  codename="$(sed -n 's/^UBUNTU_CODENAME=//p' "${OS_RELEASE:-/etc/os-release}" | tr -d '"')"
  [ -n "$codename" ] || codename="$(sed -n 's/^VERSION_CODENAME=//p' "${OS_RELEASE:-/etc/os-release}" | tr -d '"')"
  [ -n "$codename" ] || { echo "não achei o codinome do sistema em /etc/os-release" >&2; return 1; }
  ensure_curl || return 1
  as_root mkdir -p -m 755 /etc/apt/keyrings \
    && curl -fsSL "https://download.docker.com/linux/$os/gpg" | as_root tee "$keyring" >/dev/null \
    && as_root chmod go+r "$keyring" \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=$keyring] https://download.docker.com/linux/$os $codename stable" \
      | as_root tee /etc/apt/sources.list.d/docker.list >/dev/null
}

# formacao-fde-ops #58: o Supabase CLI não se instala pelo npm global. No Linux, o binário da versão fixa vai para ~/.local/bin, sem sudo, depois de o hash bater.
install_supabase_binary() {
  local arch file expected dir code
  ensure_curl || return 1
  arch="$(dpkg --print-architecture)"
  case "$arch" in
    amd64) expected="$SUPABASE_SHA256_AMD64" ;;
    arm64) expected="$SUPABASE_SHA256_ARM64" ;;
    *) echo "o Supabase CLI não tem binário para $arch" >&2; return 1 ;;
  esac
  file="supabase_${SUPABASE_VERSION}_linux_$arch.tar.gz"
  dir="$(mktemp -d)" || return 1
  curl -fsSL -o "$dir/$file" "https://github.com/supabase/cli/releases/download/v$SUPABASE_VERSION/$file" \
    && echo "$expected  $dir/$file" | sha256sum -c - >/dev/null \
    && mkdir -p "$HOME/.local/bin" \
    && tar -xzf "$dir/$file" -C "$HOME/.local/bin" supabase
  code=$?
  rm -rf "$dir"
  return "$code"
}

# formacao-fde-ops #58: O motor é o Colima, não o Docker Desktop: o docker do Homebrew é só o cliente.
install_on_macos() {
  case "$1" in
    git | gh | docker | colima) brew install "$1" && hash -r ;;
    node) if brew list node >/dev/null 2>&1; then brew upgrade node; else brew install node; fi ;;
    supabase) brew install supabase/tap/supabase ;;
    docker-daemon) colima start ;;
  esac
}

# formacao-fde-ops #57: o PPA git-core traz o git atual para o Ubuntu.
add_git_core_repository() {
  have add-apt-repository || apt_install software-properties-common || return 1
  as_root add-apt-repository -y ppa:git-core/ppa
}

# formacao-fde-ops #58: o Docker Engine vem do repositório da Docker, e o pacote liga o serviço. Entrar no grupo docker só vale num terminal novo.
install_on_debian() {
  case "$1" in
    git) if have git && is_ubuntu; then add_git_core_repository && apt_install git; else apt_install git; fi ;;
    gh) add_github_cli_repository && apt_install gh ;;
    node) add_nodesource_repository && apt_install nodejs ;;
    docker)
      add_docker_repository \
        && apt_install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
        && as_root usermod -aG docker "$USER" ;;
    supabase) install_supabase_binary ;;
  esac
}

install() {
  case "$1" in
    uv) if have uv; then update_uv; else ensure_curl && curl -LsSf https://astral.sh/uv/install.sh | sh; fi ;;
    python) uv python install "$PYTHON_FLOOR" ;;
    claude) ensure_curl && curl -fsSL https://claude.ai/install.sh | bash ;;
    # formacao-fde-ops #58: num prefixo da pessoa, o npm instala sem sudo, e o wrangler cai no ~/.local/bin.
    wrangler) npm install -g --prefix "$HOME/.local" "wrangler@$WRANGLER_VERSION" ;;
    case-clone) git -C "$CASE_DIR" remote add upstream "$UPSTREAM_URL" ;;
    uv-sync) (cd "$CASE_DIR" && uv sync) ;;
    ahrena) install_ahrena ;;
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
