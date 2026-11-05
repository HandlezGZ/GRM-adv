# LexTax - Tax Document Analysis & Grounded Q&A Assistant

LexTax is a domain-specialized artificial intelligence platform designed for ingestion, structural extraction, executive summarization, and auditably grounded question-answering over Brazilian tax documents (*Autos de Infração e Imposição de Multa*, *Notificações de Lançamento*, *Pareceres/Soluções de Consulta COSIT*, *Guias DARF*, and *Certidões Fiscais*).

---

## 1. System Architecture

```text
                                  ┌─────────────────────────────┐
                                  │ React 18 Web UI (Port 8503) │
                                  └──────────────┬──────────────┘
                                                 │ HTTP / REST
                                                 
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Backend (Port 8002)                              │
│                                                                                         │
│  ┌────────────────────────┐      ┌─────────────────────────┐   ┌─────────────────────┐  │
│  │  PDF Ingestion Service │      │ Tax Extraction Service  │   │ Tax Summary Service │  │
│  │ (pypdf, page chunking, │      │ (Deterministic Patterns │   │ (Risk Assessment,   │  │
│  │   SHA-256 validation)  │      │  + LLM Schema Fallback) │   │  Deadlines Timeline)│  │
│  └───────────┬────────────┘      └────────────┬────────────┘   └──────────┬──────────┘  │
│              │                                │                           │             │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                        Grounded RAG & Retrieval Engine                            │  │
│  │     - BM25 Token Ranking over Context Chunks                                      │  │
│  │     - Mandatory Verbatim Sentence-Level Citations (Page Tracking)                 │  │
│  │     - Strict Anti-Hallucination Guardrail (Refusal on Missing Facts)              │  │
│  └───────────────────────────────────────────┬───────────────────────────────────────┘  │
└──────────────────────────────────────────────┼──────────────────────────────────────────┘
                                               │ SQLAlchemy ORM
                                               
                                  ┌─────────────────────────────┐
                                  │   SQLite Database (lextax.db) │
                                  │ TaxDocument, DocumentChunk, │
                                  │ TaxExtraction, ChatSession  │
                                  └─────────────────────────────┘
```

---

## 2. Key Capabilities & Engines

### 2.1 PDF Ingestion & Normalization (`PDFIngestionService`)
- Native extraction of text streams per page using `pypdf`.
- Form-feed partitioner and sliding-window chunking with configurable overlap (`chunk_size=800`, `chunk_overlap=150`).
- Cryptographic hash generation (`SHA-256`) to guarantee idempotency and prevent duplicate processing.
- Heuristic detection of tax document categories (`AIIM`, `NL`, `COSIT`, `DARF`, `CND`, `OUTRO`).

### 2.2 Dual-Engine Tax Extraction (`TaxExtractionService`)
- **Deterministic Pattern Engine:** High-performance, offline regex extractors tuned for Brazilian tax terminology:
  - **Taxpayer Identification:** CNPJ (`\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}`) / CPF and corporate name.
  - **Taxing Authority:** Identification of Federal Revenue (Receita Federal), State Secretariats (SEFAZ), or Municipal Finance bodies.
  - **Identified Taxes:** Detection of ICMS, IRPJ, CSLL, PIS, COFINS, IPI, ISS, ITCMD, IPVA, IPTU.
  - **Financial Breakdown:** Brazilian Real (`R$`) parsing for Principal, Fine (*Multa de Ofício/Isolada*), Interest (*Juros Selic*), and Total Assessment.
  - **Critical Dates:** Date of issuance (*lavratura*), formal notice (*intimação*), and payment/due date.
  - **Legal Articles:** Automated detection of invoked laws, decrees, CTN, and state regulations.
- **LLM Schema Fallback:** Support for structured LLM parsing with automatic fallback to deterministic extraction if no API key is provided.

### 2.3 Executive Summary & Risk Assessment (`TaxSummaryService`)
- Automated detection of allegation theses (e.g., credit disallowance, revenue omission, non-deductible expenses).
- Administrative deadline calculation (e.g., 30-day statutory limit for administrative defense under Decree 70.235/1972 or state codes).
- Risk scoring (`ALTO`, `MEDIO`, `BAIXO`) based on total exposure and penalty severity.
- Exportable Markdown legal memorandums.

