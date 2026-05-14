from pathlib import Path

import fitz  # pymupdf
from rich.console import Console

console = Console()

IGNORE_DIRS = {".venv", "venv", "data"}

LEGISLACAO_KEYWORDS = {"lei", "estatuto", "provimento", "codigo"}


def _classify(name: str) -> str:
    """Return subfolder name based on filename keywords."""
    lower = name.lower()
    if "gabarito" in lower:
        return "gabaritos"
    for kw in LEGISLACAO_KEYWORDS:
        if kw in lower:
            return "legislacao"
    if "prova" in lower:
        return "provas"
    return "provas"  # default bucket for unrecognised PDFs


def extract_text(pdf_path: str | Path) -> str:
    """Extract and return all text from a PDF file."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def find_pdfs(root: Path) -> list[Path]:
    """Walk *root* and return PDF paths, skipping ignored directories."""
    pdfs: list[Path] = []
    for path in root.rglob("*.pdf"):
        # skip any path whose parts include an ignored directory
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        pdfs.append(path)
    return sorted(pdfs)


def process_all(root: Path, processed_dir: Path) -> None:
    pdfs = find_pdfs(root)

    if not pdfs:
        console.print("[yellow]Nenhum PDF encontrado.[/yellow]")
        return

    console.print(f"[bold]Encontrados {len(pdfs)} PDF(s).[/bold]")

    for pdf_path in pdfs:
        subfolder = _classify(pdf_path.stem)
        dest_dir = processed_dir / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        # prefix with parent folder to avoid collisions (e.g. 44-exame/gabarito vs 45-exame/gabarito)
        stem = f"{pdf_path.parent.name}_{pdf_path.stem}" if pdf_path.parent != root else pdf_path.stem
        dest_file = dest_dir / f"{stem}.txt"

        if dest_file.exists():
            console.print(f"[dim]  skip  {pdf_path.name} (ja extraido)[/dim]")
            continue

        try:
            text = extract_text(pdf_path)
            dest_file.write_text(text, encoding="utf-8")
            console.print(f"[green]  ok    {pdf_path.name}[/green] -> {dest_file.relative_to(root)}")
        except Exception as exc:
            console.print(f"[red]  erro  {pdf_path.name}: {exc}[/red]")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    processed_dir = root / "data" / "processed"
    process_all(root, processed_dir)
