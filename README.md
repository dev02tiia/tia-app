# tia-app — MVP OAB IA

Plataforma de estudos com IA para preparação em provas e concursos.

## O que faz

Pipeline que transforma PDFs jurídicos (provas da OAB, legislação) em questões de múltipla escolha comentadas, usando LLMs via Groq.

```
PDF → extração de texto → chunks → geração de questão → validação → explicação
```

## Estrutura

```
tia-app/
├── src/
│   ├── config.py              # Variáveis de ambiente e constantes
│   ├── llm_client.py          # Cliente Groq
│   ├── extract_pdf_text.py    # Extração de texto de PDFs
│   ├── chunk_documents.py     # Divisão em chunks
│   ├── generate_question.py   # Agente gerador de questões
│   ├── validate_question.py   # Agente validador
│   ├── explain_question.py    # Agente explicador
│   └── run_pipeline.py        # CLI orquestradora
├── data/
│   ├── processed/             # Textos extraídos dos PDFs
│   └── output/                # Questões geradas em cada etapa
├── docs/
│   ├── tasks.md               # Checklist do projeto
│   └── agents.md              # Descrição dos agentes LLM
├── 44-exame/                  # PDFs do 44º Exame OAB
├── 45-exame/                  # PDFs do 45º Exame OAB
├── lei-8906-94-site.pdf       # Estatuto da OAB
├── .env.example
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

cp .env.example .env
# edite .env e adicione sua GROQ_API_KEY
```

## Uso

```bash
python -m src.run_pipeline caminho/para/arquivo.pdf
```

## Docs

- [Checklist de tarefas](docs/tasks.md)
- [Descrição dos agentes](docs/agents.md)
