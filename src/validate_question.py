import json
import re

from src.config import MAX_TOKENS, TEMPERATURE_VALIDATE
from src.llm_client import generate_text

_SCHEMA = """{
  "approved": true,
  "issues": ["lista de problemas encontrados, vazia se aprovada"],
  "confidence": 0.95,
  "comment": "parecer geral sobre a questão"
}"""


def _parse_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text.strip())


def validate_question(question_json: dict, legal_context: str) -> dict:
    """
    Validate an OAB question for legal accuracy and clarity.

    Returns a dict with keys:
        approved (bool), issues (list[str]), confidence (float), comment (str)
    """
    question_str = json.dumps(question_json, ensure_ascii=False, indent=2)

    prompt = f"""Você é um revisor jurídico sênior especializado no Exame da OAB.

Analise a questão abaixo verificando cada critério:
1. O enunciado está claro e sem ambiguidade?
2. As alternativas incorretas são juridicamente plausíveis (não absurdas)?
3. O gabarito está correto conforme a legislação vigente?
4. Há uma única resposta inequivocamente correta?
5. A questão se baseia no contexto jurídico fornecido?

Questão a validar:
{question_str}

Contexto jurídico de referência:
{legal_context}

Retorne SOMENTE o JSON abaixo, sem texto adicional, sem markdown:
{_SCHEMA}

Notas sobre os campos:
- "approved": true somente se todos os critérios foram atendidos.
- "issues": liste cada problema encontrado como string separada; vazio se aprovada.
- "confidence": número entre 0.0 e 1.0 refletindo sua certeza sobre o gabarito.
- "comment": parecer técnico em uma ou duas frases."""

    raw = generate_text(prompt, temperature=TEMPERATURE_VALIDATE, max_tokens=MAX_TOKENS)
    return _parse_json(raw)
