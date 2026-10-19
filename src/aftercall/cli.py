from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from . import config, memory, pipeline
from .llm import LLMError

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Turn a client call into a reviewed, routed action list.")
client_app = typer.Typer(help="Inspect client memory.")
app.add_typer(client_app, name="client")


def _date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise typer.BadParameter(f"expected YYYY-MM-DD, got {value!r}")


@app.command()
def run(
    transcript: Path = typer.Argument(..., exists=True, dir_okay=False, help="Transcript (.md / .txt)"),
    client: Optional[str] = typer.Option(None, "--client", "-c", help="Client slug; derived from the transcript if omitted"),
    meeting_date: Optional[str] = typer.Option(None, "--date", "--meeting-date", help="Meeting date YYYY-MM-DD (default: from header)"),
    as_of: Optional[str] = typer.Option(None, "--as-of", help="Evaluate due dates and blackouts as of YYYY-MM-DD (default: today)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Ignore cached LLM responses"),
    approve_all: bool = typer.Option(False, "--approve-all", help="Demo only: commit every verified item to client memory"),
):
    """Process a transcript. Writes runs/<date>_<client>/ and prints the report."""
    try:
        result = pipeline.run(transcript, client, _date(meeting_date), _date(as_of), use_cache=not no_cache,
                              log=lambda m: typer.echo(m, err=True))
    except (LLMError, ValueError) as e:
        typer.secho(f"error: {e}", fg="red", err=True)
        raise typer.Exit(1)
    typer.echo((result.run_dir / "report.md").read_text())
    typer.echo(f"→ outputs in {result.run_dir.relative_to(config.ROOT)}/", err=True)
    if approve_all:
        counts = pipeline.approve(result.run_dir, None)
        typer.echo(f"→ committed to memory: {counts}", err=True)
    else:
        typer.echo(f"→ nothing committed. Review, then: aftercall approve {result.run_dir.relative_to(config.ROOT)} --all", err=True)


@app.command()
def approve(
    run_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated item ids to approve"),
    all_: bool = typer.Option(False, "--all", help="Approve every verified, non-superseded item"),
):
    """Commit approved items from a run into client memory."""
    if not ids and not all_:
        raise typer.BadParameter("pass --ids or --all")
    counts = pipeline.approve(run_dir, ids.split(",") if ids else None)
    typer.echo(f"committed: {counts}")


@app.command("eval")
def eval_(
    run_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    gold: Path = typer.Option(..., "--gold", exists=True, dir_okay=False),
):
    """Score a run against a gold file: must-catch recall and trap pass/fail."""
    from . import evaluate

    ok = evaluate.run(run_dir, gold, echo=typer.echo)
    raise typer.Exit(0 if ok else 1)


@app.command()
def view(
    run_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    no_open: bool = typer.Option(False, "--no-open", help="Only regenerate the file"),
):
    """Regenerate runs/<dir>/report.html (self-contained review page) and open it."""
    import webbrowser

    from . import html_report

    out = html_report.build(run_dir)
    typer.echo(f"→ {out}")
    if not no_open:
        webbrowser.open(out.resolve().as_uri())


@client_app.command("show")
def client_show(slug: str):
    state = memory.load(slug)
    typer.echo(state.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
