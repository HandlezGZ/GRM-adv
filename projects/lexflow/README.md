# LexFlow --- Sistema de Automação e Triagem de Solicitações Internas

> **LexFlow** é uma plataforma moderna e resiliente para recebimento, classificação automática, encaminhamento e auditoria de demandas e chamados internos em operações corporativas e jurídicas.

---

## 1. Visão Geral

Em operações corporativas com múltiplos departamentos, o recebimento descentralizado de solicitações (via mensagens instantâneas, e-mails ou canais informais) acarreta perda de rastreabilidade, triagem inconsistente, encaminhamento para equipes incorretas e falta de visibilidade sobre pendências e tempos de atendimento.

O **LexFlow** resolve esse gargalo através de um fluxo digital integrado:
- **Entrada Padronizada:** Cadastro com validação de esquema em tempo real via Pydantic v2.
- **Classificação Determinística por Regras (`RulesClassifier`):** Motor local baseado em padrões e termos operacionais, sem dependência de serviços externos.
- **Integração Opcional com IA (`LLMClassifier`):** Suporte a modelos generativos com saída estritamente estruturada em JSON e validação contra schema tipado.
- **Resiliência e Fallback Automático:** Caso o provedor de IA apresente indisponibilidade, erro de rede ou timeout, o sistema aciona instantaneamente o motor de regras locais, registrando o incidente para auditoria sem interromper o serviço.
- **Revisão Humana ("Human-in-the-Loop"):** A IA atua como assistente de triagem; os analistas operacionais têm autoridade total para revisar, confirmar ou ajustar categorias, equipes e prioridades com registro formal de justificativa.
- **Workflow com Máquina de Estados:** Controle estrito de transições (`NEW`  `TRIAGE`  `IN_PROGRESS`  `WAITING`  `RESOLVED` / `CANCELLED`) com registro imutável de eventos (`RequestEvent`).
- **Dashboard Operacional:** Interface interativa em Streamlit com métricas de volumetria, distribuição por categoria/prioridade e monitoramento de qualidade.

---

## 2. Princípios de Segurança e Privacidade

1. **Dados Controlados:** A aplicação é concebida para operar com dados estruturados de demonstração e ambientes controlados.
2. **Mitigação de Prompt Injection:** Todo conteúdo inserido pelo solicitante é tratado como dado não confiável. O prompt versionado instrui o classificador a ignorar instruções operacionais contidas na descrição da solicitação.
3. **Gestão Segura de Configurações:** Variáveis de ambiente e credenciais são gerenciadas via `.env` (com modelo em `.env.example`), sem expor secrets no código.
4. **Ausência de Efeitos Colaterais Externos:** A IA atua exclusivamente na inferência estruturada de categorias e equipes, sem permissão para executar comandos no sistema ou disparar comunicações externas descontroladas.

---

## 3. Arquitetura e Tecnologias

```
[Streamlit UI - Frontend]
       │
        (HTTP / REST JSON)
[FastAPI REST API - Backend]
       │
       ├── [Workflow Service - Máquina de Estados]
       │
       ├── [Classification Service]
       │      │
       │      ├── [Rules Engine (Local & Determinístico)]
       │      └── [Optional LLM Provider (Com Fallback)]
       │
       ├── [Audit & Event Logger]
       │
        (SQLAlchemy ORM)
[Banco de Dados - SQLite / PostgreSQL]
```

- **Backend:** Python 3.12+, FastAPI, Pydantic v2, Pydantic-Settings.
- **Persistência:** SQLAlchemy 2.0 (SQLite para desenvolvimento ágil / PostgreSQL para produção).
- **Frontend:** Streamlit com componentes analíticos e interface multi-página.
- **Qualidade de Código:** Ruff (linter e formatador) e Pytest (31 testes automatizados).
- **Containerização:** Docker Compose para orquestração de backend e frontend.

---

## 4. Como Executar

### Opção A: Ambiente Local com Python Virtualenv (Recomendado)

1. **Criar e ativar o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

