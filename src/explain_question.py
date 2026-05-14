import json
import re

from src.config import MAX_TOKENS, TEMPERATURE_EXPLAIN
from src.llm_client import generate_text

_SCHEMA = """{
  "short_explanation": "resumo em 1-2 frases do conceito testado pela questão",
  "why_correct": "por que a alternativa correta está certa, com fundamento legal",
  "why_wrong": {
    "X": "por que esta alternativa está errada (substitua X pelas letras incorretas)"
  },
  "review_topic": "tópico ou artigo específico que o aluno deve revisar",
  "memory_tip": "dica mnemônica ou associação para fixar o conceito"
}"""


def _parse_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text.strip())


def explain_question(question_json: dict, legal_context: str) -> dict:
    """
    Generate a didactic explanation for an OAB question.

    Returns a dict with keys:
        short_explanation, why_correct, why_wrong (dict keyed by wrong option letters),
        review_topic, memory_tip
    """
    correct = question_json.get("correct_option", "")
    wrong_letters = [k for k in ("A", "B", "C", "D") if k != correct]
    question_str = json.dumps(question_json, ensure_ascii=False, indent=2)

    prompt = f"""Você é um professor de curso preparatório para o Exame da OAB, especialista em didática jurídica.

Com base na questão e no contexto jurídico fornecidos, produza uma explicação completa e didática.

Questão:
{question_str}

Contexto jurídico:
{legal_context}

Instruções:
- "short_explanation": explique o conceito central testado, sem mencionar as alternativas.
- "why_correct": fundamente a alternativa {correct} citando o dispositivo legal exato.
- "why_wrong": explique por que cada alternativa incorreta ({", ".join(wrong_letters)}) está errada. \
Use as letras como chaves do objeto.
- "review_topic": indique o artigo ou tópico que o candidato deve revisar se errou.
- "memory_tip": crie uma dica de memorização prática (associação, sigla, regra geral).

Retorne SOMENTE o JSON abaixo, sem texto adicional, sem markdown:
{_SCHEMA}"""

    raw = generate_text(prompt, temperature=TEMPERATURE_EXPLAIN, max_tokens=MAX_TOKENS)
    return _parse_json(raw)
