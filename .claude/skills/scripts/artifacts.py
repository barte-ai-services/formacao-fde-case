#!/usr/bin/env python3
"""Artefatos do claude.ai versionados no repositorio.

Cada pasta de artefato tem um artifact.json:

    {
      "pages": {
        "<nome>": {
          "file": "index.html",
          "title": "...",
          "files": ["outra-pagina.html", "ds/theme.js"],
          "home": "team",
          "links": {"team": "https://claude.ai/artifact/...", "max": "..."},
          "capabilities": {}
        }
      },
      "publishOrder": ["<nome>", ...]
    }

`home` e' a org onde a pagina mora. Uma sessao so atualiza artefatos da org em
que esta logada, e publicar de outra org cria um link novo, com outro banco: o
`plan` recusa. Mudar de casa e' decisao da pessoa, com `plan --move`. Sem `home`,
a casa e' a org do unico link que existe; com links em mais de uma org e sem
`home`, o `plan` pede que ela seja gravada (`record --home`).

Um link fixo para outro artefato vira {{artefato:<nome>}} no HTML e e' trocado
pelo link da org de destino na hora de publicar.

Toda pagina HTML sai do `plan` com a origem gravada numa linha de formato fixo:

    <!-- artifact-source repo="dono/repo" path="artifacts/portal" page="portal" commit="abc1234" -->

O conteudo anda por git: o `plan` busca a pasta na branch principal do GitHub
(`git fetch` e `git show`), e o `submit` faz o commit e o push. O `gh` so e' usado
para abrir o pull request e, no hook, para ler o PR que foi mergeado.

Comandos:
  list     lista os artefatos de um repositorio, ou acha a pasta de um link
  hook     le o evento PostToolUse no stdin; depois de um `gh pr merge` cujo PR
           mexeu em pastas de artefato, devolve o lembrete de publicar
  submit   leva uma pasta de artefato para o GitHub: branch, commit so da pasta,
           push e pull request
  plan     busca a pasta na branch principal do GitHub, monta numa pasta de saida
           os arquivos prontos para publicar numa org e imprime o plano em JSON
  record   grava o link de uma pagina numa org, e a casa dela, no artifact.json
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

MANIFEST = "artifact.json"
MARKER = re.compile(r"\{\{artefato:([A-Za-z0-9_.-]+)\}\}")
MERGE = re.compile(r"\bgh\s+pr\s+merge\b(.*)", re.S)
STAMP = re.compile(r"<!-- artifact-source\b[^>]*-->\n?")
REMOTE = re.compile(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$")


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def must_git(repo, *args):
    """Como `git`, mas para o script com a mensagem do git quando o comando falha."""
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {out.stderr.strip() or 'falhou'}")
    return out.stdout.strip()


def repo_root(path):
    return git(path, "rev-parse", "--show-toplevel")


def default_branch(root):
    """A branch principal do remoto, lida de origin/HEAD; `main` quando ele nao diz."""
    head = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    return head.split("/", 1)[1] if head and "/" in head else "main"


def repo_slug(root):
    m = REMOTE.search(git(root, "remote", "get-url", "origin") or "")
    return m.group(1) if m else None


class Tree:
    """Os arquivos de um repositorio, lidos do disco ou de uma ref do git.

    Com `ref`, nada do disco e' lido: o que sai e' o que aquele commit guarda, e
    uma branch de trabalho ou uma mudanca nao commitada nao chegam ao claude.ai.
    """

    def __init__(self, root, ref=None):
        self.root, self.ref = root, ref

    def read(self, rel):
        if self.ref is None:
            return open(os.path.join(self.root, rel), "rb").read()
        out = subprocess.run(["git", "-C", self.root, "show", f"{self.ref}:{rel}"], capture_output=True)
        if out.returncode != 0:
            sys.exit(f"{rel} nao existe em {self.ref}: a pasta ja foi mergeada na branch principal?")
        return out.stdout

    def manifests(self):
        """pasta (relativa a raiz) -> manifesto, de todo artifact.json do repositorio."""
        if self.ref is None:
            return {os.path.relpath(f, self.root).replace(os.sep, "/"): m for f, m in all_manifests(self.root).items()}
        names = must_git(self.root, "ls-tree", "-r", "--name-only", self.ref).splitlines()
        return {os.path.dirname(n) or ".": json.loads(self.read(n)) for n in names if os.path.basename(n) == MANIFEST}

    def commit(self):
        return git(self.root, "rev-parse", "--short", self.ref or "HEAD")

    def dirty(self, folder):
        return self.ref is None and bool(git(self.root, "status", "--porcelain", "--", folder))


def current_org():
    """Chave da org logada no Claude Code, no vocabulario dos manifestos."""
    try:
        acc = json.load(open(os.path.expanduser("~/.claude.json"), encoding="utf-8"))["oauthAccount"]
    except (OSError, KeyError, ValueError):
        return None
    kind = acc.get("organizationType") or ""
    if kind in ("claude_team", "claude_enterprise"):
        return "team"
    if kind in ("claude_max", "claude_pro"):
        return "max"
    name = (acc.get("organizationName") or "").lower()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-") or None


def load(folder):
    return json.load(open(os.path.join(folder, MANIFEST), encoding="utf-8"))


def all_manifests(root):
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".claude")]
        if MANIFEST in filenames:
            found[dirpath] = load(dirpath)
    return found


# ------------------------------------------------------------------ hook

def command_dir(command, cwd):
    """Pasta em que o comando rodou: `cd X && gh ...`."""
    m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)\s*&&", command)
    if m:
        return os.path.join(cwd, os.path.expanduser(shlex.split(m.group(1))[0]))
    return cwd


def merge_args(command):
    """Seletor do PR e repo de um `gh pr merge`, ou None se o comando nao e' um merge."""
    m = MERGE.search(command)
    if not m:
        return None
    try:
        tokens = shlex.split(re.split(r"\s(?:&&|\|\||;|\|)\s", m.group(1))[0])
    except ValueError:
        tokens = m.group(1).split()
    selector, repo, auto, skip = None, None, False, False
    for i, tok in enumerate(tokens):
        if skip:
            skip = False
            continue
        if tok in ("-R", "--repo"):
            repo, skip = (tokens[i + 1] if i + 1 < len(tokens) else None), True
        elif tok.startswith("--repo="):
            repo = tok.split("=", 1)[1]
        elif tok == "--auto":
            auto = True
        elif tok in ("-b", "--body", "-t", "--subject", "-F", "--body-file", "--match-head-commit", "-A", "--author-email"):
            skip = True
        elif not tok.startswith("-") and selector is None:
            selector = tok
    return selector, repo, auto


