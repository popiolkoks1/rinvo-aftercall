---
name: export-transcript
description: Export the transcripts of this project's Claude Code conversations (current and past sessions) to plain .txt files in ./transcripts/. Use when the user asks to save, copy, dump or export the conversation/transcript/chat history.
---

# Export transcripts

Run:

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/export-transcript/export_transcripts.py" "$CLAUDE_PROJECT_DIR"
```

(If `$CLAUDE_PROJECT_DIR` is empty, use the project root path instead.)

- Writes one file per session to `transcripts/<date>_<session-id>.txt`. Re-running appends only messages not exported yet (tracked in `transcripts/.export-state.json`); existing content is never overwritten.
- Includes user and assistant messages plus one-line summaries of tool calls.
- If the user wants tool outputs too, add `--full` (tool results are truncated to 2000 chars each).

Report the paths of the written files to the user.
