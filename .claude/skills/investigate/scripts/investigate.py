#!/usr/bin/env python3
"""Evidence collection for the investigate skill. Standard library only.

Subcommands: baseline, workspace, run, classify, context, impact.
Evidence goes to ~/.oss-contrib/<owner>__<repo>/<issue>/. Never writes to the
target repository's working tree.
"""

import argparse
import ast
import fnmatch
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_ROOT = Path.home() / ".oss-contrib"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
             ".tox", ".mypy_cache", ".pytest_cache", ".next", "coverage", "site-packages"}
PY_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
MAX_SITES = 200
TAIL_LINES = 40


def sh(args, cwd=None):
    """Run a command and return stripped stdout, or None on failure."""
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_slug(repo):
    url = sh(["git", "remote", "get-url", "origin"], cwd=repo) or ""
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?$", url)
    return f"{m.group(1)}__{m.group(2)}" if m else Path(repo).resolve().name


def evidence_dir(repo, issue):
    d = EVIDENCE_ROOT / repo_slug(repo) / str(issue)
    d.mkdir(parents=True, exist_ok=True)
    return d


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def walk(repo, exts):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if Path(f).suffix in exts:
                yield Path(root) / f


def is_test(rel):
    return bool(re.search(r"(^|/)(tests?|__tests__|spec)(/|$)|(^|/)test_|_test\.|\.test\.|\.spec\.", rel))


def module_of(rel):
    parts = rel.split("/")
    return "/".join(parts[:2]) if len(parts) > 2 else parts[0]


# ---------- baseline ----------

