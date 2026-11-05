import pandas as pd
import streamlit as st
from utils import list_requests

st.set_page_config(page_title="Solicitações | LexFlow", page_icon=None, layout="wide")

st.title(" Solicitações Cadastradas")
st.caption("Consulte, filtre e acompanhe o fluxo de triagem interna.")

# Filters
f1, f2, f3, f4 = st.columns([2, 2, 2, 3])

STATUSES = ["TODOS", "NEW", "TRIAGE", "IN_PROGRESS", "WAITING", "RESOLVED", "CANCELLED"]
CATEGORIES = [
    "TODAS",
    "ACCESS_AND_SYSTEMS",
    "DOCUMENTS_AND_TEMPLATES",
    "DATA_AND_REPORTS",
    "AI_AND_AUTOMATION",
    "INTERNAL_REQUEST",
    "OTHER",
]
PRIORITIES = ["TODAS", "LOW", "NORMAL", "HIGH", "URGENT"]

with f1:
    selected_status = st.selectbox("Status", options=STATUSES)
with f2:
    selected_cat = st.selectbox("Categoria", options=CATEGORIES)
with f3:
    selected_prio = st.selectbox("Prioridade", options=PRIORITIES)
with f4:
    search_query = st.text_input("Buscar por termo", placeholder="Ex.: Acesso, VPN, Relatório...")

# Fetch data
requests_data = list_requests(
    status=selected_status,
    category=selected_cat,
    priority=selected_prio,
    search=search_query.strip() if search_query else None,
)

if not requests_data:
    st.info("Nenhuma solicitação encontrada para os filtros selecionados.")
else:
    st.write(f"**Total de registros encontrados:** {len(requests_data)}")

    # Display clean table
    formatted = []
    for r in requests_data:
        formatted.append({
            "ID": r["id"],
            "Título": r["title"],
            "Status": r["status"],
            "Categoria": r["category"] or "Não classificada",
            "Equipe": r["team"] or "Não definida",
            "Prioridade": r["priority"],
            "Origem": r["classification_source"] or "Pendente",
            "Confiança": f"{r['classification_confidence']:.2f}" if r["classification_confidence"] else "-",
            "Criado em": r["created_at"][:19].replace("T", " ") if r.get("created_at") else "-",
        })

    df = pd.DataFrame(formatted)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.write("#####  Ação Rápida")
    st.info("Para visualizar o histórico completo ou revisar a classificação de uma solicitação, acerte o ID na página **Detalhes e Revisão** no menu lateral.")
