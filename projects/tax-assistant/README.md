# TaxAssistant --- Assistente de IA para Análise de Documentos Tributários

> **TaxAssistant** é uma solução de inteligência artificial especializada na análise, extração estruturada de dados e consulta fundamentada sobre documentos, decisões e normas do Direito Tributário.

---

## 1. Visão Geral

Profissionais jurídicos e da área tributária lidam rotineiramente com volumes expressivos de certidões, autos de infração, acórdãos do CARF/tribunais e pareceres complexos. O **TaxAssistant** atua como uma ferramenta de apoio analítico com alta rastreabilidade.

### Principais Capacidades Planejadas:
- **Ingestão e Processamento de Documentos:** Leitura e segmentação de arquivos PDF jurídicos e tributários.
- **Extração Estruturada:** Identificação automática de tributos (IRPJ, CSLL, PIS, COFINS, ICMS, ISS), bases de cálculo, alíquotas, datas de vencimento e obrigações principais/acessórias.
- **Resumos Fáticos e Técnicos:** Síntese executiva com ênfase em teses jurídicas e dispositivos normativos.
- **Consulta Interativa com Citação de Fontes:** Interface conversacional com exibição obrigatória dos trechos originais do documento que fundamentaram cada resposta (zero alucinação tolerada).
- **Integração com LexEval:** Monitoramento contínuo de acurácia fática e precisão de citações através da suíte de avaliação do `LexEval`.

---

## 2. Arquitetura Planejada

```text
projects/tax-assistant/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Ingestão de documentos, chat e extração
│   │   ├── core/                # Configurações e segurança
│   │   ├── services/
│   │   │   ├── extractor.py     # Parser e extrator de metadados tributários
│   │   │   ├── summarizer.py    # Gerador de resumos estruturados
│   │   │   └── qa_service.py    # Q&A com citação obrigatória de fontes
│   └── tests/
├── frontend/
│   ├── app.py                   # Interface interativa Streamlit
│   └── pages/                   # Upload, Análise e Chat Fundamentado
├── data/sample_docs/            # Documentos públicos tributários sintéticos
├── Makefile
└── README.md
```
