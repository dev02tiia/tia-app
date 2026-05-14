import json
import re
from pathlib import Path

from rich.console import Console

console = Console()

MAX_CHUNK = 2000
LEGISLACAO_DIR = Path("data/processed/legislacao")
CHUNKS_DIR = Path("data/output/chunks")


def _split_paragraphs(text: str) -> list[str]:
    """Split text on blank lines, keeping non-empty paragraphs."""
    raw = re.split(r"\n{2,}", text)
    return [p.strip() for p in raw if p.strip()]


def _split_lines(paragraph: str) -> list[str]:
    """Fallback: split an oversized paragraph by single newlines."""
    return [ln.strip() for ln in paragraph.splitlines() if ln.strip()]


def _joined_len(parts: list[str]) -> int:
    """Exact character length of '\\n\\n'.join(parts)."""
    return sum(len(p) for p in parts) + 2 * (len(parts) - 1) if parts else 0


def chunk_text(text: str, max_size: int = MAX_CHUNK) -> list[str]:
    """
    Split *text* into chunks of at most *max_size* characters.
    Tries to preserve full paragraphs; falls back to line-level splits
    when a single paragraph exceeds the limit.
    """
    chunks: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            chunks.append("\n\n".join(current))
            current.clear()

    def would_overflow(piece: str) -> bool:
        projected = current + [piece]
        return _joined_len(projected) > max_size

    for para in _split_paragraphs(text):
        if len(para) <= max_size:
            if would_overflow(para):
                flush()
            current.append(para)
        else:
            # paragraph itself exceeds limit: flush pending, then split by line
            flush()
            for line in _split_lines(para):
                if would_overflow(line):
                    flush()
                current.append(line)

    flush()
    return chunks


def chunk_file(txt_path: Path, out_dir: Path) -> int:
    """Chunk a single .txt file and write JSON output. Returns chunk count."""
    text = txt_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{txt_path.stem}.json"

    records = [
        {
            "id": f"{txt_path.stem}_{i:04d}",
            "source_file": str(txt_path),
            "chunk_index": i,
            "text": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

    out_file.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(chunks)


def process_all(input_dir: Path, out_dir: Path) -> None:
    files = sorted(input_dir.glob("*.txt"))

    if not files:
        console.print(f"[yellow]Nenhum .txt encontrado em {input_dir}[/yellow]")
        return

    console.print(f"[bold]Processando {len(files)} arquivo(s) de {input_dir}[/bold]")

    total = 0
    for txt_path in files:
        n = chunk_file(txt_path, out_dir)
        console.print(f"[green]  ok    {txt_path.name}[/green] -> {n} chunks")
        total += n

    console.print(f"[bold]Total: {total} chunks salvos em {out_dir}[/bold]")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    process_all(root / LEGISLACAO_DIR, root / CHUNKS_DIR)