def gh_json(cwd, *args):
    """Roda `gh` e devolve a resposta JSON como objeto, ou None.

    None quando o gh nao esta instalado, nao esta autenticado, demorou demais ou
    devolveu algo que nao e' JSON. O chamador trata None como "nao consegui falar
    com o forge", entao o plugin degrada em vez de quebrar quando falta o gh ou o
    token: o submit cai no link de comparacao, e o hook apenas nao da o lembrete.
    """
    if not shutil.which("gh"):
        return None
    try:
        out = subprocess.run(["gh", *args], cwd=cwd, capture_output=True, text=True, timeout=12)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except ValueError:
        return None


def artifact_folders(root, paths):
    """Pastas com artifact.json tocadas por `paths` (relativos a `root`)."""
    folders = {}
    for rel in paths:
        folder = os.path.dirname(os.path.join(root, rel))
        while folder.startswith(root):
            if os.path.isfile(os.path.join(folder, MANIFEST)):
                folders.setdefault(folder, []).append(rel)
                break
            if folder == root:
                break
            folder = os.path.dirname(folder)
    # um PR que so grava links no manifesto nao pede publicacao nova
    return {f: files for f, files in folders.items() if any(os.path.basename(x) != MANIFEST for x in files)}


def cmd_hook(_args):
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    command = (event.get("tool_input") or {}).get("command") or ""
    parsed = merge_args(command)
    if parsed is None:
        return
    selector, repo, auto = parsed
    cwd = command_dir(command, event.get("cwd") or os.getcwd())
    view = ["pr", "view", *([selector] if selector else []), *(["-R", repo] if repo else []),
            "--json", "number,state,baseRefName,files,url"]
    pr = gh_json(cwd, *view)
    if not pr:
        return
    root = repo_root(cwd)
    if not root:
        return  # merge de um repo que nao esta neste disco: nao ha manifesto para ler
    folders = artifact_folders(root, [f["path"] for f in pr.get("files") or []])
    if not folders:
        return
    org = current_org() or "<org>"
    rels = ", ".join(os.path.relpath(f, root) + "/" for f in sorted(folders))
    if pr.get("state") != "MERGED":
        if auto:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
                f"O PR #{pr['number']} entrou em auto-merge e muda artefatos versionados ({rels}). "
                "Eles so devem ser publicados depois que o merge acontecer: avise o usuario que a publicacao fica pendente."}},
                ensure_ascii=False))
        return
    lines = [f"O PR #{pr['number']} foi mergeado em {pr.get('baseRefName')} e muda artefatos versionados. "
             f"Publique cada pasta abaixo na org logada ({org}), seguindo a skill publishing-artifacts: o `plan` "
             f"busca a pasta em {pr.get('baseRefName')} no GitHub, entao nao e' preciso atualizar a copia local."]
    for folder in sorted(folders):
        pages = load(folder).get("pages", {})
        status = ", ".join(f"{name}: {'link existente' if org in (p.get('links') or {}) else 'primeira publicacao'}"
                           for name, p in pages.items())
        lines.append(f"- {os.path.relpath(folder, root)}/ ({status})")
    lines.append("Se o usuario pediu para nao publicar agora, apenas avise que ficou pendente.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": "\n".join(lines)}}, ensure_ascii=False))


