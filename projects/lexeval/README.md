# LexEval — Continuous AI Evaluation & Quality Monitoring Platform

> **LexEval** is an enterprise-grade evaluation, benchmarking, and observability platform specifically engineered for legal and tax artificial intelligence systems. It provides continuous verification of factual faithfulness, detects hallucinations, analyzes prompt regressions via A/B testing, and audits safety guardrail compliance.

---

## 1. Overview & Key Capabilities

Deploying generative models in high-stakes domains like law and taxation requires strict verification against ground truth and source documents. LexEval automates quality assurance through multi-dimensional scoring pipelines:

- **Golden Datasets Management:** Versioned repositories of test cases containing legal questions, context documents (statutes, administrative rulings, court precedents), and curated ground truth answers.
- **Deterministic & Semantic Evaluators:**
  - *Context Faithfulness (Groundedness):* Sentence-level claim verification and numerical entity extraction to ensure zero factual fabrication.
  - *Legal Citation Precision:* Regex-based extraction and context validation of laws, articles, and judicial themes (e.g., STJ Tema 779, STF ADI 5659).
  - *Schema & Guardrail Compliance:* Validation of structured formats (JSON) and active detection of forbidden terms or unauthorized advice.
  - *Answer Relevance:* Lexical similarity and mandatory keyword coverage against reference standards.
- **A/B Testing & Regression Detection:** Automated comparison between baseline prompts and candidate versions, categorizing outcomes into *Gains*, *Regressions*, and *Ties*.
- **Failure Catalog & Diagnostics:** Audit registry storing all defective model outputs, categorized by root cause (`HALLUCINATED_CITATION`, `HALLUCINATED_NUMERICAL_VALUE`, `FORBIDDEN_TERM_VIOLATION`, `UNGROUNDED_CLAIM`, `SCHEMA_ERROR`).
- **Interactive Multi-Page Streamlit Dashboard:** Operational interface with KPI metric cards, quality trends, failure browsers, and dataset editors.

---

## 2. Architecture & Logical Design

```text
┌────────────────────────────────────────────────────────┐
│             Streamlit Web Dashboard (Port 8502)        │
│  [Overview]  [Run Benchmark]  [A/B Test]  [Failures]   │
└──────────────────────────┬─────────────────────────────┘
                           │ (HTTP REST / JSON)
                           
┌────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8001)              │
│  /health  /api/v1/datasets  /api/v1/prompts  /eval     │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
                                         
┌──────────────────────────────┐ ┌──────────────────────────────┐
│       Evaluation Engine      │ │       Persistence Layer      │
│ ├── DeterministicEvaluator   │ │ ├── SQLAlchemy ORM           │
│ ├── FaithfulnessEvaluator    │ │ ├── SQLite / PostgreSQL      │
│ ├── PromptBenchmarkService   │ │ └── Repository Pattern       │
│ └── LLM-Judge (Mock/Fallback)│ └──────────────────────────────┘
└──────────────────────────────┘
```

---

## 3. Multi-Dimensional Quality Metrics

| Metric | Type | Scale | Description |
|---|---|---|---|
| **`Schema Compliance`** | Deterministic | `0.0` or `1.0` | Verifies structured output conformance (valid JSON and required fields). |
| **`Context Faithfulness`** | Hybrid | `0.0` to `1.0` | Measures degree to which assertions are backed by the source document. Penalized on ungrounded claims. |
| **`Citation Precision`** | Regex / Grounding | `0.0` to `1.0` | Verifies whether cited statutes (e.g. `CTN art. 174`) exist in the reference context. |
| **`Numerical Grounding`** | Factual | `0.0` to `1.0` | Verifies dates, deadlines, rates, and monetary amounts against source text. |
| **`Answer Relevance`** | Lexical / Overlap | `0.0` to `1.0` | Weighted combination of required keywords presence and token overlap against expected answer. |
| **`Negative Constraints`** | Guardrail | `Pass` / `Fail` | Enforces absence of prohibited expressions or dangerous assumptions. |

---

## 4. API Reference (`/api/v1`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status and version |
| `POST` | `/api/v1/datasets` | Create a new evaluation golden dataset |
| `GET` | `/api/v1/datasets` | List all datasets with test case counts |
| `GET` | `/api/v1/datasets/{id}/cases` | List all test cases in a dataset |
| `POST` | `/api/v1/datasets/{id}/cases` | Add a new test case to a dataset |
| `POST` | `/api/v1/prompts` | Register a new prompt version |
| `GET` | `/api/v1/prompts` | List all prompt versions |
| `POST` | `/api/v1/eval/run` | Execute batch evaluation on a dataset |
| `GET` | `/api/v1/eval/runs` | List evaluation history |
| `GET` | `/api/v1/eval/runs/{id}` | Detailed run metrics and case-by-case diagnostics |
| `GET` | `/api/v1/eval/compare` | Compare two runs (A/B testing, regression analysis) |
| `GET` | `/api/v1/eval/failures` | Query catalog of failed evaluations and hallucinations |
| `GET` | `/api/v1/dashboard/metrics` | Aggregated executive KPIs and failure distribution |

---

## 5. Getting Started

### 5.1 Prerequisites
- Python `>= 3.11`
- SQLite 3 or PostgreSQL
- Docker & Docker Compose (optional)

### 5.2 Local Installation & Execution

```bash
# Navigate to the project directory
cd projects/lexeval

# Install dependencies in editable mode
pip install -e .[dev]

# Seed golden tax dataset and prompt versions
make seed

# Run the backend API server (port 8001)
make run-backend

# In a separate terminal, launch the Streamlit frontend (port 8502)
make run-frontend
```

Once running, access:
- **Streamlit Dashboard:** [http://localhost:8502](http://localhost:8502)
- **FastAPI Interactive Docs (Swagger):** [http://localhost:8001/api/v1/docs](http://localhost:8001/api/v1/docs)

### 5.3 Docker Compose Execution

```bash
cd projects/lexeval
docker compose up --build -d
```

---

## 6. Testing & Code Quality

The project enforces comprehensive test coverage across unit and integration levels, guaranteeing zero external network dependencies during tests:

```bash
# Run full test suite with verbose output
make test

# Run unit tests only
make test-unit

# Run API integration tests
make test-integration

# Code formatting and linting
make lint
make format
```
