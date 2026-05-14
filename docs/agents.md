# Agents — MVP OAB IA

Este documento descreve os agentes de IA do pipeline de geração, validação e explicação de questões da OAB.

O objetivo dos agentes é transformar documentos oficiais, especialmente legislação da OAB, em questões objetivas da 1ª fase com validação e explicação didática.

Fluxo atual:

1. Selecionar contexto legal.
2. Gerar questão.
3. Validar questão.
4. Gerar explicação.
5. Salvar resultado em JSON.

---

## 1. Agente Gerador de Questões

Arquivo: `src/generate_question.py`

### Responsabilidade

Gerar uma questão objetiva da 1ª fase da OAB com base em:

- tema escolhido;
- trechos de legislação;
- futuramente, exemplos de questões antigas.

### Entrada

Campos esperados:

- `topic`: tema da questão.
- `legal_context`: trechos legais usados como base.
- `examples`: exemplos opcionais de questões antigas.

Exemplo de entrada:

```json
{
  "topic": "Direitos do advogado",
  "legal_context": "Trechos do Estatuto da OAB...",
  "examples": []
}
```

### Saída esperada

Campos esperados:

- `subject`
- `topic`
- `statement`
- `options`
- `correct_option`
- `explanation`
- `references`

Exemplo de saída:

```json
{
  "subject": "Ética Profissional",
  "topic": "Direitos do advogado",
  "statement": "Enunciado da questão...",
  "options": {
    "A": "Alternativa A",
    "B": "Alternativa B",
    "C": "Alternativa C",
    "D": "Alternativa D"
  },
  "correct_option": "C",
  "explanation": "Explicação inicial da resposta correta.",
  "references": [
    "Lei nº 8.906/1994, art. 7º"
  ]
}
```

### Regras do agente

- Retornar somente JSON válido.
- Gerar apenas uma alternativa correta.
- Usar somente a base legal fornecida.
- Não inventar artigos, regras ou consequências.
- Não copiar questões antigas.
- Usar linguagem compatível com a 1ª fase da OAB.
- Preencher `subject` como `Ética Profissional`.

### Problemas observados

- Às vezes preenche `subject` com texto genérico.
- Às vezes cria consequências jurídicas não expressas na base legal.
- Às vezes gera alternativas incorretas pouco plausíveis.

### Melhorias planejadas

- Forçar `subject = "Ética Profissional"`.
- Preferir perguntas sobre conceitos, prazos, requisitos, permissões e vedações.
- Evitar perguntas sobre consequências não expressas.
- Adicionar exemplos reais de questões antigas como referência de estilo.
- Adicionar verificação anti-cópia.

---

## 2. Agente Validador

Arquivo: `src/validate_question.py`

### Responsabilidade

Avaliar se a questão gerada está juridicamente correta, clara e útil para estudo.

### Entrada

Campos esperados:

- `question_json`: questão gerada pelo agente anterior.
- `legal_context`: trechos legais usados como base.

Exemplo de entrada:

```json
{
  "question_json": {},
  "legal_context": "Trechos usados como base..."
}
```

### Saída esperada

Campos esperados:

- `approved`
- `issues`
- `suggestions`
- `confidence`
- `comment`

Exemplo de saída:

```json
{
  "approved": true,
  "issues": [],
  "suggestions": [],
  "confidence": 0.95,
  "comment": "Questão aprovada com base no art. X."
}
```

### Critérios de aprovação

A questão deve ser aprovada quando:

- a resposta correta está sustentada na legislação;
- há apenas uma alternativa correta;
- não há fundamento inventado;
- o enunciado é respondível;
- as alternativas erradas são incorretas à luz da base.

### Critérios de reprovação

A questão deve ser reprovada quando:

- o gabarito está errado;
- há mais de uma alternativa correta;
- não há base legal suficiente;
- a questão inventa artigo, regra ou consequência;
- o enunciado é impossível ou muito ambíguo;
- a questão não corresponde ao tema pedido.

### Critérios para aprovar com sugestões

A questão pode ser aprovada com sugestões quando:

- o enunciado poderia ser mais claro;
- as alternativas poderiam ser mais plausíveis;
- a referência poderia ser melhor formatada;
- a redação poderia ser mais objetiva.

### Problemas observados

O validador às vezes reprova uma questão mesmo reconhecendo que:

- o gabarito está correto;
- há uma única resposta correta;
- a questão está baseada na legislação.

### Melhorias planejadas

- Separar `issues` críticos de `suggestions`.
- Aprovar questões juridicamente corretas mesmo com pequenas melhorias de redação.
- Criar campo `severity` futuramente.
- Criar logs dos motivos de reprovação.

---

## 3. Agente Explicador

Arquivo: `src/explain_question.py`

### Responsabilidade

Gerar uma explicação didática para o aluno após a questão ser aprovada.

### Entrada

Campos esperados:

- `question_json`: questão aprovada.
- `legal_context`: trechos legais usados como base.

Exemplo de entrada:

```json
{
  "question_json": {},
  "legal_context": "Trechos da legislação usados como base..."
}
```