2. **Instalar as dependências:**
   ```bash
   pip install -r backend/requirements.txt -r frontend/requirements.txt
   ```

3. **Popular o banco com dados de demonstração:**
   ```bash
   python scripts/seed_demo_data.py
   ```

4. **Iniciar o Backend (FastAPI):**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Documentação interativa Swagger:* [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Iniciar o Frontend (Streamlit) em outro terminal:**
   ```bash
   source .venv/bin/activate
   streamlit run frontend/app.py --server.port 8501
   ```
   *Acesso à interface web:* [http://localhost:8501](http://localhost:8501)

---

### Opção B: Execução via Docker Compose

```bash
docker compose up --build -d
```
- **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)
- **Backend API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Testes Automatizados

O projeto conta com **31 testes automatizados** cobrindo integração de endpoints, regras de workflow, validação de schemas, resiliência de fallback e persistência.

```bash
# Executar a suíte de testes
pytest backend/tests -v

# Executar verificação de linting
ruff check backend frontend scripts
```

---

## 6. Endpoints Principais da API REST (`/api/v1`)

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Verificação de integridade e modo de classificação ativo |
| `POST` | `/api/v1/requests` | Cadastra nova solicitação com validação estrita |
| `GET` | `/api/v1/requests` | Lista e filtra solicitações (status, categoria, busca textual) |
| `GET` | `/api/v1/requests/{id}` | Retorna detalhes completos de uma solicitação |
| `POST` | `/api/v1/requests/{id}/classify` | Executa classificação automática (Regras ou IA) |
| `POST` | `/api/v1/requests/{id}/review` | Registra revisão humana com justificativa obrigatória |
| `PATCH` | `/api/v1/requests/{id}/status` | Atualiza status respeitando as transições permitidas |
| `GET` | `/api/v1/requests/{id}/events` | Retorna histórico de auditoria e eventos |
| `GET` | `/api/v1/dashboard/metrics` | Métricas consolidadas de volumetria e atendimento |
| `GET` | `/api/v1/classification/failures` | Relatório de falhas e incidentes do classificador |

---

## 7. Guia de Demonstração do Fluxo

1. **Dashboard Operacional:** Acesse `http://localhost:8501` para visualizar o panorama de solicitações ativas, resolvidas e gráficos de distribuição.
2. **Cadastro:** Na página **Nova Solicitação**, preencha o formulário e marque a opção de classificação imediata.
3. **Triagem Automática:** Observe como o motor analisa o conteúdo, atribui categoria e equipe correspondente e justifica a decisão.
4. **Revisão Humana:** Na página **Detalhes e Revisão**, utilize o painel de validação para ajustar parâmetros e registrar a justificativa formal do analista.
5. **Máquina de Estados:** Altere o status de `TRIAGE` para `IN_PROGRESS` e acompanhe a evolução do chamado na **Trilha de Auditoria**.
6. **Resiliência e Falhas:** Na página **Qualidade e Falhas**, inspecione o monitoramento de incidentes e a política de fallback determinístico.

---

## 8. Estrutura do Repositório

```text
GRM-adv/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Endpoints da API REST
│   │   ├── core/                # Configurações e logging
│   │   ├── db/                  # Conexão e inicialização do banco
│   │   ├── models/              # Entidades SQLAlchemy (Request, Event, Attempt)
│   │   ├── prompts/             # Templates versionados de prompt
│   │   ├── repositories/        # Camada de persistência
│   │   └── services/            # Classificadores (Rules, LLM) e Workflow
│   └── tests/                   # Testes unitários e de integração
├── frontend/
│   ├── app.py                   # Dashboard principal Streamlit
│   ├── pages/                   # Páginas da aplicação web
│   └── utils.py                 # Cliente de integração com a API
├── scripts/
│   └── seed_demo_data.py        # Carga inicial de dados
├── docker-compose.yml           # Orquestração de containers
├── Makefile                     # Comandos de atalho para automação
└── README.md                    # Documentação do projeto
```
