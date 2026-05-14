import json
import re
import sys
from datetime import datetime
from pathlib import Path

# allow `python src/run_pipeline.py` without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from src.config import CHUNKS_DIR, FINAL_DIR, VALIDATED_DIR
from src.explain_question import explain_question
from src.generate_question import generate_question
from src.validate_question import validate_question

app = typer.Typer(add_completion=False)
console = Console()

MAX_CONTEXT_CHARS = 5000  # safe ceiling for llama-3.1-8b-instant context window


# ── Chunk loading & selection ──────────────────────────────────────────────────

def _load_all_chunks(chunks_dir: Path) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(chunks_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        chunks.extend(data)
    return chunks


def _score_chunk(chunk: dict, topic_words: set[str]) -> int:
    text_lower = chunk["text"].lower()
    return sum(1 for word in topic_words if word in text_lower)


def _select_chunks(all_chunks: list[dict], topic: str, max_chunks: int) -> list[dict]:
    topic_words = set(w for w in topic.lower().split() if len(w) > 2)
    ranked = sorted(all_chunks, key=lambda c: _score_chunk(c, topic_words), reverse=True)
    return ranked[:max_chunks]


def _build_context(chunks: list[dict]) -> str:
    parts: list[str] = []
    total = 0
    for chunk in chunks:
        text = chunk["text"].strip()
        if total + len(text) > MAX_CONTEXT_CHARS:
            break
        parts.append(text)
        total += len(text)
    return "\n\n---\n\n".join(parts)


# ── Output persistence ─────────────────────────────────────────────────────────

def _safe_filename(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{slug}.json"


def _save(dest_dir: Path, topic: str, source_ids: list[str], payload: dict) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_file = dest_dir / _safe_filename(topic)
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_file


# ── Pipeline ───────────────────────────────────────────────────────────────────

@app.command()
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="Tema da questão a gerar"),
    max_chunks: int = typer.Option(3, "--max-chunks", help="Número máximo de chunks de contexto"),
    chunks_dir: Path = typer.Option(None, "--chunks-dir", help="Diretório de chunks (padrão: data/output/chunks)"),
) -> None:
    chunks_dir = chunks_dir or CHUNKS_DIR

    console.print(Rule("[bold]Pipeline OAB[/bold]"))

    # 1. Load chunks
    console.print(f"[dim]Carregando chunks de {chunks_dir}...[/dim]")
    all_chunks = _load_all_chunks(chunks_dir)
    if not all_chunks:
        console.print(f"[red]Nenhum chunk encontrado em {chunks_dir}. Rode extract e chunk primeiro.[/red]")
        raise typer.Exit(1)
    console.print(f"  {len(all_chunks)} chunks carregados.")

    # 2. Select relevant chunks
    selected = _select_chunks(all_chunks, topic, max_chunks)
    source_ids = [c["id"] for c in selected]
    console.print(f"  Chunks selecionados: {source_ids}")

    legal_context = _build_context(selected)

    # 3. Generate
    console.print(f"\n[bold cyan]1/3 Gerando questao:[/bold cyan] {topic}")
    try:
        question = generate_question(topic, legal_context)
    except Exception as exc:
        console.print(f"[red]Erro na geracao: {exc}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]{question.get('statement', '')}[/bold]\n\n"
        + "\n".join(f"  {k}) {v}" for k, v in question.get("options", {}).items())
        + f"\n\n[green]Gabarito: {question.get('correct_option')}[/green]",
        title="Questao gerada",
        expand=False,
    ))

    # 4. Validate
    console.print("\n[bold cyan]2/3 Validando...[/bold cyan]")
    try:
        validation = validate_question(question, legal_context)
    except Exception as exc:
        console.print(f"[red]Erro na validacao: {exc}[/red]")
        raise typer.Exit(1)

    approved: bool = validation.get("approved", False)
    confidence: float = validation.get("confidence", 0.0)
    issues: list[str] = validation.get("critical_issues", validation.get("issues", []))
    suggestions: list[str] = validation.get("suggestions", [])

    status_color = "green" if approved else "red"
    status_label = "APROVADA" if approved else "REPROVADA"
    console.print(f"  Status: [{status_color}]{status_label}[/{status_color}]  "
                  f"| Confianca: {confidence:.0%}")
    if issues:
        console.print("  Erros criticos:")
        for issue in issues:
            console.print(f"    [red]- {issue}[/red]")
    if suggestions:
        console.print("  Sugestoes de melhoria:")
        for s in suggestions:
            console.print(f"    [yellow]- {s}[/yellow]")

    # 5. Branch on approval
    if not approved:
        payload = {
            "topic": topic,
            "source_chunks": source_ids,
            "question": question,
            "validation": validation,
            "generated_at": datetime.now().isoformat(),
        }
        out_file = _save(VALIDATED_DIR, topic, source_ids, payload)
        console.print(f"\n[yellow]Questao reprovada salva em:[/yellow] {out_file}")
        raise typer.Exit(0)

    # 6. Explain
    console.print("\n[bold cyan]3/3 Gerando explicacao...[/bold cyan]")
    try:
        explanation = explain_question(question, legal_context)
    except Exception as exc:
        console.print(f"[red]Erro na explicacao: {exc}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Resumo:[/bold] {explanation.get('short_explanation', '')}\n\n"
        f"[bold]Dica:[/bold] {explanation.get('memory_tip', '')}",
        title="Explicacao",
        expand=False,
    ))

    # 7. Save final
    payload = {
        "topic": topic,
        "source_chunks": source_ids,
        "question": question,
        "validation": validation,
        "explanation": explanation,
        "generated_at": datetime.now().isoformat(),
    }
    out_file = _save(FINAL_DIR, topic, source_ids, payload)
    console.print(f"\n[green]Questao final salva em:[/green] {out_file}")
    console.print(Rule())


if __name__ == "__main__":
    app()