### Saída esperada

Campos esperados:

- `short_explanation`
- `why_correct`
- `why_wrong`
- `review_topic`
- `memory_tip`

Exemplo de saída:

```json
{
  "short_explanation": "Resumo curto da resposta.",
  "why_correct": "Por que a alternativa correta está certa.",
  "why_wrong": {
    "A": "Por que A está errada.",
    "B": "Por que B está errada.",
    "C": "Por que C está errada.",
    "D": "Por que D está errada."
  },
  "review_topic": "Tema para revisar",
  "memory_tip": "Dica rápida de memorização"
}
```

### Regras do agente

- Usar linguagem simples.
- Explicar como professor de curso preparatório.
- Usar somente a base legal fornecida.
- Não inventar artigo, exceção ou regra.
- Indicar um tema de revisão.
- Gerar uma dica curta e útil.

### Melhorias planejadas

- Padronizar tom da explicação.
- Criar explicações mais curtas para interface mobile.
- Criar explicação detalhada opcional.
- Validar se a explicação cita corretamente a base legal.

---

## 4. Agente Seletor de Contexto

Arquivo atual: `src/run_pipeline.py`

### Responsabilidade

Selecionar os chunks de legislação mais relevantes para o tema informado.

### Entrada

Campos esperados:

- `topic`: tema solicitado pelo usuário.
- `chunks`: lista de chunks disponíveis.

Exemplo de entrada:

```json
{
  "topic": "Mandato e procuração do advogado",
  "chunks": []
}
```

### Saída esperada

Lista com os IDs dos chunks selecionados.

Exemplo:

```json
[
  "lei-8906-94-site_0002",
  "lei-8906-94-site_0016",
  "lei-8906-94-site_0017"
]
```

### Estratégia atual

A seleção é feita por pontuação simples, contando palavras do tema dentro do texto de cada chunk.

### Limitações

- Não entende sinônimos.
- Não faz busca semântica real.
- Pode selecionar chunks pouco relevantes se o tema for amplo.
- Não usa embeddings.

### Melhorias planejadas

- Implementar embeddings.
- Usar FAISS, Chroma ou pgvector.
- Salvar metadados por artigo e parágrafo.
- Criar busca híbrida: palavra-chave + semântica.

---

## 5. Agente Classificador de Questões

Status: planejado.

### Responsabilidade

Classificar questões oficiais ou geradas por:

- matéria;
- tema;
- subtópico;
- dificuldade;
- habilidade cobrada.

### Entrada

Campos esperados:

- `statement`: enunciado.
- `options`: alternativas.

Exemplo de entrada:

```json
{
  "statement": "Enunciado...",
  "options": {}
}
```

### Saída esperada

Exemplo:

```json
{
  "subject": "Ética Profissional",
  "topic": "Direitos do advogado",
  "subtopic": "Prerrogativas",
  "difficulty": "média",
  "skill": "interpretação de regra legal"
}
```

### Uso futuro

- Relatório de desempenho do aluno.
- Recomendação personalizada.
- Organização das trilhas.
- Geração adaptativa de questões.

---

## 6. Agente Anti-Cópia

Status: planejado.

### Responsabilidade

Verificar se uma questão gerada está muito parecida com questão oficial antiga.

### Motivo

As provas antigas devem servir como referência de estilo, não como texto para cópia.

### Estratégias possíveis

- Similaridade textual simples.
- Comparação por embeddings.
- Verificação de enunciado e alternativas.
- Rejeição se a similaridade passar de um limite definido.

---

## 7. Agente Tutor

Status: futuro.

### Responsabilidade

Responder dúvidas do aluno com base na legislação e nas questões.

### Exemplo de pergunta

> Qual a diferença entre impedimento e incompatibilidade?

### Saída esperada

Resposta didática, curta e baseada em documentos oficiais.

### Observação

Este agente deve ser tratado como tutor educacional, não como consultor jurídico.

---

## 8. Agente Avaliador de Dataset

Status: futuro.

### Responsabilidade

Avaliar a qualidade das questões geradas e criar dados para melhoria futura.

### Métricas possíveis

- JSON válido.
- Questão aprovada.
- Gabarito correto.
- Referência correta.
- Ausência de alucinação.
- Clareza do enunciado.
- Qualidade das alternativas.
- Utilidade pedagógica.

### Uso futuro

Esse agente pode ajudar a montar dataset para fine-tuning.

---

## Observações sobre fine-tuning

Fine-tuning não é prioridade neste MVP.

Antes de fine-tuning, precisamos de:

- muitas questões geradas;
- revisão humana ou semi-humana;
- métricas de qualidade;
- exemplos bons e ruins;
- padrão consistente de entrada e saída.

O fine-tuning poderá ajudar no futuro a melhorar:

- consistência do formato;
- estilo das questões;
- qualidade das alternativas;
- aderência ao padrão OAB.

Mesmo com fine-tuning, a arquitetura ainda deve usar RAG, porque o modelo precisa consultar documentos oficiais atualizados.
