import streamlit as st

from frontend.api_client import api_client

st.set_page_config(page_title="Visualizador & Extração | LexTax", page_icon=None, layout="wide")

st.title(" Visualizador e Extração Estruturada")
st.caption("Visão comparativa entre o texto integral paginado e as entidades tributárias extraídas deterministicamente.")

# Load available documents
docs = api_client.list_documents()
if not docs:
    st.warning("Nenhum documento carregado. Retorne à página inicial para enviar um arquivo.")
    st.stop()

doc_map = {f"{d['filename']} ({d['document_type']}) - {d['id'][:8]}": d["id"] for d in docs}

default_idx = 0
selected_id = st.session_state.get("selected_doc_id")
if selected_id:
    for i, (k, v) in enumerate(doc_map.items()):
        if v == selected_id:
            default_idx = i
            break

selected_key = st.selectbox("Selecione o Documento Fiscal:", list(doc_map.keys()), index=default_idx)
doc_id = doc_map[selected_key]
st.session_state["selected_doc_id"] = doc_id

doc = api_client.get_document(doc_id)
if not doc:
    st.error("Documento não encontrado.")
    st.stop()

# Action bar
col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    if st.button(" Reprocessar Extração", use_container_width=True):
        with st.spinner("Extraindo entidades..."):
            api_client.extract_document(doc_id, force=True)
            st.success("Extração reprocessada com sucesso!")
            st.rerun()

extraction = api_client.extract_document(doc_id)

st.divider()

col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader(f" Texto Integral ({doc['total_pages']} páginas, {len(doc.get('chunks', []))} chunks)")
    st.text_area(
        "Conteúdo extraído:",
        value=doc["raw_text"],
        height=620,
        disabled=True,
    )

with col_right:
    st.subheader(" Entidades Fiscais Estruturadas")
    if not extraction:
        st.info("Nenhuma extração gerada.")
    else:
        # Contribuinte Card
        st.markdown(
            f"""
            <div style="background-color: #F1F5F9; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #2563EB;">
                <div style="font-size: 0.85rem; color: #64748B; font-weight: 600;">CONTRIBUINTE / AUTUADO</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{extraction.get('contribuinte_nome') or 'Não identificado'}</div>
                <div style="font-size: 0.9rem; color: #334155;">CNPJ/CPF: <b>{extraction.get('contribuinte_cnpj_cpf') or 'Não localizado'}</b></div>
                <div style="font-size: 0.85rem; color: #475569;">Órgão Autuante: <b>{extraction.get('orgao_fiscal') or 'Não identificado'}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Values Breakdown
        st.markdown("#####  Decomposição do Crédito Tributário")
        val_total = extraction.get("valor_total", 0.0)
        val_princ = extraction.get("valor_principal", 0.0)
        val_multa = extraction.get("valor_multa", 0.0)
        val_juros = extraction.get("valor_juros", 0.0)

        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.metric("Total da Autuação", f"R$ {val_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("Multa de Ofício", f"R$ {val_multa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with v_col2:
            st.metric("Valor Principal", f"R$ {val_princ:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("Juros Selic/Mora", f"R$ {val_juros:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Taxes and Dates
        st.markdown("#####  Tributos e Competência")
        tributos = extraction.get("tributos_identificados", [])
        if tributos:
            st.write(" ".join([f"`{t}`" for t in tributos]))
        else:
            st.caption("Nenhum tributo específico detectado.")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.write(f" **Data Intimação:** {extraction.get('data_intimacao') or 'Não informada'}")
        with d_col2:
            st.write(f" **Vencimento:** {extraction.get('data_vencimento') or 'Não informado'}")

        # Legal Citations
        st.markdown("#####  Dispositivos Legais Invocados")
        arts = extraction.get("dispositivos_legais", [])
        if arts:
            for art in arts:
                st.markdown(f"- `{art}`")
        else:
            st.caption("Nenhum artigo localizado.")

        st.caption(f"Método: `{extraction.get('extraction_method')}` | Confiança: `{int(extraction.get('confidence_score', 0) * 100)}%`")
