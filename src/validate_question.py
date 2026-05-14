import json
import re

from src.config import MAX_TOKENS, TEMPERATURE_VALIDATE
from src.llm_client import generate_text

_SCHEMA = """{
  "approved": true,
  "critical_issues": [],
  "suggestions": [],
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
        approved (bool), critical_issues (list[str]), suggestions (list[str]),
        confidence (float), comment (str), issues (list[str] — alias for critical_issues)
    """
    question_str = json.dumps(question_json, ensure_ascii=False, indent=2)

    prompt = f"""Você é um revisor jurídico sênior especializado no Exame da OAB.

Seu papel é APROVAR questões juridicamente corretas, não rejeitar por estilo.

REGRA PRINCIPAL: aprove a questão sempre que o gabarito estiver correto, houver uma única alternativa correta e a resposta estiver sustentada na base legal fornecida. Coloque melhorias de redação em "suggestions", NÃO em "critical_issues".

REPROVE (approved: false) SOMENTE se houver pelo menos um dos erros abaixo:
- Gabarito incorreto segundo a legislação.
- Mais de uma alternativa correta.
- Nenhuma alternativa correta.
- A resposta correta não tem sustentação na base legal fornecida.
- A questão inventa artigo, regra ou consequência que não existe na lei.
- O enunciado é impossível de responder ou completamente ambíguo.
- A questão é fora do tema jurídico.

APROVE com suggestions (approved: true) quando houver apenas melhorias de:
- Clareza do enunciado.
- Plausibilidade das alternativas incorretas.
- Objetividade da redação.
- Formatação das referências legais.

NÃO reprove por:
- Alternativas incorretas pouco criativas, desde que juridicamente incorretas.
- Enunciado um pouco longo ou indireto.
- Falta de elegância na redação.
- Referências mal formatadas.

Questão a validar:
{question_str}

Contexto jurídico de referência:
{legal_context}

Retorne SOMENTE o JSON abaixo, sem texto adicional, sem markdown:
{_SCHEMA}

Notas sobre os campos:
- "approved": true se não há erro crítico; false somente se há erro crítico listado.
- "critical_issues": lista de erros críticos que justificam reprovação; vazio se aprovada.
- "suggestions": lista de melhorias de redação ou clareza, sem afetar a aprovação.
- "confidence": número entre 0.0 e 1.0 refletindo sua certeza sobre o gabarito.
- "comment": parecer técnico em uma ou duas frases."""

    raw = generate_text(prompt, temperature=TEMPERATURE_VALIDATE, max_tokens=MAX_TOKENS)
    result = _parse_json(raw)
    # backward-compat: expose critical_issues also as "issues"
    result.setdefault("issues", result.get("critical_issues", []))
    result.setdefault("critical_issues", result.get("issues", []))
    result.setdefault("suggestions", [])
    return result
