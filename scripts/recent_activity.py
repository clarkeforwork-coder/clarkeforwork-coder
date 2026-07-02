"""Render the account's recent public GitHub activity into README.md.

Fills the block between <!--START_SECTION:activity--> and <!--END_SECTION:activity-->.
Covers pushes / repo & branch creation / stars / forks / PRs / issues / releases —
unlike the issue-only actions. No emojis (keeps the terminal aesthetic).

Run locally:  GITHUB_TOKEN=ghp_... python scripts/recent_activity.py
In CI it uses the workflow's GITHUB_TOKEN automatically.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

USER = "clarkeforwork-coder"
MAX_LINES = 6
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!--START_SECTION:activity-->", "<!--END_SECTION:activity-->"


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def link(full_name):
    return f"[{full_name}](https://github.com/{full_name})"


def describe(ev):
    t = ev["type"]
    repo = ev.get("repo", {}).get("name", "")
    p = ev.get("payload", {})
    if t == "PushEvent":
        n = p.get("size") or p.get("distinct_size") or len(p.get("commits") or [])
        return f"Pushed {n} commits to {link(repo)}" if n else f"Pushed to {link(repo)}"
    if t == "CreateEvent":
        rt = p.get("ref_type", "")
        if rt == "repository":
            return f"Created repository {link(repo)}"
        if rt in ("branch", "tag"):
            return f"Created {rt} `{p.get('ref')}` in {link(repo)}"
    if t == "WatchEvent":
        return f"Starred {link(repo)}"
    if t == "ForkEvent":
        return f"Forked {link(repo)}"
    if t == "PullRequestEvent":
        return f"{p.get('action', '').capitalize()} PR #{p.get('number')} in {link(repo)}"
    if t == "IssuesEvent":
        return f"{p.get('action', '').capitalize()} issue #{p.get('issue', {}).get('number')} in {link(repo)}"
    if t == "IssueCommentEvent":
        return f"Commented on #{p.get('issue', {}).get('number')} in {link(repo)}"
    if t == "ReleaseEvent":
        return f"Released {p.get('release', {}).get('tag_name')} in {link(repo)}"
    if t == "PublicEvent":
        return f"Open-sourced {link(repo)}"
    return None


def main():
    events = api(f"https://api.github.com/users/{USER}/events/public?per_page=30")
    lines, seen = [], set()
    for ev in events:
        desc = describe(ev)
        if not desc or desc in seen:
            continue
        seen.add(desc)
        lines.append(f"{len(lines) + 1}. {desc}")
        if len(lines) >= MAX_LINES:
            break

    block = "\n".join(lines) if lines else "_No recent public activity._"
    text = README.read_text(encoding="utf-8")
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n{block}\n{END}",
        text,
        flags=re.DOTALL,
    )
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README updated:\n" + block)
        return 0
    print("No change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
