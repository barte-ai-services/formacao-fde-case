#!/usr/bin/env bash
# A suíte do setup-fde.sh.
#
# O script lê a máquina pelos comandos do PATH e pelos arquivos da HOME, então
# cada caso monta uma caixa de areia com os dois: uma pasta `bin` com dublês de
# cada ferramenta que o script consulta, uma home vazia e uma cópia do case com
# o script dentro. Nada da máquina de verdade é lido nem mudado. Cada dublê
# anota a linha de comando em `calls`, e é assim que um caso prova o que o `fix`
# rodou e o que deixou quieto.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/setup-fde.sh"
ORIGINAL="https://github.com/barte-ai-services/formacao-fde-case.git"
INSTALLS='apt-get|brew (install|upgrade)|curl|dpkg|uv python install|uv self update|uv sync$|git .*remote (add|set-url)|gh auth (login|setup-git|refresh)|gh repo fork'
FAILURES=0
SANDBOX=""

# Todas as caixas de areia ficam numa pasta só, apagada no fim. Os dublês são
# executáveis, então a pasta precisa aceitar execução: há máquinas com /tmp
# montado como noexec, e nelas a pasta vai para ~/.cache.
ROOT="$(mktemp -d)"
printf '#!/bin/sh\n' > "$ROOT/probe" && chmod +x "$ROOT/probe"
if ! "$ROOT/probe" 2>/dev/null; then
  rm -rf "$ROOT"
  mkdir -p "$HOME/.cache"
  ROOT="$(mktemp -d "$HOME/.cache/test-setup-fde.XXXXXX")"
fi
trap 'rm -rf "$ROOT"' EXIT

stub() {
  printf '#!/bin/sh\necho "%s $*" >> "$CALLS"\n%s\n' "$1" "$2" > "$SANDBOX/bin/$1"
  chmod +x "$SANDBOX/bin/$1"
}

# Uma máquina Linux com tudo instalado, o login feito e o fork clonado.
healthy_machine() {
  local tool
  SANDBOX="$(mktemp -d "$ROOT/caso.XXXXXX")"
  mkdir -p "$SANDBOX/bin" "$SANDBOX/home" "$SANDBOX/case/scripts" "$SANDBOX/case/.claude/skills/setup-fde/scripts"
  cp "$SCRIPT" "$SANDBOX/case/.claude/skills/setup-fde/scripts/setup-fde.sh"
  : > "$SANDBOX/case/scripts/check_setup.py"
  : > "$SANDBOX/case/.synced"
  : > "$SANDBOX/calls"
  for tool in sh sed grep head mktemp rm mkdir cat chmod dirname ln tr tee; do
    ln -s "$(type -P "$tool")" "$SANDBOX/bin/$tool"
  done
  # O bash do sistema, não o primeiro do PATH: no macOS é o 3.2, o mais velho
  # em que o script precisa rodar.
  ln -s /bin/bash "$SANDBOX/bin/bash"
  for tool in claude apt-get dpkg; do
    stub "$tool" ''
  done
  stub uname 'case "$1" in -s) echo "${FAKE_SYSTEM:-Linux}" ;; *) echo x86_64 ;; esac'
  # Nunca root, e o sudo só repassa para os dublês: nada toca o /etc de verdade.
  stub id 'echo 1000'
  stub sudo 'if [ "$1" = -n ]; then [ -z "${FAKE_SUDO_PASSWORD:-}" ] || exit 1; shift; fi
  case "$1" in apt-get | dpkg | true) "$@" ;; tee) cat > /dev/null ;; esac'
  # Instalar o claude o põe no PATH, como o instalador de verdade.
  stub curl 'case "$*" in *claude.ai/install.sh*) printf "#!/bin/sh\n" > "$(dirname "$0")/claude"; chmod +x "$(dirname "$0")/claude" ;; esac'
  stub git 'case "$*" in
    "config user.name") [ -n "${FAKE_NO_IDENTITY:-}" ] || echo Ada ;;
    "config user.email") [ -n "${FAKE_NO_IDENTITY:-}" ] || echo ada@exemplo.com ;;
    "rev-parse --show-toplevel") [ -n "${FAKE_TOPLEVEL:-}" ] || exit 128; echo "$FAKE_TOPLEVEL" ;;
    *"remote get-url origin") u="${FAKE_ORIGIN-https://github.com/ada/formacao-fde-case.git}"; [ -n "$u" ] || exit 2; echo "$u" ;;
    *"remote get-url upstream")
      u="${FAKE_UPSTREAM-'"$ORIGINAL"'}"
      [ -f "$(dirname "$CALLS")/upstream-added" ] && u='"$ORIGINAL"'
      [ -n "$u" ] || exit 2; echo "$u" ;;
    *"remote add upstream"*) : > "$(dirname "$CALLS")/upstream-added" ;;
  esac'
  stub gh 'case "$*" in "auth status") [ -z "${FAKE_LOGGED_OUT:-}" ] || exit 1 ;; esac'
  # O `uv sync` deixa a .venv em dia, e o `uv sync --check` lê isso.
  stub uv 'case "$*" in
    "python find"*) [ -z "${FAKE_NO_PYTHON:-}" ] || exit 1 ;;
    "sync --check") [ -f .synced ] ;;
    sync) : > .synced ;;
    "sync --help") [ -n "${FAKE_OLD_UV:-}" ] && [ ! -f "$(dirname "$CALLS")/uv-updated" ] || echo "      --check" ;;
    "self update") : > "$(dirname "$CALLS")/uv-updated" ;;
  esac'
  stub python3 '[ -z "${FAKE_CHECK_FAILS:-}" ]'
  # Instalar o gh pelo apt o põe no PATH.
  stub apt-get 'case "$*" in "install -y gh") printf "#!/bin/sh\n" > "$(dirname "$0")/gh"; chmod +x "$(dirname "$0")/gh" ;; esac'
}

