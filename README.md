# Legal Operations & AI Platform --- Monorepo

> **Repositório Monorepo** consolidando o ecossistema integrado de soluções de automação de processos internos, avaliação contínua de IA e assistência especializada em documentos jurídicos.

---

## 1. Visão Geral da Plataforma

Este repositório adota uma arquitetura monorepo modular para gerenciar soluções tecnológicas complementares voltadas à eficiência operacional e ao uso responsável de Inteligência Artificial:

```text
GRM-adv/
├── Makefile                       # Orquestrador global de tarefas (testes, linting, execução)
├── docker-compose.yml             # Orquestração unificada de containers
├── README.md                      # Documentação central do monorepo
├── .gitignore                     # Regras globais de exclusão
│
└── projects/
    ├── lexflow/                   # Módulo 1: Automação e Triagem de Solicitações Internas
    │   ├── backend/               # API FastAPI, Pydantic v2, SQLAlchemy, State Machine
    │   ├── frontend/              # Interface Streamlit com dashboard e revisão humana
    │   ├── scripts/               # Carga inicial de dados de demonstração
    │   ├── Makefile               # Automação local do projeto
    │   └── README.md              # Documentação técnica específica do LexFlow
    │
    ├── lexeval/                   # Módulo 2: Avaliação e Monitoramento de Qualidade de IA
    │   └── README.md              # Especificação de benchmarking fático e detecção de alucinações
    │
    └── tax-assistant/             # Módulo 3: Assistente de Análise de Documentos Tributários
        └── README.md              # Especificação de extração estruturada e Q&A fundamentado
```

---

## 2. Módulos do Repositório

### [1. LexFlow --- Automação e Triagem Interna](projects/lexflow/README.md)
*Status: Operacional / Concluído*
- **Finalidade:** Centralização, validação estrita e classificação de chamados operacionais.
- **Destaques:** Motor híbrido de classificação (regras determinísticas + LLM opcional), fallback automático resiliente com zero indisponibilidade, máquina de estados com transições restritas e painel de revisão humana obrigatório (*Human-in-the-Loop*).
- **Stack:** Python, FastAPI, Pydantic v2, SQLAlchemy, Streamlit.

### [2. LexEval --- Avaliação e Observabilidade de IA](projects/lexeval/README.md)
*Status: Especificado / Pronto para Implementação*
- **Finalidade:** Plataforma contínua de benchmarking, validação de acurácia fática e detecção de alucinações em respostas de IA jurídica.
- **Destaques:** Golden datasets com ground truth, métricas de fidelidade (*Faithfulness*), precisão de citações normativas, comparador A/B de versões de prompts e catálogo automatizado de falhas.

### [3. TaxAssistant --- Análise de Documentos Tributários](projects/tax-assistant/README.md)
*Status: Planejado*
- **Finalidade:** Processamento de autos de infração, acórdãos e certidões com extração estruturada de tributos, alíquotas e obrigações, acompanhado de respostas fundamentadas em trechos originais.

---

## 3. Como Executar

### Ambiente Local com Python Virtualenv

1. **Criar e ativar o ambiente virtual na raiz:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

2. **Instalar dependências de todos os módulos ativos:**
   ```bash
   make install-all
   ```

3. **Popular dados de demonstração do LexFlow:**
   ```bash
   make seed-lexflow
   ```

4. **Executar serviços do LexFlow:**
   - **Backend API (FastAPI):**
     ```bash
     make run-lexflow-backend
     ```
     *Acesse a documentação Swagger:* [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Frontend (Streamlit):**
     ```bash
     make run-lexflow-frontend
     ```
     *Acesse o painel web:* [http://localhost:8501](http://localhost:8501)

---

### Execução via Docker Compose

Inicie todos os serviços da plataforma com portas isoladas:
```bash
docker compose up --build -d
```
- **LexFlow Frontend:** [http://localhost:8501](http://localhost:8501)
- **LexFlow Backend:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 4. Testes e Qualidade

O repositório impõe padrões estritos de qualidade através de suítes de testes automatizados e formatação via Ruff:

```bash
# Executar testes em todos os projetos
make test-all

# Executar testes específicos do LexFlow
make test-lexflow

# Verificar linting e formatação em todos os projetos
make lint-all
```
