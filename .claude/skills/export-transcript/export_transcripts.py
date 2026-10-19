#!/usr/bin/env python3
"""Export Claude Code session transcripts for a project to plain .txt files.

Usage: export_transcripts.py [project_dir] [--full]
  project_dir  defaults to the current directory
  --full       also include tool results (truncated) in the output
"""
import json
import re
import sys
from pathlib import Path

REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
RESULT_LIMIT = 2000


def clean(text):
    return REMINDER.sub("", text).strip()


def tool_summary(block):
    inp = block.get("input", {})
    detail = inp.get("description") or inp.get("command") or inp.get("file_path") or ""
    detail = str(detail).splitlines()[0][:200] if detail else ""
    return f"[tool: {block.get('name')}] {detail}".rstrip()


def result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        content = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    content = clean(str(content or ""))
    if len(content) > RESULT_LIMIT:
        content = content[:RESULT_LIMIT] + "\n... [truncated]"
    return content


def render(jsonl_path, full):
    blocks, started = [], None
    for raw in jsonl_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if entry.get("type") not in ("user", "assistant") or entry.get("isSidechain") or entry.get("isMeta"):
            continue
        started = started or entry.get("timestamp")
        role = entry["type"].upper()
        content = entry.get("message", {}).get("content")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        parts = []
        for block in content or []:
            kind = block.get("type")
            if kind == "text":
                text = clean(block.get("text", ""))
                if text:
                    parts.append(text)
            elif kind == "tool_use":
                parts.append(tool_summary(block))
            elif kind == "tool_result" and full:
                text = result_text(block)
                if text:
                    parts.append("[tool result]\n" + text)
        if not parts:
            continue
        if role == "USER" and all(p.startswith("[tool result]") for p in parts):
            role = "TOOL"
        ts = (entry.get("timestamp") or "")[:19].replace("T", " ")
        blocks.append((entry.get("uuid"), f"===== {role} ({ts}) =====\n" + "\n\n".join(parts) + "\n"))
    return started, blocks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    full = "--full" in sys.argv
    project = Path(args[0] if args else ".").resolve()
    store = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(project))
    if not store.is_dir():
        sys.exit(f"No transcripts found at {store}")
    out_dir = project / "transcripts"
    out_dir.mkdir(exist_ok=True)
    state_file = out_dir / ".export-state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    for path in sorted(store.glob("*.jsonl")):
        started, blocks = render(path, full)
        done = set(state.get(path.stem, []))
        new = [(uuid, text) for uuid, text in blocks if uuid not in done]
        if not new:
            continue
        date = (started or "unknown")[:10]
        out = out_dir / f"{date}_{path.stem}.txt"
        with out.open("a", encoding="utf-8") as f:
            if out.stat().st_size == 0:
                f.write(f"Session: {path.stem}\nStarted: {started}\n\n")
            f.write("\n".join(text for _, text in new) + "\n")
        state[path.stem] = sorted(done | {uuid for uuid, _ in new})
        print(f"{out} (+{len(new)} messages)")
    state_file.write_text(json.dumps(state, indent=1))


if __name__ == "__main__":
    main()