def cmd_baseline(a):
    repo = a.repo
    eco = {}
    if (Path(repo) / "package.json").exists():
        pm = next((n for f, n in [("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
                                  ("package-lock.json", "npm")] if (Path(repo) / f).exists()), None)
        eco["node"] = {"version": sh(["node", "--version"]), "package_manager": pm}
    py_markers = ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"]
    found = [m for m in py_markers if (Path(repo) / m).exists()]
    if found:
        eco["python"] = {"version": sh([sys.executable, "--version"]), "markers": found}
    rec = {
        "measured_at": now(),
        "repo": repo_slug(repo),
        "branch": a.branch,
        "commit": sh(["git", "rev-parse", f"origin/{a.branch}"], cwd=repo)
                  or sh(["git", "rev-parse", a.branch], cwd=repo),
        "os": f"{platform.system()} {platform.release()} {platform.machine()}",
        "ecosystems": eco or "unsupported (v1 supports Node and Python)",
    }
    d = evidence_dir(repo, a.issue)
    (d / "baseline.json").write_text(json.dumps(rec, indent=2))
    rec["evidence_dir"] = str(d)
    emit(rec)


# ---------- workspace ----------

def cmd_workspace(a):
    repo = a.repo
    d = evidence_dir(repo, a.issue)
    wt = d / "worktree"
    if wt.exists():
        emit({"worktree": str(wt), "reused": True, "head": sh(["git", "rev-parse", "HEAD"], cwd=wt)})
        return
    sh(["git", "fetch", "origin", a.branch], cwd=repo)
    ref = f"origin/{a.branch}" if sh(["git", "rev-parse", f"origin/{a.branch}"], cwd=repo) else a.branch
    out = subprocess.run(["git", "worktree", "add", "--detach", str(wt), ref],
                         cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        emit({"error": out.stderr.strip()})
        sys.exit(1)
    emit({"worktree": str(wt), "reused": False, "ref": ref, "head": sh(["git", "rev-parse", "HEAD"], cwd=wt)})


# ---------- run ----------

def cmd_run(a):
    if not a.cmd:
        sys.exit("run: give the command after --")
    cmd = a.cmd[1:] if a.cmd[0] == "--" else a.cmd
    d = evidence_dir(a.repo, a.issue) / "runs"
    d.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = d / f"{stamp}-{re.sub(r'[^A-Za-z0-9_.-]', '_', a.label)}"
    start = time.time()
    timed_out = False
    try:
        p = subprocess.run(cmd, cwd=a.cwd, capture_output=True, text=True, timeout=a.timeout)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        timed_out, code = True, None
        out = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
    except OSError as e:
        code, out, err = None, "", str(e)
    Path(f"{base}.out").write_text(out)
    Path(f"{base}.err").write_text(err)
    rec = {"label": a.label, "cmd": cmd, "cwd": a.cwd, "exit_code": code, "timed_out": timed_out,
           "duration_s": round(time.time() - start, 2), "at": now(),
           "stdout": f"{base}.out", "stderr": f"{base}.err"}
    Path(f"{base}.json").write_text(json.dumps(rec, indent=2))
    with open(d.parent / "runs.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    rec["record"] = f"{base}.json"
    rec["stdout_tail"] = out.splitlines()[-TAIL_LINES:]
    rec["stderr_tail"] = err.splitlines()[-TAIL_LINES:]
    emit(rec)


# ---------- classify ----------

ENV_PATTERNS = [
    r"command not found", r"No such file or directory", r"ModuleNotFoundError", r"No module named",
    r"Cannot find module", r"ERR_MODULE_NOT_FOUND", r"ECONNREFUSED", r"ENOTFOUND", r"EACCES",
    r"[Pp]ermission denied", r"npm ERR! code E", r"Could not find a version that satisfies",
    r"error: externally-managed-environment", r"unsupported engine", r"ENOENT",
]
FAIL_PATTERNS = [
    r"AssertionError", r"\bFAILED\b", r"\bFAIL\b", r"Expected.*(Received|got)", r"assert ",
    r"\d+ failed", r"not ok \d+", r"Traceback \(most recent call last\)", r"Error:",
]


def cmd_classify(a):
    rec = json.loads(Path(a.record).read_text())
    text = Path(rec["stdout"]).read_text() + "\n" + Path(rec["stderr"]).read_text()
    lines = text.splitlines()

    def hits(patterns):
        return [l.strip() for l in lines if any(re.search(p, l) for p in patterns)][:10]

    env, fail = hits(ENV_PATTERNS), hits(FAIL_PATTERNS)
    if rec.get("timed_out"):
        cat = "timeout"
    elif rec.get("exit_code") == 0:
        cat = "passed"
    elif env:
        cat = "environment"
    elif fail:
        cat = "target-failure"
    else:
        cat = "unknown"
    emit({"record": a.record, "category": cat, "environment_lines": env, "failure_lines": fail,
          "note": "Heuristic. Confirm the category before treating it as a reproduced bug."})


# ---------- context ----------

def codeowners(repo):
    for p in ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]:
        f = Path(repo) / p
        if f.exists():
            rules = []
            for line in f.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    rules.append((parts[0], parts[1:]))
            return rules
    return []


def owners_for(rel, rules):
    match = []
    for pat, owners in rules:
        p = pat.lstrip("/")
        if p.endswith("/"):
            p += "**"
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p + "/**") or rel.startswith(p.rstrip("*")):
            match = owners  # last match wins
    return match


def cmd_context(a):
    repo = a.repo
    rules = codeowners(repo)
    all_files = [str(p.relative_to(repo)) for p in walk(repo, PY_EXT | JS_EXT)]
    result = []
    for rel in a.paths:
        if not rel.strip():
            continue
        stem = Path(rel).stem
        log = sh(["git", "log", "-n", "10", "--format=%h|%ad|%an|%s", "--date=short", "--", rel], cwd=repo)
        entry = {
            "path": rel,
            "exists": (Path(repo) / rel).exists(),
            "recent_commits": [dict(zip(["sha", "date", "author", "subject"], l.split("|", 3)))
                               for l in (log or "").splitlines()],
            "codeowners": owners_for(rel, rules),
            "related_tests": [f for f in all_files if is_test(f) and stem in Path(f).name][:20],
        }
        if a.lines:
            blame = sh(["git", "blame", "--line-porcelain", "-L", a.lines, "--", rel], cwd=repo) or ""
            authors = re.findall(r"^author (.+)$", blame, re.M)
            times = [int(t) for t in re.findall(r"^author-time (\d+)$", blame, re.M)]
            entry["blame"] = {"lines": a.lines, "authors": sorted(set(authors)),
                              "latest": datetime.fromtimestamp(max(times), timezone.utc).date().isoformat()
                              if times else None}
        result.append(entry)
    emit(result)


# ---------- impact (internal) ----------

def py_sites(path, rel, symbol):
    try:
        src = path.read_text(errors="replace")
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return [], False
    lines = src.splitlines()
    found, defines = set(), False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
            defines = True
        elif isinstance(node, ast.Name) and node.id == symbol:
            found.add(node.lineno)
        elif isinstance(node, ast.Attribute) and node.attr == symbol:
            found.add(node.lineno)
        elif isinstance(node, ast.ImportFrom) and any(n.name == symbol for n in node.names):
            found.add(node.lineno)
    return [(n, lines[n - 1].strip()) for n in sorted(found)], defines


def js_sites(path, symbol):
    src = path.read_text(errors="replace")
    pat = re.compile(rf"\b{re.escape(symbol)}\b")
    define = re.compile(rf"(function\s+{re.escape(symbol)}\b|(const|let|var|class)\s+{re.escape(symbol)}\b)")
    sites, defines = [], False
    for i, line in enumerate(src.splitlines(), 1):
        if pat.search(line):
            if define.search(line):
                defines = True
            sites.append((i, line.strip()))
    return sites, defines


def exported(path, symbol):
    src = path.read_text(errors="replace")
    s = re.escape(symbol)
    if path.suffix in PY_EXT:
        m = re.search(r"__all__\s*=\s*[\[(]([^\])]*)[\])]", src, re.S)
        if m:
            return bool(re.search(rf"['\"]{s}['\"]", m.group(1)))
        return not symbol.startswith("_")
    return bool(re.search(rf"export\s+(default\s+)?(async\s+)?(function|const|let|var|class)\s+{s}\b", src)
                or re.search(rf"export\s*\{{[^}}]*\b{s}\b", src)
                or re.search(rf"(module\.)?exports\.{s}\b", src)
                or re.search(rf"module\.exports\s*=\s*\{{[^}}]*\b{s}\b", src, re.S))


def cmd_impact(a):
    repo = Path(a.repo)
    sites, def_files = [], []
    for path in walk(repo, PY_EXT | JS_EXT):
        rel = str(path.relative_to(repo))
        if path.suffix in PY_EXT:
            found, defines = py_sites(path, rel, a.symbol)
        else:
            found, defines = js_sites(path, a.symbol)
        if defines:
            def_files.append(path)
        for line, text in found:
            sites.append({"file": rel, "line": line, "text": text[:200],
                          "in_tests": is_test(rel), "module": module_of(rel)})
    by_module = {}
    for s in sites:
        by_module[s["module"]] = by_module.get(s["module"], 0) + 1
    defined_in = [str(p.relative_to(repo)) for p in def_files]
    emit({
        "symbol": a.symbol,
        "defined_in": defined_in,
        "exported": any(exported(p, a.symbol) for p in def_files) if def_files else None,
        "total_sites": len(sites),
        "in_tests": sum(s["in_tests"] for s in sites),
        "by_module": dict(sorted(by_module.items(), key=lambda kv: -kv[1])),
        "sites": sites[:MAX_SITES],
        "truncated": len(sites) > MAX_SITES,
        "note": "Static scan: a lower bound. Misses dynamic calls, reflection, string imports, "
                "plugin or config-driven calls. Name matches can include unrelated symbols.",
    })


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd_name", required=True)

    s = sub.add_parser("baseline"); s.add_argument("--repo", required=True)
    s.add_argument("--branch", required=True); s.add_argument("--issue", required=True)
    s.set_defaults(fn=cmd_baseline)

    s = sub.add_parser("workspace"); s.add_argument("--repo", required=True)
    s.add_argument("--branch", required=True); s.add_argument("--issue", required=True)
    s.set_defaults(fn=cmd_workspace)

    s = sub.add_parser("run"); s.add_argument("--repo", required=True)
    s.add_argument("--issue", required=True); s.add_argument("--label", required=True)
    s.add_argument("--cwd", required=True); s.add_argument("--timeout", type=int, default=600)
    s.add_argument("cmd", nargs=argparse.REMAINDER); s.set_defaults(fn=cmd_run)

    s = sub.add_parser("classify"); s.add_argument("--record", required=True)
    s.set_defaults(fn=cmd_classify)

    s = sub.add_parser("context"); s.add_argument("--repo", required=True)
    s.add_argument("--paths", nargs="+", required=True); s.add_argument("--lines")
    s.set_defaults(fn=cmd_context)

    s = sub.add_parser("impact"); s.add_argument("--repo", required=True)
    s.add_argument("--symbol", required=True); s.set_defaults(fn=cmd_impact)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
