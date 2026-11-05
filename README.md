# Legal Operations & AI Platform --- Monorepo

> **Repositório Monorepo** consolidando o ecossistema integrado de soluções jurídicas: automação de processos e triagem de solicitações, avaliação contínua e benchmarking de IA, e análise estruturada de documentos tributários com respostas fundamentadas.

---

## 1. Visão Geral da Plataforma

Este repositório adota uma arquitetura monorepo modular para gerenciar três soluções tecnológicas complementares voltadas à eficiência operacional, confiabilidade e governança de Inteligência Artificial:

```text
GRM-adv/
├── Makefile                       # Orquestrador global de tarefas (testes, linting, execução)
├── docker-compose.yml             # Orquestração unificada de containers (portas 8000-8002 / 8501-8503)
├── README.md                      # Documentação central do monorepo
├── .gitignore                     # Regras globais de exclusão
│
└── projects/
    ├── lexflow/                   # Módulo 1: Automação e Triagem de Solicitações Internas
    │   ├── backend/               # API FastAPI (:8000), Pydantic v2, SQLAlchemy, State Machine
    │   ├── frontend/              # Interface Streamlit (:8501) com dashboard e revisão humana
    │   ├── scripts/               # Carga inicial de dados de demonstração
    │   └── Makefile               # Automação local do projeto
    │
    ├── lexeval/                   # Módulo 2: Plataforma de Avaliação e Observabilidade de IA
    │   ├── backend/               # API FastAPI (:8001), Evaluators (Faithfulness, Citations, A/B)
    │   ├── frontend/              # Interface Streamlit (:8502) com comparador e catálogo de falhas
    │   ├── scripts/               # Carga de Golden Datasets sintéticos
    │   └── Makefile               # Automação local do projeto
    │
    └── tax-assistant/             # Módulo 3: LexTax - Análise e Consulta de Documentos Tributários
        ├── backend/               # API FastAPI (:8002), Ingestão PDF, Extrator de Tributos, RAG
        ├── frontend/              # Interface Streamlit (:8503) com visualizador e chat com fontes
        ├── scripts/               # Carga de autos de infração e pareceres sintéticos
        └── Makefile               # Automação local do projeto
```

---

## 2. Mapeamento de Portas e Serviços

| Projeto | Serviço | Tipo | Porta Local | Documentação / Interface |
|---|---|---|---|---|
| **LexFlow** | Backend | FastAPI | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **LexFlow** | Frontend | Streamlit | `8501` | [http://localhost:8501](http://localhost:8501) |
| **LexEval** | Backend | FastAPI | `8001` | [http://localhost:8001/docs](http://localhost:8001/docs) |
| **LexEval** | Frontend | Streamlit | `8502` | [http://localhost:8502](http://localhost:8502) |
| **LexTax** | Backend | FastAPI | `8002` | [http://localhost:8002/docs](http://localhost:8002/docs) |
| **LexTax** | Frontend | Streamlit | `8503` | [http://localhost:8503](http://localhost:8503) |

---

## 3. Módulos do Repositório

### [1. LexFlow --- Automação e Triagem Interna](projects/lexflow/README.md)
*Status: Operacional / Concluído (31 testes automatizados)*
- **Finalidade:** Centralização, validação estrita e classificação automática de chamados operacionais de escritórios e departamentos jurídicos.
- **Destaques:** Motor híbrido de classificação (regras determinísticas + LLM opcional), fallback automático resiliente com zero indisponibilidade, máquina de estados com transições restritas e painel de revisão humana obrigatório (*Human-in-the-Loop*).
- **Stack:** Python, FastAPI, Pydantic v2, SQLAlchemy, Streamlit.

### [2. LexEval --- Avaliação e Observabilidade de IA](projects/lexeval/README.md)
*Status: Operacional / Concluído (20 testes automatizados)*
- **Finalidade:** Plataforma contínua de benchmarking, validação de acurácia fática e detecção automatizada de alucinações em respostas de IA aplicadas ao contexto jurídico.
- **Destaques:** Gestão de Golden Datasets com ground truth, métricas de fidelidade fática (*Faithfulness*), precisão de citações legais e normativas, comparador A/B de versões de prompts com identificação de regressões, e catálogo de incidentes.
- **Stack:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic v2, Streamlit.

### [3. LexTax (Tax Assistant) --- Análise de Documentos Tributários](projects/tax-assistant/README.md)
*Status: Operacional / Concluído (30 testes automatizados)*
- **Finalidade:** Ingestão de arquivos PDF fiscais (Autos de Infração, Notificações de Lançamento, Pareceres e Guias) com extração estruturada de tributos, valores decompostos e prazos de impugnação.
- **Destaques:** Extração determinística de CNPJ, tributos (ICMS, PIS, COFINS, ISS, IRPJ, CSLL), valores monetários em BRL (Principal, Multa, Juros, Total) e motor de consulta RAG com citação verbatim obrigatória e número de página, prevenindo alucinações fáticas.
- **Stack:** Python, FastAPI, PyPDF, BM25 Tokenizer, SQLAlchemy, SQLite, Streamlit.

---

## 4. Guia Rápido de Execução

### Ambiente Local com Python Virtualenv

1. **Ativar o ambiente virtual compartilhado:**
   ```bash
   source .venv/bin/activate
   ```

2. **Popular dados de demonstração em todos os módulos:**
   ```bash
   make seed-all
   ```
   *(Ou individualmente: `make seed-lexflow`, `make seed-lexeval`, `make seed-tax`)*

3. **Iniciar serviços individuais conforme necessário:**
   ```bash
   # LexFlow (Triagem e Solicitações)
   make run-lexflow-backend   # Porta 8000
   make run-lexflow-frontend  # Porta 8501

   # LexEval (Avaliação de IA)
   make run-lexeval-backend   # Porta 8001
   make run-lexeval-frontend  # Porta 8502

   # LexTax (Análise Tributária e RAG)
   make run-tax-backend       # Porta 8002
   make run-tax-frontend      # Porta 8503
   ```

---

### Execução via Docker Compose

Inicie todos os 6 serviços (3 backends + 3 frontends) de forma simultânea com redes e volumes isolados:

```bash
docker compose up --build -d
```

Para encerrar todos os containers:
```bash
docker compose down
```

---

## 5. Testes Automatizados e Qualidade de Código

O repositório mantém **100% de cobertura nos fluxos principais**, somando **81 testes automatizados** e zero pendências de linting ou formatação:

```bash
# Executar todos os 81 testes do monorepo de uma só vez
make test-all

# Executar testes por projeto específico
make test-lexflow          # 31 testes
make test-lexeval          # 20 testes
make test-tax-assistant    # 30 testes

# Executar análise estática de código (Ruff) em todo o repositório
make lint-all
```
