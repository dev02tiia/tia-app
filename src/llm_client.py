import json
from typing import TYPE_CHECKING

from src.config import GROQ_API_KEY, GROQ_MODEL, LLM_PROVIDER

if TYPE_CHECKING:
    from groq import Groq

_groq_client: "Groq | None" = None


def _get_groq_client() -> "Groq":
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


_MOCK_RESPONSE = json.dumps({
    "enunciado": "[MOCK] Advogado X praticou ato vedado pelo Estatuto da OAB. Qual a penalidade cabível?",
    "alternativas": {
        "A": "Advertência",
        "B": "Censura",
        "C": "Suspensão",
        "D": "Exclusão",
    },
    "gabarito": "B",
    "validacao": {"aprovada": True, "motivo": "[MOCK] Questão válida."},
    "explicacao": "[MOCK] A alternativa correta é B conforme o art. 35 do Estatuto da OAB.",
}, ensure_ascii=False, indent=2)


def generate_text(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """Call the configured LLM provider and return the response as a string."""
    if LLM_PROVIDER == "mock":
        return _MOCK_RESPONSE

    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
