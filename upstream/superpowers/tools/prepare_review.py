"""Gather the data for reviewing a Superpowers release against Anvil (design §8.1).

Clones or fetches obra/superpowers into a cache outside this repo, checks out
both tags, and writes upstream/superpowers/reviews/<date>-<new-tag>.md as a
scaffold: Release notes, Mapped changes, Unmapped changes, Verdicts.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

URL = "https://github.com/obra/superpowers"
REPO = Path(__file__).resolve().parents[3]
UPSTREAM = REPO / "upstream" / "superpowers"


def git(*args, cwd=None) -> str:
    return subprocess.run(["git", *map(str, args)], cwd=cwd, check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def default_cache() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "anvil" / "superpowers-upstream"


def fetch(cache: Path, tags: list[str]) -> Path:
    clone = cache / "repo"
    if (clone / ".git").exists():
        git("-C", clone, "fetch", "--quiet", "--tags", "--force", "origin")
    else:
        cache.mkdir(parents=True, exist_ok=True)
        git("clone", "--quiet", "--no-checkout", URL, clone)
    git("-C", clone, "worktree", "prune")
    for tag in tags:
        tree = cache / "tags" / tag
        if not tree.exists():
            git("-C", clone, "worktree", "add", "--quiet", "--detach", "-f", tree, tag)
    return clone


def build_report(clone: Path, base: str, new: str, cache: Path) -> str:
    source_map = json.loads((UPSTREAM / "source-map.json").read_text(encoding="utf-8"))
    changed = {}
    for line in git("-C", clone, "diff", "--name-status", base, new).splitlines():
        status, *paths = line.split("\t")
        changed[paths[-1]] = status[0]
        if len(paths) == 2:  # rename: count the old path as changed too
            changed[paths[0]] = status[0]
    feeds: dict[str, list[str]] = {}  # Superpowers path -> Anvil files it feeds
    for anvil_path, sources in source_map.items():
        for src in sources:
            feeds.setdefault(src, []).append(anvil_path)

    notes = [l[1:] for l in git("-C", clone, "diff", base, new, "--", "RELEASE-NOTES.md").splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    issues = sorted({int(n) for n in re.findall(r"#(\d+)", "\n".join(notes))})
    log = git("-C", clone, "log", "--oneline", "--no-decorate", f"{base}..{new}").strip()

    out = [f"# Superpowers upstream review: {base} → {new}", "",
           f"- **Date:** {date.today().isoformat()}",
           f"- **Base:** {base} (`{git('-C', clone, 'rev-list', '-n1', base).strip()}`)",
           f"- **New:** {new} (`{git('-C', clone, 'rev-list', '-n1', new).strip()}`)",
           f"- **Checkouts:** `{(cache / 'tags' / base).as_posix()}`, `{(cache / 'tags' / new).as_posix()}`",
           "- **Runbook:** [upstream/superpowers/README.md](../README.md)", "",
           "## Release notes", "",
           f"Release page: {URL}/releases/tag/{new}", ""]
    out += ["Lines added to `RELEASE-NOTES.md`:", "", "```markdown", *notes, "```", ""] if notes \
        else ["No change to `RELEASE-NOTES.md`.", ""]
    if issues:
        out += ["Linked issues: " + ", ".join(f"[#{n}]({URL}/issues/{n})" for n in issues), ""]
    out += ["Commits:", "", "```", log or "(none)", "```", "", "## Mapped changes", ""]

    hit = sorted(s for s in feeds if s in changed)
    for src in hit:
        diff = git("-C", clone, "diff", base, new, "--", src).rstrip()
        out += [f"### `{src}` ({changed[src]})", "",
                "Feeds: " + ", ".join(f"`{a}`" for a in feeds[src]), "",
                "````diff", diff, "````", ""]
    if not hit:
        out += [f"No mapped Superpowers file changed between {base} and {new}.", ""]

    out += ["## Unmapped changes", ""]
    unmapped = [f"- {st} `{p}`" for p, st in sorted(changed.items(), key=lambda kv: (kv[1] != "A", kv[0]))
                if p not in feeds]
    out += (unmapped or ["None."]) + [""]
    out += ["## Verdicts", "",
            "Categories A–G and default verdicts are in the README rubric. "
            "Stop for Saad's approval after filling this in (in AFK, only A and B are applied). "
            "Churn in `tests/`, `docs/` and other-harness files can share one grouped row.", "",
            "| Change | Category | Verdict | Reason (principle or evidence) | Anvil files |",
            "|---|---|---|---|---|", ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("new_tag", help="the Superpowers release tag to review, e.g. v7.1.0")
    ap.add_argument("--base", help="tag to compare from (default: baseline.json tag)")
    ap.add_argument("--cache", type=Path, default=default_cache(),
                    help=f"clone location, outside this repo (default: {default_cache()})")
    args = ap.parse_args(argv)
    base = args.base or json.loads((UPSTREAM / "baseline.json").read_text(encoding="utf-8"))["tag"]
    cache = args.cache.resolve()
    if cache == REPO or REPO in cache.parents:
        print(f"prepare_review: the cache must be outside the repo: {cache}", file=sys.stderr)
        return 2
    out = UPSTREAM / "reviews" / f"{date.today().isoformat()}-{args.new_tag}.md"
    if out.exists():
        print(f"prepare_review: {out} already exists; move it aside to regenerate", file=sys.stderr)
        return 1
    try:
        clone = fetch(cache, [base, args.new_tag])
        report = build_report(clone, base, args.new_tag, cache)
    except subprocess.CalledProcessError as e:
        print(f"prepare_review: git {' '.join(map(str, e.cmd[1:]))} failed:\n{e.stderr}", file=sys.stderr)
        return 1
    out.write_text(report, encoding="utf-8", newline="\n")
    print(out.relative_to(REPO).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
