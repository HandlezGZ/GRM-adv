import streamlit as st

from frontend.api_client import api_client

st.set_page_config(
    page_title="LexTax | Análise Tributária Inteligente",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header"> LexTax - Assistente Tributário Inteligente</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Plataforma de análise documental, extração estruturada de contingências fiscais e consulta fundamentada com citações verbatim.</div>',
    unsafe_allow_html=True,
)

# Fetch Metrics
metrics = api_client.get_metrics()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Documentos Cadastrados", metrics.get("total_documents", 0))
with col2:
    total_val = metrics.get("total_tax_amount", 0.0)
    st.metric(
        "Débito Total Mapeado",
        f"R$ {total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )
with col3:
    st.metric("Páginas Processadas", metrics.get("total_pages_analyzed", 0))
with col4:
    conf = metrics.get("average_confidence_score", 0.0)
    st.metric("Acurácia Média", f"{int(conf * 100)}%")

st.divider()

# Ingestion / Upload Section
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader(" Ingestão de Documento Fiscal (PDF / TXT)")
    uploaded_file = st.file_uploader(
        "Selecione um arquivo de Auto de Infração, Notificação de Lançamento ou Parecer:",
        type=["pdf", "txt"],
        help="Upload de documento fiscal para análise automática.",
    )
    if uploaded_file is not None:
        if st.button(" Processar Documento", type="primary", use_container_width=True):
            with st.spinner("Extraindo páginas, gerando hash e indexando chunks..."):
                content_bytes = uploaded_file.read()
                result = api_client.upload_document(uploaded_file.name, content_bytes)
                if result:
                    st.success(f"Documento '{result['filename']}' ({result['document_type']}) processado com sucesso!")
                    st.session_state["selected_doc_id"] = result["id"]
                    st.rerun()
                else:
                    st.error("Falha ao processar o documento via API.")

with col_right:
    st.subheader(" Entrada Rápida de Texto Fiscal (Simulador)")
    sim_filename = st.text_input("Identificador do Documento:", value="AIIM_Simulado_Teste.txt")
    sim_text = st.text_area(
        "Texto bruto fiscal:",
        height=140,
        placeholder="Ex.: AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA\nAUTUADO: EMPRESA MODELO S.A.\nCNPJ: 00.123.456/0001-99\nICMS R$ 250.000,00...",
    )
    if st.button(" Ingerir Texto Bruto", use_container_width=True):
        if sim_text.strip():
            with st.spinner("Ingerindo e extraindo entidades..."):
                res = api_client.intake_text_document(sim_filename, sim_text)
                if res:
                    st.success("Texto ingerido com sucesso!")
                    st.session_state["selected_doc_id"] = res["id"]
                    st.rerun()
                else:
                    st.error("Erro ao enviar texto.")
        else:
            st.warning("Insira o texto antes de enviar.")

st.divider()

# Documents Table
st.subheader(" Catálogo de Documentos Fiscais Analisados")

filter_type = st.selectbox(
    "Filtrar por Tipo Documental:",
    ["TODOS", "AIIM", "NL", "COSIT", "DARF", "CND", "OUTRO"],
)

docs = api_client.list_documents(doc_type=filter_type)

if not docs:
    st.info("Nenhum documento encontrado. Utilize o botão acima para carregar ou execute o script de seed.")
else:
    table_data = []
    for d in docs:
        table_data.append(
            {
                "ID": d["id"][:8] + "...",
                "Arquivo": d["filename"],
                "Tipo": d["document_type"],
                "Páginas": d["total_pages"],
                "Tamanho (KB)": round(d["file_size_bytes"] / 1024, 1),
                "Status": d["status"],
                "Data de Cadastro": d["created_at"][:10],
            }
        )
    st.dataframe(table_data, use_container_width=True)

    # Fast document selector
    doc_options = {f"{d['filename']} ({d['document_type']}) - ID: {d['id'][:8]}": d["id"] for d in docs}
    chosen = st.selectbox("Selecione um documento para detalhar:", list(doc_options.keys()))
    if st.button(" Abrir no Visualizador"):
        st.session_state["selected_doc_id"] = doc_options[chosen]
        st.switch_page("pages/1_Visualizador_e_Extracao.py")
