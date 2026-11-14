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
INSTALLS='apt-get|brew (install|upgrade)|curl|dpkg -i|npm install|colima start|tar|usermod|sha256sum|supabase login|wrangler login|uv python install|uv self update|uv sync$|git .*remote (add|set-url)|gh auth (login|setup-git|refresh)|gh repo fork|add-apt-repository|claude plugin (install|marketplace add)'
FAILURES=0
SANDBOX=""
REAL_PYTHON="$(type -P python3)"

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
  cp "$HERE/ahrena_faltando.py" "$SANDBOX/case/.claude/skills/setup-fde/scripts/"
  # formacao-fde-ops #57: dois plugins do Ahrena ligados; outro marketplace e desligado não contam.
  cat > "$SANDBOX/case/.claude/settings.json" <<'JSON'
{"enabledPlugins": {"ahrena-engineering-development@ahrena": true, "ahrena-contributing@ahrena": true,
 "outro@outro-marketplace": true, "ahrena-engineering-go@ahrena": false}}
JSON
  : > "$SANDBOX/case/scripts/check_setup.py"
  : > "$SANDBOX/case/.synced"
  : > "$SANDBOX/calls"
  printf 'ID=ubuntu\nVERSION_CODENAME=noble\n' > "$SANDBOX/os-release"
  for tool in sh sed grep head mktemp rm mkdir cat chmod cp dirname ln tr tee awk; do
    ln -s "$(type -P "$tool")" "$SANDBOX/bin/$tool"
  done
  # O bash do sistema, não o primeiro do PATH: no macOS é o 3.2, o mais velho
  # em que o script precisa rodar.
  ln -s /bin/bash "$SANDBOX/bin/bash"
  for tool in apt-get add-apt-repository supabase usermod; do
    stub "$tool" ''
  done
  stub dpkg 'echo amd64'
  # formacao-fde-ops #58: os dublês das ferramentas novas ficam numa pasta à parte, e cada instalador de mentira cria o dublê dele ali.
  stub node 'echo "${FAKE_NODE_VERSION:-v24.1.0}"'
  stub npm 'case "$*" in "install -g --prefix "*" wrangler@"*) mkdir -p "$4/bin"; printf "#!/bin/sh\\n" > "$4/bin/wrangler"; chmod +x "$4/bin/wrangler" ;; esac'
  stub wrangler 'case "$*" in whoami) [ -n "${FAKE_WRANGLER_LOGGED_OUT:-}" ] && echo "You are not authenticated. Please run wrangler login." ;; esac; exit 0'
  stub supabase 'case "$*" in "projects list") [ -z "${FAKE_SUPABASE_LOGGED_OUT:-}" ] ;; esac'
  # formacao-fde-ops #58: O docker responde quando o motor está ligado; o colima start liga.
  stub docker 'case "$*" in info) [ -z "${FAKE_DOCKER_DOWN:-}" ] || [ -f "$(dirname "$CALLS")/colima-started" ] ;; esac'
  # formacao-fde-ops #58: O tar do release do Supabase deixa o binário na pasta que recebeu.
  stub tar 'printf "#!/bin/sh\\n" > "$4/supabase"; chmod +x "$4/supabase"'
  # formacao-fde-ops #58: FAKE_BAD_CHECKSUM faz o hash do Supabase não bater.
  stub sha256sum 'cat > /dev/null; [ -z "${FAKE_BAD_CHECKSUM:-}" ]'
  # formacao-fde-ops #58: uma cópia de cada dublê fica de reserva: o instalador de mentira põe a cópia de volta no PATH, e a ferramenta instalada se comporta como a de verdade.
  mkdir -p "$SANDBOX/spare"
  cp "$SANDBOX/bin/node" "$SANDBOX/bin/npm" "$SANDBOX/bin/docker" "$SANDBOX/spare/"
  stub uname 'case "$1" in -s) echo "${FAKE_SYSTEM:-Linux}" ;; *) echo x86_64 ;; esac'
  # formacao-fde-ops #58: nunca root, e o sudo só repassa para os dublês: nada toca o /etc de verdade.
  stub id 'echo 1000'
  stub sudo 'if [ "$1" = -n ]; then [ -z "${FAKE_SUDO_PASSWORD:-}" ] || exit 1; shift; fi
  case "$1" in apt-get | dpkg | add-apt-repository | usermod | true) "$@" ;; tee) cat > /dev/null ;; esac'
  # formacao-fde-ops #57: claude plugin list --json; FAKE_PLUGINS troca a lista.
  # formacao-fde-ops #57: instalar um plugin deixa a lista completa; FAKE_INSTALL_FAILS faz a instalação falhar.
  stub claude 'd="$(dirname "$CALLS")"
  case "$*" in
  "plugin marketplace list") [ -n "${FAKE_NO_MARKETPLACE:-}" ] && [ ! -f "$d/marketplace-added" ] || echo "ahrena (ahrenatechnology/ahrena-framework)" ;;
  "plugin marketplace add"*) : > "$d/marketplace-added" ;;
  "plugin install "*) [ -z "${FAKE_INSTALL_FAILS:-}" ] || exit 1; : > "$d/plugins-installed" ;;
  "plugin list --json")
    if [ -n "${FAKE_PLUGINS:-}" ] && [ ! -f "$d/plugins-installed" ]; then echo "$FAKE_PLUGINS"; exit; fi
    c="$(dirname "$CALLS")/case"
    echo "[{\"id\":\"ahrena-engineering-development@ahrena\",\"scope\":\"project\",\"enabled\":true,\"projectPath\":\"$c\"},
      {\"id\":\"ahrena-contributing@ahrena\",\"scope\":\"user\",\"enabled\":true}]" ;;
  esac'
  cp "$SANDBOX/bin/claude" "$SANDBOX/claude-instalado"
  # formacao-fde-ops #57: Instalar o claude o põe no PATH, como o instalador de verdade.
  stub curl 'case "$*" in
    *claude.ai/install.sh*) cp "$(dirname "$CALLS")/claude-instalado" "$(dirname "$0")/claude" ;;
    "-fsSL -o "*) : > "$3" ;;
  esac'
  stub git 'case "$*" in
    --version) echo "git version ${FAKE_GIT_VERSION:-2.47.1}" ;;
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
  # formacao-fde-ops #57: o python3 de verdade lê os plugins.
  stub python3 'case "$1" in *ahrena_faltando.py) exec '"$REAL_PYTHON"' "$@" ;; esac
  [ -z "${FAKE_CHECK_FAILS:-}" ]'
  # formacao-fde-ops #57: Instalar o gh pelo apt o põe no PATH.
  stub apt-get 'case "$*" in
    "install -y gh") printf "#!/bin/sh\n" > "$(dirname "$0")/gh"; chmod +x "$(dirname "$0")/gh" ;;
    "install -y docker-ce "*) cp "$(dirname "$CALLS")/spare/docker" "$(dirname "$0")/" ;;
    "install -y nodejs") cp "$(dirname "$CALLS")/spare/node" "$(dirname "$CALLS")/spare/npm" "$(dirname "$0")/" ;;
  esac'
}

