# LexEval --- Plataforma de Avaliação e Monitoramento de IA Jurídica

> **LexEval** é um sistema de avaliação contínua, benchmarking fático, detecção de alucinações e observabilidade para soluções de inteligência artificial aplicadas ao contexto jurídico e corporativo.

---

## 1. Visão Geral

Modelos de linguagem e agentes aplicados ao domínio jurídico exigem rigor absoluto quanto à fundamentação fática e conformidade com normas. O **LexEval** fornece um ambiente estruturado para aferir a qualidade e confiabilidade das respostas antes e durante a operação em produção.

### Principais Capacidades:
- **Golden Datasets:** Repositório de casos de teste com perguntas, documentos de contexto e gabaritos (*ground truth*).
- **Métricas Multi-Dimensionais:**
  - *Context Faithfulness (Groundedness):* Avalia se a resposta se apoia estritamente no documento-fonte ou se contém alucinações.
  - *Citation Precision:* Validação de normas, artigos e cláusulas citadas contra o texto-base.
  - *Answer Relevance:* Mede se a resposta atende diretamente à dúvida formulada.
  - *Schema & Constraint Compliance:* Aderência a formatos JSON estritos e ausência de termos vedados.
- **Comparador A/B de Prompts:** Análise comparativa entre diferentes versões de prompt e modelos para detecção precoce de regressões de qualidade.
- **Catálogo de Incidentes e Falhas:** Registro automatizado de todas as respostas reprovadas com categorização da causa raiz.
- **Dashboard Analítico (Streamlit):** Painel visual com *pass rate*, evolução histórica e exploração caso a caso.

---

## 2. Arquitetura Planejada

```text
projects/lexeval/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Endpoints REST (datasets, runs, prompts, failures)
│   │   ├── core/                # Configurações e logging
│   │   ├── db/                  # Persistência relacional
│   │   ├── models/              # Entidades (EvalDataset, TestCase, EvalRun, Result)
│   │   ├── repositories/        # Repositórios de dados
│   │   └── services/
│   │       ├── evaluators/      # Avaliadores (Deterministic, Faithfulness, LLM-Judge)
│   │       ├── benchmark.py     # Comparador de prompts
│   │       └── diagnostics.py   # Catálogo de falhas
│   └── tests/                   # Suíte de testes automatizados
├── frontend/
│   ├── app.py                   # Dashboard principal Streamlit
│   ├── pages/                   # Páginas (Runs, Comparador, Falhas, Datasets)
│   └── utils.py                 # Cliente de integração com a API
├── scripts/
│   └── seed_golden_dataset.py   # Carga inicial com casos sintéticos
├── Makefile
└── README.md
```

---

## 3. Guia de Execução

Consulte as especificações detalhadas no plano mestre da plataforma em `plano_monitoramento_qualidade_ia.md`.
