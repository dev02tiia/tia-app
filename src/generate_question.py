import json
import re

from src.config import MAX_TOKENS, TEMPERATURE_GENERATE
from src.llm_client import generate_text

_SCHEMA = """{
  "subject": "área do direito (ex: Ética e Estatuto da OAB)",
  "topic": "tópico específico da questão",
  "statement": "enunciado completo, com situação-problema quando possível",
  "options": {
    "A": "texto da alternativa A",
    "B": "texto da alternativa B",
    "C": "texto da alternativa C",
    "D": "texto da alternativa D"
  },
  "correct_option": "A",
  "explanation": "por que a alternativa correta está certa, citando o dispositivo legal",
  "references": ["Lei n. 8.906/94, art. X", "..."]
}"""


def _build_examples_block(examples: list[dict] | None) -> str:
    if not examples:
        return ""
    lines = ["Exemplos de questões no estilo desejado:"]
    for ex in examples[:2]:
        lines.append(json.dumps(ex, ensure_ascii=False, indent=2))
    return "\n".join(lines) + "\n\n"


def _parse_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text.strip())


def generate_question(
    topic: str,
    legal_context: str,
    examples: list[dict] | None = None,
) -> dict:
    """
    Generate an OAB-style multiple-choice question from a legal context chunk.

    Returns a dict with keys:
        subject, topic, statement, options (A-D), correct_option,
        explanation, references
    """
    examples_block = _build_examples_block(examples)

    prompt = f"""Você é um elaborador expert de questões para o Exame da OAB (Ordem dos Advogados do Brasil).

Com base no contexto jurídico abaixo, crie UMA questão de múltipla escolha no estilo OAB.

Regras obrigatórias:
- O enunciado deve apresentar uma situação-problema concreta, não apenas perguntar a letra da lei.
- Apenas uma alternativa deve estar correta; as demais devem ser plausíveis mas incorretas.
- Não invente dispositivos. Baseie-se somente no contexto fornecido.
- As alternativas devem ter tamanho semelhante para não denunciar o gabarito.

Tópico solicitado: {topic}

{examples_block}Contexto jurídico:
{legal_context}

Retorne SOMENTE o JSON abaixo, sem texto adicional, sem markdown, sem explicações fora do JSON:
{_SCHEMA}"""

    raw = generate_text(prompt, temperature=TEMPERATURE_GENERATE, max_tokens=MAX_TOKENS)
    return _parse_json(raw)