### 2.4 Grounded RAG with Verbatim Citations (`TaxRetrievalService`)
- In-memory BM25 indexer with Portuguese stop-word filtering.
- **Zero-Tolerance Anti-Hallucination Guardrail:** If query relevance is below threshold, the system returns:  
  `"A informação não foi localizada no documento analisado."` with empty citations.
- **Mandatory Attribution:** Every factual response is anchored to exact page numbers and verbatim excerpts from the source document.

---

## 3. Tax Document Taxonomy

| Type Code | Brazilian Tax Instrument | Scope & Critical Fields Extracted |
|---|---|---|
| `AIIM` | Auto de Infração e Imposição de Multa | State/Municipal tax notice (ICMS/ISS), punitive fines, credit glosa, TIT defense deadline. |
| `NL` | Notificação de Lançamento | Direct Federal assessment (IRPJ/CSLL), Lalur glosas, DRJ impugnation terms. |
| `COSIT` | Solução de Consulta Tributária | Federal Revenue interpretive binding ruling, legal thesis, PIS/COFINS credits. |
| `DARF` | Documento de Arrecadação | Federal tax collection form, revenue code, maturity date, principal amounts. |
| `CND` | Certidão de Regularidade Fiscal | Negative/Positive clearance certificates, validity expiration. |

---

## 4. Getting Started

### 4.1 Prerequisites
- Python 3.11+
- Virtual environment with requirements installed:
  ```bash
  pip install -r requirements.txt
  ```

### 4.2 Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4.3 Makefile Commands
```bash
# Run 100% of the test suite
make test

# Check code with Ruff
make lint

# Auto-format code
make format

# Populate database with realistic synthetic tax notices
make seed

# Start FastAPI backend (port 8002)
make run-backend

# Start React 18 + Vite frontend (port 8503)
make run-frontend
```

---

## 5. REST API Reference

The backend exposes interactive documentation at `http://localhost:8002/docs`.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` ou `/api/v1/health` | Service health status and version |
| `POST` | `/api/v1/documents/upload` | Multipart PDF upload and chunking |
| `POST` | `/api/v1/documents/text` | Direct raw text intake for testing |
| `GET` | `/api/v1/documents` | Catalog listing with filters |
| `GET` | `/api/v1/documents/{id}` | Full document detail with chunks |
| `POST` | `/api/v1/documents/{id}/extract` | Run structured tax entity extraction |
| `GET` | `/api/v1/documents/{id}/summary` | Generate executive brief and deadlines |
| `POST` | `/api/v1/chat/sessions` | Create a new Q&A session |
| `POST` | `/api/v1/chat/sessions/{id}/query` | Grounded Q&A with verbatim citations |
| `GET` | `/api/v1/chat/sessions/{id}/history` | Message conversation history |
| `GET` | `/api/v1/dashboard/metrics` | Portfolio exposure and document statistics |

---

## 6. React 18 User Interface (Port 8503)

Built with React 18, Vite, Tailwind CSS, and Lucide Icons (zero emojis):

- **Dashboard:** Portfolio exposure KPI cards (Total Assessed Debt, Principal, Penalties, Interest), document taxonomy distribution, and recent activity.
- **Documentos & Ingestão:** Drag-and-drop file uploader supporting `.pdf` and `.txt` with automated parsing, hashing, and processing status.
- **Visualizador & Entidades:** Side-by-side inspection of paginated document chunks alongside structured metadata (CNPJ, taxpayer, authorities, taxes, amounts, statutory articles).
- **Resumo Executivo & Prazos:** Executive memorandum with procedural timelines (+30 days administrative defense under Decree 70.235/1972 or state law) and financial exposure scoring.
- **Chat com Documentos (Grounded Q&A):** Conversational interface powered by BM25 retrieval, exact page citations, and zero-hallucination guardrail.

---

## 7. Docker Deployment

Deploy backend and frontend services using Docker Compose:
```bash
docker compose up --build -d
```
- Backend API available at: `http://localhost:8002/docs`
- React Frontend available at: `http://localhost:8503`
