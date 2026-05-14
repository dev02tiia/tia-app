# Tasks — MVP OAB IA

Este documento acompanha o progresso da parte de IA/dados do projeto TIA.

O objetivo atual é criar um pipeline local capaz de:

PDFs oficiais da OAB → extração de texto → chunks → seleção de contexto → geração de questão → validação → explicação → JSON final.

---

## 1. Status geral

### Feito

- [x] Criar estrutura inicial do projeto
- [x] Criar pastas `src/`, `docs/`, `data/`
- [x] Criar `requirements.txt`
- [x] Criar `.env.example`
- [x] Configurar `.gitignore`
- [x] Configurar uso da Groq API
- [x] Configurar modelo `llama-3.1-8b-instant`
- [x] Criar cliente LLM em `src/llm_client.py`
- [x] Criar extração de texto de PDFs
- [x] Criar chunking da legislação
- [x] Criar agente gerador de questões
- [x] Criar agente validador
- [x] Criar agente explicador
- [x] Criar pipeline orquestrador em `src/run_pipeline.py`
- [x] Testar geração de questão com o Estatuto da OAB
- [x] Testar validação automática
- [x] Salvar questões reprovadas em `data/output/validated_questions/`
- [x] Salvar questões aprovadas em `data/output/final_questions/`

---

## 2. Setup local

- [ ] Confirmar que todos do projeto conseguem rodar Python
- [ ] Criar ambiente virtual `.venv`
- [ ] Instalar dependências com `pip install -r requirements.txt`
- [ ] Criar arquivo `.env` a partir do `.env.example`
- [ ] Adicionar `GROQ_API_KEY` no `.env`
- [ ] Testar provider `mock`
- [ ] Testar provider `groq`

---

## 3. Pipeline atual

### 3.1 Extração de texto

Arquivo: `src/extract_pdf_text.py`

Responsabilidade:

- Procurar PDFs no projeto
- Ignorar `.venv`, `venv`, `data/processed` e `data/output`
- Extrair texto usando PyMuPDF
- Classificar arquivos como:
  - legislação
  - prova
  - gabarito
- Salvar `.txt` em `data/processed/`

Status:

- [x] Implementado
- [x] Testado com `lei-8906-94-site.pdf`
- [ ] Testar com todos os PDFs do 44º Exame
- [ ] Testar com todos os PDFs do 45º Exame
- [ ] Avaliar qualidade da extração dos gabaritos

---

### 3.2 Chunking

Arquivo: `src/chunk_documents.py`

Responsabilidade:

- Ler textos processados de legislação
- Quebrar documentos em chunks
- Salvar chunks em `data/output/chunks/`

Status:

- [x] Implementado
- [x] Testado com Estatuto da OAB
- [ ] Melhorar chunking preservando artigos da lei
- [ ] Adicionar metadados de artigo/parágrafo quando possível
- [ ] Avaliar tamanho ideal dos chunks

---

### 3.3 Seleção de contexto

Arquivo: `src/run_pipeline.py`

Responsabilidade:

- Receber um tema via CLI
- Buscar chunks relacionados ao tema
- Selecionar os chunks mais relevantes
- Concatenar contexto respeitando limite de caracteres

Status:

- [x] Implementado com busca simples por palavras
- [x] Testado com temas como:
  - Direitos do advogado
  - Mandato e procuração do advogado
  - Inscrição na OAB e nulidade dos atos
- [ ] Substituir busca simples por embeddings futuramente
- [ ] Criar RAG real com FAISS, Chroma ou pgvector

---

### 3.4 Geração de questões

Arquivo: `src/generate_question.py`

Responsabilidade:

- Receber tema e contexto legal
- Gerar questão objetiva da 1ª fase da OAB
- Retornar JSON estruturado

Status:

- [x] Implementado
- [x] Testado com Llama 3.1 via Groq
- [ ] Ajustar prompt para sempre usar `subject = "Ética Profissional"`
- [ ] Evitar perguntas sobre consequências não expressas na lei
- [ ] Melhorar qualidade das alternativas incorretas
- [ ] Adicionar exemplos de questões antigas como referência de estilo
- [ ] Adicionar mecanismo anti-cópia

---

### 3.5 Validação de questões

Arquivo: `src/validate_question.py`

Responsabilidade:

- Avaliar se a questão gerada é juridicamente consistente
- Verificar se há apenas uma alternativa correta
- Verificar se a resposta está sustentada na base legal
- Rejeitar questões ambíguas, inventadas ou mal formuladas

Status:

- [x] Implementado
- [x] Validador consegue reprovar questões fracas
- [x] Validador retorna `approved`, `issues`, `confidence` e `comment`
- [ ] Ajustar para aprovar questões boas com pequenas sugestões
- [ ] Adicionar campo `suggestions`
- [ ] Separar problemas críticos de melhorias de redação
- [ ] Criar critérios objetivos de aprovação/reprovação

---

### 3.6 Explicação didática

Arquivo: `src/explain_question.py`

Responsabilidade:

- Gerar explicação para o aluno
- Explicar por que a alternativa correta está certa
- Explicar por que as alternativas erradas estão erradas
- Sugerir tópico de revisão
- Criar dica rápida de memorização

Status:

- [x] Implementado
- [ ] Testar com questões aprovadas
- [ ] Padronizar formato da explicação
- [ ] Validar se as explicações não inventam fundamento

---

## 4. Qualidade e avaliação

### Testes manuais necessários

- [ ] Rodar pipeline com 10 temas diferentes de Ética Profissional
- [ ] Medir quantas questões foram aprovadas
- [ ] Medir quantas questões foram reprovadas
- [ ] Ler manualmente as questões aprovadas
- [ ] Identificar principais motivos de reprovação
- [ ] Ajustar prompts com base nos erros

### Métricas iniciais

Criar uma planilha ou JSON com:

- Tema
- Questão aprovada?
- Motivo da reprovação
- Confiança do validador
- Houve alucinação?
- Referência legal correta?
- Questão útil para aluno?

---

## 5. Próximas melhorias técnicas

### Curto prazo

- [ ] Melhorar prompts do gerador
- [ ] Melhorar prompts do validador
- [ ] Melhorar prompts do explicador
- [ ] Adicionar campo `suggestions` na validação
- [ ] Criar `docs/pipeline.md`
- [ ] Criar `docs/architecture.md`
- [ ] Criar `docs/prompts.md`
- [ ] Criar `docs/data_sources.md`

### Médio prazo

- [ ] Extrair questões oficiais das provas antigas
- [ ] Associar gabaritos oficiais às questões
- [ ] Criar base estruturada de questões oficiais
- [ ] Classificar questões por matéria, tema e subtópico
- [ ] Usar questões antigas como exemplos de estilo
- [ ] Implementar busca semântica com embeddings
- [ ] Criar API com FastAPI para integração com app

### Futuro

- [ ] Criar banco PostgreSQL/Supabase
- [ ] Criar tabelas para documentos, chunks, questões oficiais e questões geradas
- [ ] Implementar RAG real
- [ ] Criar tutor IA para dúvidas do aluno
- [ ] Criar relatório de pontos fracos
- [ ] Avaliar fine-tuning após montar dataset revisado
- [ ] Expandir para 2ª fase da OAB