# A mesma máquina como um Mac: Homebrew no lugar do apt.
healthy_mac() {
  healthy_machine
  rm "$SANDBOX/bin/apt-get"
  stub xcode-select '[ -z "${FAKE_NO_CLT:-}" ]'
  stub colima 'case "$*" in start) : > "$(dirname "$CALLS")/colima-started" ;; esac'
  cp "$SANDBOX/bin/colima" "$SANDBOX/spare/"
  stub brew 'case "$*" in
    "list node") exit 0 ;;
    "install docker" | "install colima") cp "$(dirname "$CALLS")/spare/$2" "$(dirname "$0")/" ;;
    "install gh" | "install supabase/tap/supabase")
      t="${2##*/}"; printf "#!/bin/sh\n" > "$(dirname "$0")/$t"; chmod +x "$(dirname "$0")/$t" ;;
  esac'
}

# run <check|fix> [VAR=valor...]: deixa a saída em OUTPUT e o código em CODE.
run() {
  local command="$1"
  shift
  OUTPUT="$(cd "$SANDBOX" && env -i PATH="$SANDBOX/bin" HOME="$SANDBOX/home" USER=ada CALLS="$SANDBOX/calls" OS_RELEASE="$SANDBOX/os-release" "$@" \
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
expect "os itens saem nesta ordem" lists_items "git gh node uv python docker docker-daemon supabase wrangler claude git-identity gh-login supabase-login wrangler-login case-clone uv-sync check-setup ahrena "
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
expect "o Mac confere o colima" lists_items "brew git gh node uv python docker colima docker-daemon supabase wrangler claude git-identity gh-login supabase-login wrangler-login case-clone uv-sync check-setup ahrena "
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

# covers formacao-fde-ops #58/AC-1, AC-2
# formacao-fde-ops #58: o Node.js com o npm, e numa versão que o Wrangler aceita.
healthy_machine
run check FAKE_NODE_VERSION=v18.19.1
expect "um Node.js 18 sai outdated" line_is outdated node
expect "a linha do node diz a versão pedida" detail_has node "22.12 ou mais novo"
run check FAKE_NODE_VERSION=v22.11.0
expect "um Node.js 22.11 sai outdated, porque o Wrangler pede o 22.12" line_is outdated node
run check FAKE_NODE_VERSION=v22.12.0
expect "um Node.js 22.12 fica ok" line_is ok node
healthy_machine
rm "$SANDBOX/bin/node" "$SANDBOX/bin/npm" "$SANDBOX/bin/wrangler"
run check
expect "sem Node.js, o node sai missing" line_is missing node
expect "sem npm, o wrangler espera o node" detail_has wrangler "depende do node"
run fix
expect "no Ubuntu o Node.js vem da NodeSource" ran "deb.nodesource.com/gpgkey/nodesource-repo.gpg.key"
expect "no Ubuntu o Node.js entra pelo apt" ran "apt-get install -y nodejs"
expect "o wrangler entra pelo npm, sem sudo" ran "npm install -g --prefix $SANDBOX/home/.local wrangler@4."
expect "depois do fix o node fica ok" line_is ok node
expect "depois do fix o wrangler fica ok" line_is ok wrangler

healthy_mac
run fix FAKE_SYSTEM=Darwin FAKE_NODE_VERSION=v20.0.0
expect "no Mac o Node.js velho é atualizado pelo Homebrew" ran "brew upgrade node"

# formacao-fde-ops #58: O Supabase CLI: Homebrew no Mac, o binário do release no Linux.
healthy_machine
rm "$SANDBOX/bin/supabase"
run check
expect "sem o Supabase CLI, o supabase sai missing" line_is missing supabase
expect "sem o Supabase CLI, o login espera ele" detail_has supabase-login "depende do supabase"
run fix
expect "no Ubuntu o Supabase CLI vem de um release fixo do GitHub" ran "https://github.com/supabase/cli/releases/download/v3."
expect "no Ubuntu o Supabase CLI confere o hash" ran "sha256sum -c -"
expect "no Ubuntu o Supabase CLI não passa pelo npm" never_ran "npm install -g --prefix $SANDBOX/home/.local supabase"
expect "no Ubuntu o Supabase CLI não pede sudo" never_ran "sudo"
expect "depois do fix o supabase fica ok" line_is ok supabase

healthy_mac
rm "$SANDBOX/bin/supabase"
run fix FAKE_SYSTEM=Darwin
expect "no Mac o Supabase CLI vem do tap do Supabase" only_install_is "brew install supabase/tap/supabase"
expect "no Mac o supabase fica ok" line_is ok supabase

healthy_machine
rm "$SANDBOX/bin/supabase"
run fix FAKE_BAD_CHECKSUM=1
expect "um hash do Supabase que não bate não instala nada" never_ran "tar "
expect "com o hash errado o supabase continua missing" line_is missing supabase

# formacao-fde-ops #58: O Docker: Colima no Mac, Docker Engine no Linux, nunca o Docker Desktop.
healthy_mac
rm "$SANDBOX/bin/docker" "$SANDBOX/bin/colima"
run fix FAKE_SYSTEM=Darwin FAKE_DOCKER_DOWN=1
expect "no Mac o docker vem do Homebrew" ran "brew install docker"
expect "no Mac o motor é o Colima" ran "brew install colima"
expect "no Mac o fix liga o Colima" ran "colima start"
expect "no Mac nada instala o Docker Desktop" never_ran "cask"
expect "depois do fix o motor do Mac responde" line_is ok docker-daemon

healthy_mac
rm "$SANDBOX/bin/colima"
run check FAKE_SYSTEM=Darwin
expect "um Mac em que o docker já responde não precisa do Colima" line_is ok colima

healthy_machine
rm "$SANDBOX/bin/docker"
run check
expect "sem o docker, o docker sai missing" line_is missing docker
expect "sem o docker, o motor espera ele" detail_has docker-daemon "depende do docker"
run fix
expect "no Ubuntu a chave do Docker vem do download.docker.com" ran "curl -fsSL https://download.docker.com/linux/ubuntu/gpg"
expect "no Ubuntu o Docker Engine entra pelo apt" ran "apt-get install -y docker-ce docker-ce-cli containerd.io"
expect "nada roda o get.docker.com" never_ran "get.docker.com"
expect "no Ubuntu a pessoa entra no grupo docker" ran "usermod -aG docker ada"
expect "no Ubuntu o docker fica ok" line_is ok docker

healthy_machine
rm "$SANDBOX/bin/docker"
run fix FAKE_SUDO_PASSWORD=1
expect "quando o sudo pede senha, o docker continua missing" line_is missing docker
expect "quando o sudo pede senha, o Docker Engine não entra" never_ran "apt-get install"
expect "quando o sudo pede senha, ninguém entra no grupo docker" never_ran "usermod"

healthy_machine
run fix FAKE_DOCKER_DOWN=1
expect "no Ubuntu o motor parado é manual" line_is manual docker-daemon
expect "a linha do motor traz o systemctl e o grupo" detail_has docker-daemon "sudo usermod -aG docker"
expect "no Ubuntu o fix não liga o motor" no_install_ran

# covers formacao-fde-ops #58/AC-3
healthy_machine
run fix FAKE_SUPABASE_LOGGED_OUT=1 FAKE_WRANGLER_LOGGED_OUT=1
expect "o login do Supabase é manual" line_is manual supabase-login
expect "a linha do login do Supabase traz o comando" detail_has supabase-login "supabase login"
expect "o login da Cloudflare é manual" line_is manual wrangler-login
expect "a linha do login da Cloudflare traz o comando" detail_has wrangler-login "wrangler login"
expect "o fix não faz nenhum dos dois logins" no_install_ran
healthy_machine
rm "$SANDBOX/bin/wrangler"
run check
expect "sem o wrangler, o login espera ele" detail_has wrangler-login "depende do wrangler"

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

# covers formacao-fde-ops #56/AC-2
healthy_machine
run check
expect "com os plugins do case instalados, o ahrena fica ok" line_is ok ahrena
run check FAKE_PLUGINS='[{"id":"ahrena-contributing@ahrena","scope":"user","enabled":true}]'
expect "um plugin do case que não está instalado deixa o ahrena missing" line_is missing ahrena
expect "a linha do ahrena diz qual plugin falta" detail_has ahrena "faltam: ahrena-engineering-development"
expect "a linha do ahrena não cita o que já está instalado" eval '! detail_has ahrena ahrena-contributing'
expect "o ahrena faltando sai 1" exits 1
run check FAKE_PLUGINS="[{\"id\":\"ahrena-engineering-development@ahrena\",\"scope\":\"project\",\"enabled\":true,\"projectPath\":\"/outra/pasta\"},{\"id\":\"ahrena-contributing@ahrena\",\"scope\":\"user\",\"enabled\":true}]"
expect "um plugin instalado para outra pasta não conta" line_is missing ahrena
run check FAKE_PLUGINS="[{\"id\":\"ahrena-engineering-development@ahrena\",\"scope\":\"user\",\"enabled\":false},{\"id\":\"ahrena-contributing@ahrena\",\"scope\":\"user\",\"enabled\":true}]"
expect "um plugin desabilitado não conta" line_is missing ahrena
run check FAKE_PLUGINS='nada disso é json'
expect "uma lista que não se lê deixa o ahrena manual" detail_has ahrena "não deu para ler os plugins"

# covers formacao-fde-ops #56/AC-3
FALTA_UM='[{"id":"ahrena-contributing@ahrena","scope":"user","enabled":true}]'
healthy_machine
run fix FAKE_PLUGINS="$FALTA_UM"
expect "o fix instala só o plugin que falta, no escopo local" only_install_is "claude plugin install ahrena-engineering-development@ahrena --scope local"
expect "depois do fix o ahrena fica ok" line_is ok ahrena
expect "depois do fix a máquina com o Ahrena sai 0" exits 0
expect "o fix não toca o settings.json do case" eval 'grep -q outro-marketplace "$SANDBOX/case/.claude/settings.json"'

healthy_machine
run fix FAKE_PLUGINS="$FALTA_UM" FAKE_NO_MARKETPLACE=1
expect "sem o marketplace, o fix registra o ahrena antes" ran "claude plugin marketplace add ahrenatechnology/ahrena-framework"
expect "e depois instala o plugin" ran "claude plugin install ahrena-engineering-development@ahrena"

healthy_machine
run fix FAKE_PLUGINS="$FALTA_UM" FAKE_INSTALL_FAILS=1
expect "quando a instalação falha, o ahrena continua missing" line_is missing ahrena

healthy_machine
run fix FAKE_PLUGINS="$FALTA_UM" FAKE_GIT_VERSION=2.34.1 FAKE_SUDO_PASSWORD=1
expect "com o git velho, o ahrena espera o git" detail_has ahrena "depende do git 2.45"
expect "com o git velho, o fix não tenta instalar plugin" never_ran "claude plugin install"

# O git: o Claude Code precisa de um git novo para instalar os plugins.
healthy_machine
run check FAKE_GIT_VERSION=2.34.1
expect "o git 2.34 do Ubuntu sai outdated" line_is outdated git
run fix FAKE_GIT_VERSION=2.34.1
expect "no Ubuntu, o git novo vem do PPA git-core" ran "add-apt-repository -y ppa:git-core/ppa"
expect "e depois do apt" ran "apt-get install -y git"

healthy_machine
echo 'ID=debian' > "$SANDBOX/os-release"
run fix FAKE_GIT_VERSION=2.39.2
expect "no Debian sem PPA, o git velho é manual" line_is manual git
expect "no Debian, o fix não acrescenta PPA" never_ran "add-apt-repository"

healthy_mac
run fix FAKE_SYSTEM=Darwin FAKE_GIT_VERSION=2.39.5
expect "no Mac, o git velho da Apple é trocado pelo do Homebrew" ran "brew install git"

healthy_machine
run check FAKE_GIT_VERSION=2.45.0
expect "o git no piso fica ok" line_is ok git

healthy_machine
rm "$SANDBOX/bin/claude"
run check
expect "sem o claude, o ahrena espera por ele" detail_has ahrena "depende do claude"

# covers formacao-fde-ops #56/AC-2
healthy_machine
echo '<<<<<<< conflito' > "$SANDBOX/case/.claude/settings.json"
run check
expect "um settings.json que não se lê deixa o ahrena manual" detail_has ahrena "não deu para ler"

[ "$FAILURES" -eq 0 ] || { echo "$FAILURES falharam"; exit 1; }
echo "all passed"
