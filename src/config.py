import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()

if LLM_PROVIDER not in {"groq", "mock"}:
    raise ValueError(f"LLM_PROVIDER inválido: '{LLM_PROVIDER}'. Use 'groq' ou 'mock'.")

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY não definida. Adicione ao .env ou defina na variável de ambiente.")

# Per-agent temperatures read from .env with sensible defaults
TEMPERATURE_GENERATE: float = float(os.getenv("TEMPERATURE_GENERATE", "0.4"))
TEMPERATURE_VALIDATE: float = float(os.getenv("TEMPERATURE_VALIDATE", "0.1"))
TEMPERATURE_EXPLAIN: float = float(os.getenv("TEMPERATURE_EXPLAIN", "0.2"))

MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

# ── Paths ─────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = _ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

CHUNKS_DIR = OUTPUT_DIR / "chunks"
GENERATED_DIR = OUTPUT_DIR / "generated_questions"
VALIDATED_DIR = OUTPUT_DIR / "validated_questions"
FINAL_DIR = OUTPUT_DIR / "final_questions"

CHUNK_SIZE = 2000