# ------------------------------------------------------------------ list

def cmd_list(args):
    start = os.path.abspath(args.dir)
    root = repo_root(start) or start
    org = args.org or current_org()
    want = args.url.rstrip("/") if args.url else None
    rows = []
    for folder, manifest in sorted(all_manifests(root).items()):
        for name, page in manifest.get("pages", {}).items():
            links = page.get("links") or {}
            if want and want not in (u.rstrip("/") for u in links.values()):
                continue
            rows.append({"folder": os.path.relpath(folder, root).replace(os.sep, "/"), "page": name,
                         "title": page.get("title"), "file": page.get("file"),
                         "url": links.get(org), "links": links})
    print(json.dumps({"org": org, "root": root, "artifacts": rows}, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ submit

def cmd_submit(args):
    folder = os.path.abspath(args.dir)
    root = repo_root(folder)
    if not root or not os.path.isfile(os.path.join(folder, MANIFEST)):
        sys.exit(f"{args.dir} nao e' uma pasta de artefato dentro de um repositorio git (falta o {MANIFEST})")
    rel = os.path.relpath(folder, root).replace(os.sep, "/")
    base = default_branch(root)
    if args.branch == base:
        sys.exit(f"{base} e' a branch principal: o artefato chega nela por pull request")
    if git(root, "branch", "--show-current") != args.branch:
        exists = git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{args.branch}")
        must_git(root, "switch", *([] if exists else ["-c"]), args.branch)
    must_git(root, "add", "--", rel)
    staged = must_git(root, "diff", "--cached", "--name-only").splitlines()
    outside = [n for n in staged if not n.startswith(rel + "/")]
    if outside:
        sys.exit("ha arquivos preparados fora da pasta do artefato; tire-os do index antes: " + ", ".join(outside))
    if staged:
        must_git(root, "commit", "-m", args.message)
    must_git(root, "push", "-u", "origin", args.branch)
    result = {"folder": rel, "branch": args.branch, "base": base, "commit": git(root, "rev-parse", "--short", "HEAD"),
              "committed": staged}
    result.update(open_pull_request(root, base, args))
    print(json.dumps(result, ensure_ascii=False, indent=1))


def open_pull_request(root, base, args):
    """Abre o PR com o gh; sem ele, devolve o endereco em que a pessoa abre."""
    title, _, body = args.message.partition("\n")
    slug = repo_slug(root)
    compare = f"https://github.com/{slug}/compare/{base}...{args.branch}?expand=1" if slug else None
    if not shutil.which("gh"):
        return {"pull_request": None, "open_at": compare}
    existing = gh_json(root, "pr", "view", args.branch, "--json", "url,state")
    if existing and existing.get("state") == "OPEN":
        return {"pull_request": existing["url"]}
    out = subprocess.run(["gh", "pr", "create", "--base", base, "--head", args.branch, "--title", title,
                          "--body", body.strip() or title], cwd=root, capture_output=True, text=True)
    if out.returncode != 0:
        return {"pull_request": None, "open_at": compare, "gh_error": out.stderr.strip()}
    return {"pull_request": out.stdout.strip().splitlines()[-1]}


# ------------------------------------------------------------------ plan

def checkout_of(args, out_root):
    """A raiz do repositorio e a pasta do artefato dentro dela.

    Com --repo nao e' preciso ter o repositorio no disco: um clone raso, sem
    arquivos de trabalho, vai para a pasta de saida e serve so de onde ler a ref.
    """
    if not args.repo:
        folder = os.path.abspath(args.dir)
        root = repo_root(folder)
        if not root:
            sys.exit(f"{args.dir} nao esta num repositorio git: passe --repo dono/nome e a pasta relativa a raiz dele")
        return root, os.path.relpath(folder, root).replace(os.sep, "/")
    root = os.path.join(out_root, ".repos", args.repo.replace("/", "__"))
    if not os.path.isdir(os.path.join(root, ".git")):
        os.makedirs(os.path.dirname(root), exist_ok=True)
        out = subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--no-checkout",
                              f"git@github.com:{args.repo}.git", root], capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit(f"git clone de {args.repo}: {out.stderr.strip()}")
    return root, args.dir.strip("/")


def tree_of(args, root):
    """De onde o plano le: a branch principal no GitHub, ou o disco com --local."""
    if args.local:
        return Tree(root)
    branch = args.ref or default_branch(root)
    must_git(root, "fetch", "--quiet", "origin", branch)
    # uma ref que nao e' a principal pode nao ter branch de rastreio: le o que o fetch acabou de trazer
    return Tree(root, must_git(root, "rev-parse", "FETCH_HEAD") if args.ref else f"origin/{branch}")


def source_of(tree, folder, name):
    """De onde a pagina vem: repo, pasta, pagina e commit, lidos do git."""
    src = {"repo": repo_slug(tree.root), "path": folder, "page": name, "commit": tree.commit(),
           # a pasta tem mudanca fora do commit: o publicado nao e' o que o commit guarda
           "dirty": "true" if tree.dirty(folder) else None}
    return {k: v for k, v in src.items() if v}


def stamp(text, src):
    """Grava a origem no HTML, logo depois do <title>, trocando a que ja houver."""
    line = "<!-- artifact-source " + " ".join(f'{k}="{v}"' for k, v in src.items()) + " -->\n"
    text = STAMP.sub("", text)
    m = re.search(r"</title>[ \t]*\n?", text, re.I)
    at = m.end() if m else 0
    return text[:at] + line + text[at:]


def resolve_links(manifests, folder, org):
    """nome da pagina -> link na org, procurando na pasta e depois no repo inteiro."""
    links = {}
    for _path, manifest in sorted(manifests.items(), key=lambda kv: kv[0] != folder):
        for name, page in manifest.get("pages", {}).items():
            url = (page.get("links") or {}).get(org)
            if url and name not in links:
                links[name] = url
    return links


def home_of(page):
    """A org onde a pagina mora: a declarada, ou a do unico link; None se ainda nao foi publicada."""
    links = page.get("links") or {}
    if page.get("home"):
        return page["home"]
    if len(links) == 1:
        return next(iter(links))
    return None


def cmd_plan(args):
    out_root = os.path.abspath(args.out)
    root, folder = checkout_of(args, out_root)
    tree = tree_of(args, root)
    org = args.org or current_org()
    if not org:
        sys.exit("nao achei a org logada em ~/.claude.json: passe --org")
    manifests = tree.manifests()
    if folder not in manifests:
        where = "no disco" if tree.ref is None else f"em {tree.ref}"
        sys.exit(f"{folder}/{MANIFEST} nao existe {where}: a pasta ja foi mergeada? Para um rascunho, use --local")
    manifest = manifests[folder]
    pages = manifest.get("pages", {})
    order = manifest.get("publishOrder") or list(pages)
    # Atualizar e' sempre no link que ja existe. Uma sessao em outra org nao alcanca esse
    # link e, sem esta trava, publicaria um artefato novo, com link e banco novos.
    if not args.move:
        away = []
        for name in order:
            page = pages[name]
            links_here = page.get("links") or {}
            home = home_of(page)
            if home is None and len(links_here) > 1:
                sys.exit(f"{name} tem links em {', '.join(sorted(links_here))} e nenhuma casa: grave a casa com "
                         f"`record {folder} --page {name} --home <org>` antes de publicar")
            if home and home != org:
                away.append(f"{name} mora em {home} ({links_here.get(home, 'sem link')})")
        if away:
            sys.exit("a sessao esta logada em " + org + " e estas paginas moram em outra org: " + "; ".join(away) +
                     ". Abra uma sessao logada na org da casa para atualizar o mesmo link. Para mudar a pagina de"
                     " casa, o que cria um link novo, e' decisao da pessoa: `plan --move`.")
    links = resolve_links(manifests, folder, org)
    plan, missing = [], []
    for name in order:
        page = pages[name]
        out = os.path.join(out_root, os.path.basename(folder), name)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        src_info = source_of(tree, folder, name)
        for rel in [page["file"], *page.get("files", [])]:
            data, dst = tree.read(f"{folder}/{rel}"), os.path.join(out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if rel.endswith((".html", ".js", ".css", ".json", ".md")):
                text = data.decode("utf-8")
                for ref in set(MARKER.findall(text)):
                    if ref not in links:
                        missing.append(f"{name}: {{{{artefato:{ref}}}}} sem link na org {org}")
                text = MARKER.sub(lambda m: links.get(m.group(1), m.group(0)), text)
                if rel.endswith(".html"):
                    text = stamp(text, src_info)
                data = text.encode("utf-8")
            open(dst, "wb").write(data)
        plan.append({
            "page": name,
            "title": page.get("title"),
            "file_path": os.path.join(out, page["file"]),
            "files": {rel: os.path.join(out, rel) for rel in page.get("files", [])},
            "url": (page.get("links") or {}).get(org),
            "home": home_of(page),
            "move": bool(args.move) and home_of(page) not in (None, org),
            "capabilities": page.get("capabilities", {}),
            "source": src_info,
        })
        # a proxima pagina pode apontar para esta; o link so existe depois de publicar
        if not plan[-1]["url"]:
            break
    print(json.dumps({"org": org, "folder": folder, "read_from": tree.ref or "disco (--local)", "plan": plan,
                      "unresolved": missing, "remaining": order[len(plan):]}, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ record

def cmd_record(args):
    folder = os.path.abspath(args.dir)
    org = args.org or current_org()
    if not org:
        sys.exit("nao achei a org logada em ~/.claude.json: passe --org")
    if args.url and not re.match(r"^https://claude\.ai/(code/)?artifact/[A-Za-z0-9-]+$", args.url):
        sys.exit(f"nao parece um link de artefato: {args.url}")
    if not args.url and not args.home:
        sys.exit("passe --url, --home ou os dois")
    path = os.path.join(folder, MANIFEST)
    manifest = load(folder)
    page = manifest["pages"].get(args.page)
    if page is None:
        sys.exit(f"pagina {args.page} nao existe em {path}")
    if args.url:
        page.setdefault("links", {})[org] = args.url
        print(f"{args.page}.links.{org} = {args.url}")
        # A primeira publicacao define a casa.
        page.setdefault("home", org)
    if args.home:
        page["home"] = args.home
    print(f"{args.page}.home = {page.get('home')}")
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    open(path, "w", encoding="utf-8").write(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hook").set_defaults(fn=cmd_hook)
    s = sub.add_parser("list")
    s.add_argument("dir", nargs="?", default=".", help="qualquer pasta do repositorio (padrao: a atual)")
    s.add_argument("--url", help="so o artefato que tem este link, em qualquer org")
    s.add_argument("--org", help="chave da org nos links (padrao: a logada)")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("submit")
    s.add_argument("dir", help="pasta com o artifact.json")
    s.add_argument("--branch", required=True, help="branch de trabalho, no formato tipo/assunto")
    s.add_argument("--message", required=True, help="mensagem do commit; a primeira linha vira o titulo do PR")
    s.set_defaults(fn=cmd_submit)
    s = sub.add_parser("plan")
    s.add_argument("dir", help="pasta com o artifact.json; com --repo, relativa a raiz do repositorio")
    s.add_argument("--out", required=True, help="pasta de saida (o scratchpad da sessao)")
    s.add_argument("--org", help="chave da org nos links (padrao: a logada)")
    s.add_argument("--repo", help="dono/nome no GitHub, quando o repositorio nao esta no disco")
    s.add_argument("--ref", help="branch ou tag do GitHub a ler (padrao: a branch principal)")
    s.add_argument("--local", action="store_true", help="le do disco, para publicar um rascunho num link de teste")
    s.add_argument("--move", action="store_true",
                   help="publica numa org que nao e' a casa: cria link novo. So quando a pessoa pediu para mudar de casa")
    s.set_defaults(fn=cmd_plan)
    s = sub.add_parser("record")
    s.add_argument("dir")
    s.add_argument("--page", required=True)
    s.add_argument("--url")
    s.add_argument("--org")
    s.add_argument("--home", help="grava a org onde a pagina mora")
    s.set_defaults(fn=cmd_record)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