# A mesma máquina como um Mac: Homebrew no lugar do apt.
healthy_mac() {
  healthy_machine
  rm "$SANDBOX/bin/apt-get"
  stub xcode-select '[ -z "${FAKE_NO_CLT:-}" ]'
  stub brew 'case "$*" in "install gh") printf "#!/bin/sh\n" > "$(dirname "$0")/gh"; chmod +x "$(dirname "$0")/gh" ;; esac'
}

# run <check|fix> [VAR=valor...]: deixa a saída em OUTPUT e o código em CODE.
run() {
  local command="$1"
  shift
  OUTPUT="$(cd "$SANDBOX" && env -i PATH="$SANDBOX/bin" HOME="$SANDBOX/home" USER=ada CALLS="$SANDBOX/calls" "$@" \
    "$SANDBOX/bin/bash" "$SANDBOX/case/.claude/skills/setup-fde/scripts/setup-fde.sh" "$command" 2>/dev/null </dev/null)"
  CODE=$?
}

installs_run() { grep -E "^($INSTALLS)" "$SANDBOX/calls" || true; }

expect() {
  local name="$1"
  shift
  if "$@"; then echo "ok    $name"; else echo "FAIL  $name"; FAILURES=$((FAILURES + 1)); fi
}

line_is() { echo "$OUTPUT" | grep -Eq "^$1 +$2( |\$)"; }
exits() { [ "$CODE" -eq "$1" ]; }
every_status_is_known() { ! echo "$OUTPUT" | grep -Evq '^(ok|missing|outdated|manual) '; }
every_line_is_ok() { ! echo "$OUTPUT" | grep -vq '^ok '; }
no_install_ran() { [ -z "$(installs_run)" ]; }
only_install_is() { [ "$(installs_run)" = "$1" ]; }
ran() { grep -Fq -- "$1" "$SANDBOX/calls"; }
never_ran() { ! grep -Fq -- "$1" "$SANDBOX/calls"; }
detail_has() { echo "$OUTPUT" | grep -E "^[a-z]+ +$1 " | grep -Fq -- "$2"; }
lists_items() { [ "$(echo "$OUTPUT" | awk '{print $2}' | tr '\n' ' ')" = "$1" ]; }

# covers #50/AC-2
healthy_machine
run check
expect "uma máquina pronta tem todas as linhas ok" every_line_is_ok
expect "uma máquina pronta sai 0" exits 0
expect "os itens saem nesta ordem" lists_items "git gh uv python claude git-identity gh-login case-clone uv-sync check-setup "
rm "$SANDBOX/bin/claude"
run check
expect "uma ferramenta que falta sai missing" line_is missing claude
expect "toda linha tem um dos quatro status" every_status_is_known
expect "um item que não está ok sai 1" exits 1
expect "o check não instala nada" no_install_ran

# covers #50/AC-3
run fix
expect "o fix instala a ferramenta que falta" line_is ok claude
expect "depois do fix a máquina sai 0" exits 0
expect "o fix só rodou o instalador do claude" only_install_is "curl -fsSL https://claude.ai/install.sh"

healthy_machine
rm "$SANDBOX/bin/gh"
run fix
expect "no Ubuntu o gh vem do apt" ran "apt-get install -y gh"
expect "o repositório do gh entra sem gpg" never_ran "gpg --dearmor"
expect "a chave do repositório do gh vem do cli.github.com" ran "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg"
expect "no Ubuntu o gh fica ok" line_is ok gh

