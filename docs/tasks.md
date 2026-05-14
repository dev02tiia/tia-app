# Tasks — MVP OAB IA

## Estrutura e Setup
- [x] Criar estrutura de pastas do projeto
- [x] Criar arquivos iniciais (`src/`, `docs/`, `data/`)
- [x] Definir `requirements.txt`
- [x] Configurar `.env.example`
- [ ] Instalar dependências (`pip install -r requirements.txt`)

## Pipeline Principal
- [ ] **Extração de texto** — `src/extract_pdf_text.py`
  - Extrair texto de PDFs das provas e da legislação
  - Salvar texto em `data/processed/`
- [ ] **Chunking** — `src/chunk_documents.py`
  - Dividir texto em chunks com overlap
  - Salvar chunks em `data/output/chunks/`
- [ ] **Geração de questões** — `src/generate_question.py`
  - Gerar questão de múltipla escolha no estilo OAB a partir de cada chunk
  - Salvar em `data/output/generated_questions/`
- [ ] **Validação** — `src/validate_question.py`
  - Verificar se a questão está juridicamente correta e bem formulada
  - Salvar em `data/output/validated_questions/`
- [ ] **Explicação** — `src/explain_question.py`
  - Gerar explicação didática do gabarito
  - Salvar em `data/output/final_questions/`
- [ ] **Orquestrador** — `src/run_pipeline.py`
  - Conectar todos os passos em um único comando CLI

## Qualidade
- [ ] Testar pipeline ponta-a-ponta com `lei-8906-94-site.pdf`
- [ ] Testar com provas do `44-exame/` e `45-exame/`
- [ ] Avaliar qualidade das questões geradas
- [ ] Ajustar prompts conforme necessário
