# LexCare AI

AI-powered Retrieval-Augmented Generation (RAG) platform for healthcare legislation, policy documents, and regulatory updates.

LexCare AI enables users to query healthcare-related regulations and policy documents using natural language while providing transparent source references and traceability.

---

## Current Status

⚠️ **Active Development**

LexCare AI is currently under active development.

The core RAG pipeline is functional and includes:

- PDF document ingestion
- Metadata extraction
- Document processing and chunking
- Embedding generation
- Chroma vector store integration
- Semantic retrieval
- Source-grounded answer generation
- FastAPI REST API
- Automated test suite

Planned enhancements include:

- Incremental document ingestion
- Automated source synchronization
- Data engineering layer (PySpark / Data Vault)
- Frontend application (Next.js)
- Advanced evaluation framework

---

## Features

### Document Ingestion

- PDF document upload
- Metadata extraction
- Structured document repository

### Document Processing

- Text cleaning
- Metadata enrichment
- Configurable chunking

### Retrieval

- Azure OpenAI embeddings
- Chroma vector database
- Similarity search
- Top-k retrieval

### Generation

- Source-grounded answer generation
- Hallucination reduction prompt
- Source attribution

### API

- `POST /api/query`
- `POST /api/documents`
- `GET /api/documents`
- `GET /api/documents/{document_id}`

---

## Architecture

```text
PDF Documents
        │
        ▼
   PDF Loader
        │
        ▼
Document Repository
        │
        ▼
Document Processing
  ├─ Metadata
  ├─ Cleaning
  └─ Chunking
        │
        ▼
 Embedding Service
        │
        ▼
 Chroma Vector Store
        │
        ▼
 Retriever Service
        │
        ▼
 Generation Service
        │
        ▼
    RAG Service
        │
        ▼
 FastAPI Endpoints
```

---

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic

### AI & Retrieval

- LangChain
- Azure OpenAI
- Chroma

### Testing

- Pytest

### Development

- Black
- Ruff
- MyPy

---

## Evaluation

Current evaluation dataset:

| Query | Expected Source |
|---------|---------|
| Was ist Pflegegrad 3? | SGB XI |
| Wer hat Anspruch auf Pflegegeld? | SGB XI |
| Wie hoch ist der Entlastungsbetrag? | SGB XI |
| Was regelt das PUEG? | PUEG |
| Welche Leistungen sind in der gesetzlichen Krankenversicherung geregelt? | SGB V |

Current retrieval evaluation:

- Hit Rate@5: 100%
- Source Attribution: Supported
- End-to-End Tests: Passing

---

## Getting Started

### Create Environment

```bash
conda env create -f environment.yml
conda activate lexcare-ai
```

### Start API

```bash
uvicorn app.main:app --reload
```

### Open API Documentation

```text
http://localhost:8000/redoc
```

---

## Project Structure

```text
app/
├── api/
├── core/
├── dependencies/
├── domain/
├── infrastructure/
├── repositories/
├── services/
└── prompts/

tests/
notebooks/
data/
```

---

## Roadmap

### Phase 1

- [x] RAG MVP
- [x] API Layer
- [x] Evaluation Framework

### Phase 2

- [ ] Incremental ingestion
- [ ] Automated source updates
- [ ] Enhanced retrieval evaluation

### Phase 3

- [ ] PySpark processing layer
- [ ] Delta Lake integration
- [ ] Data Vault modeling

### Phase 4

- [ ] Next.js frontend
- [ ] Authentication
- [ ] User document collections

---

## Disclaimer

LexCare AI is intended for educational, research, and portfolio purposes.

Generated answers should not be considered legal, medical, or professional advice. Always consult official sources and qualified professionals when making healthcare or legal decisions.