healthy_mac
run check FAKE_SYSTEM=Darwin
expect "um Mac pronto tem todas as linhas ok" every_line_is_ok
expect "o Mac começa pelo brew" line_is ok brew
rm "$SANDBOX/bin/gh"
run fix FAKE_SYSTEM=Darwin
expect "no Mac o gh vem do Homebrew" only_install_is "brew install gh"
expect "no Mac o gh fica ok" line_is ok gh

healthy_mac
rm "$SANDBOX/bin/brew"
run fix FAKE_SYSTEM=Darwin
expect "um Mac sem Homebrew tem o brew manual" line_is manual brew
expect "a linha do brew diz onde instalar" detail_has brew "https://brew.sh"
expect "um Mac sem Homebrew não instala o brew" no_install_ran

healthy_mac
rm "$SANDBOX/bin/brew"
run check FAKE_SYSTEM=Darwin FAKE_NO_CLT=1
expect "um Mac sem as ferramentas da Apple tem o git manual" line_is manual git
expect "a linha do git manda instalar as ferramentas da Apple" detail_has git "xcode-select --install"
expect "sem as ferramentas da Apple, o check não chama o git" never_ran "git "
expect "sem as ferramentas da Apple, o check não chama o python3" never_ran "python3"

healthy_machine
rm "$SANDBOX/bin/gh"
run fix FAKE_SUDO_PASSWORD=1
expect "quando o sudo pede senha, o gh continua missing" line_is missing gh
expect "quando o sudo pede senha, nada entra pelo apt" never_ran "apt-get install"

healthy_machine
run check FAKE_OLD_UV=1
expect "um uv sem o uv sync --check sai outdated" line_is outdated uv
run fix FAKE_OLD_UV=1
expect "o fix atualiza o uv e mais nada" only_install_is "uv self update"
expect "depois da atualização o uv fica ok" line_is ok uv

healthy_machine
rm "$SANDBOX/bin/gh"
run fix FAKE_SYSTEM=FreeBSD
expect "num sistema sem instalador, o que falta é manual" line_is manual gh
expect "num sistema sem instalador, nada é instalado" no_install_ran

# covers #50/AC-5
healthy_machine
run fix FAKE_LOGGED_OUT=1
expect "o login é manual" line_is manual gh-login
expect "a linha do login traz o comando" detail_has gh-login "gh auth login"
expect "o fix não tenta o login" no_install_ran
expect "um item manual sai 1" exits 1
healthy_machine
run fix FAKE_NO_IDENTITY=1
expect "a identidade do git é manual" line_is manual git-identity
expect "o fix não escreve a identidade" never_ran "config --global"

# O case: o fork como origin e o original como upstream.
healthy_machine
rm "$SANDBOX/case/scripts/check_setup.py"
run fix
expect "fora do clone, o case-clone é manual" line_is manual case-clone
expect "fora do clone, a linha traz o comando do fork" detail_has case-clone "gh repo fork barte-ai-services/formacao-fde-case --clone"
expect "fora do clone, o uv-sync espera o case-clone" detail_has uv-sync "depende do case-clone"
expect "fora do clone, o fix não faz o fork" no_install_ran

healthy_machine
run fix FAKE_ORIGIN="$ORIGINAL"
expect "um clone do original, e não do fork, é manual" line_is manual case-clone
expect "a linha traz o gh repo fork --remote" detail_has case-clone "gh repo fork --remote"
expect "o fix não faz o fork pela pessoa" no_install_ran

healthy_machine
run check FAKE_ORIGIN=git@github.com:ada/formacao-fde-case.git
expect "um fork por ssh vale" line_is ok case-clone

healthy_machine
run check FAKE_UPSTREAM=
expect "um fork sem upstream sai missing" line_is missing case-clone
run fix FAKE_UPSTREAM=
expect "o fix registra o original como upstream" only_install_is "git -C $SANDBOX/case remote add upstream $ORIGINAL"
expect "depois disso o case-clone fica ok" line_is ok case-clone

healthy_machine
run fix FAKE_UPSTREAM=https://github.com/outra-pessoa/formacao-fde-case.git
expect "um upstream que aponta para outro lugar é manual" detail_has case-clone "git remote set-url upstream"
expect "o fix não troca o upstream" no_install_ran

healthy_machine
rm "$SANDBOX/case/.synced"
run check
expect "a .venv fora de dia sai missing" line_is missing uv-sync
run fix
expect "o fix roda o uv sync e mais nada" only_install_is "uv sync"
expect "depois do uv sync a máquina sai 0" exits 0

healthy_machine
run fix FAKE_CHECK_FAILS=1
expect "o verificador falhando é manual" line_is manual check-setup
expect "a linha manda rodar o verificador" detail_has check-setup "python3 scripts/check_setup.py"

[ "$FAILURES" -eq 0 ] || { echo "$FAILURES falharam"; exit 1; }
echo "all passed"
