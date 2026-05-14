# Agentes — MVP OAB IA

## Agente Gerador de Questões (`generate_question`)

**Responsabilidade:** Recebe um chunk de texto jurídico e produz uma questão de múltipla escolha no estilo OAB (enunciado + 4 alternativas + gabarito).

**Entrada:** Trecho de texto (chunk) extraído de legislação ou prova anterior.

**Saída:**
```json
{
  "enunciado": "...",
  "alternativas": { "A": "...", "B": "...", "C": "...", "D": "..." },
  "gabarito": "A"
}
```

**Prompt base:** Instruir o modelo a agir como elaborador de provas da OAB, mantendo linguagem técnica-jurídica e dificuldade compatível com o exame.

---

## Agente Validador (`validate_question`)

**Responsabilidade:** Analisa uma questão gerada e verifica se ela está juridicamente correta, bem formulada, sem ambiguidade e com gabarito inequívoco.

**Entrada:** Questão gerada pelo agente anterior (dict com enunciado, alternativas e gabarito).

**Saída:** Mesmo dict enriquecido com:
```json
{
  "validacao": {
    "aprovada": true,
    "motivo": "Questão clara e gabarito correto conforme o Estatuto da OAB."
  }
}
```

**Prompt base:** Instruir o modelo a agir como revisor jurídico sênior, rejeitando questões com erros de direito, gabarito duvidoso ou enunciado confuso.

---

## Agente Explicador (`explain_question`)

**Responsabilidade:** Gera uma explicação didática da resposta correta, com base no texto legal ou doutrinário relevante.

**Entrada:** Questão validada (dict completo).

**Saída:** Mesmo dict enriquecido com:
```json
{
  "explicacao": "A alternativa correta é A porque o art. X da Lei Y estabelece que..."
}
```

**Prompt base:** Instruir o modelo a agir como professor de curso preparatório OAB, explicando o raciocínio jurídico de forma clara e referenciando a legislação aplicável.
