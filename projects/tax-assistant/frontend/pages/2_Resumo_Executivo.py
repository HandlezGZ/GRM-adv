import streamlit as st

from frontend.api_client import api_client

st.set_page_config(page_title="Resumo Executivo | LexTax", page_icon=None, layout="wide")

st.title(" Resumo Executivo e Linha do Tempo Processual")
st.caption("Síntese jurídica da autuação, cálculo de contingência e prazos decadenciais/preclusivos.")

docs = api_client.list_documents()
if not docs:
    st.warning("Nenhum documento cadastrado.")
    st.stop()

doc_map = {f"{d['filename']} ({d['document_type']}) - {d['id'][:8]}": d["id"] for d in docs}
default_idx = 0
selected_id = st.session_state.get("selected_doc_id")
if selected_id:
    for i, (k, v) in enumerate(doc_map.items()):
        if v == selected_id:
            default_idx = i
            break

chosen = st.selectbox("Selecione o Documento:", list(doc_map.keys()), index=default_idx)
doc_id = doc_map[chosen]
st.session_state["selected_doc_id"] = doc_id

summary = api_client.get_summary(doc_id)
if not summary:
    st.error("Não foi possível gerar o resumo executivo para este documento.")
    st.stop()

st.divider()

# Top Cards
card_col1, card_col2, card_col3 = st.columns(3)

risk = summary.get("grau_risco", "MEDIO")
risk_color = "#DC2626" if risk == "ALTO" else ("#D97706" if risk == "MEDIO" else "#16A34A")

with card_col1:
    st.markdown(
        f"""
        <div style="background-color: #FEF2F2 if '{risk}' == 'ALTO' else #F8FAFC; border: 1px solid {risk_color}; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-size: 0.85rem; color: #64748B;">GRAU DE RISCO / CONTINGÊNCIA</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: {risk_color};">{risk}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_col2:
    prazos = summary.get("prazos", {})
    st.markdown(
        f"""
        <div style="border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; text-align: center; background-color: #F8FAFC;">
            <div style="font-size: 0.85rem; color: #64748B;">LIMITE IMPUGNAÇÃO (30 DIAS)</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #1E293B;">{prazos.get('prazo_impugnacao_administrativa') or 'Pendente'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_col3:
    tot = summary.get("total_autuado", 0.0)
    tot_fmt = f"R$ {tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(
        f"""
        <div style="border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; text-align: center; background-color: #F8FAFC;">
            <div style="font-size: 0.85rem; color: #64748B;">EXIGÊNCIA FISCAL TOTAL</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #1E293B;">{tot_fmt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.subheader(" Tese de Acusação Fiscal")
st.info(summary.get("tese_acusacao", "Não identificada."))

st.subheader(" Memorando Resumido Completo")
resumo_text = summary.get("resumo_texto", "")
st.markdown(resumo_text)

# Download button
st.download_button(
    label=" Baixar Memorando em Markdown",
    data=resumo_text,
    file_name=f"memorando_{summary.get('filename', 'resumo')}.md",
    mime="text/markdown",
    use_container_width=True,
)
