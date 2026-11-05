import streamlit as st

from frontend.api_client import api_client

st.set_page_config(page_title="Chat Fundamentado | LexTax", page_icon="💬", layout="wide")

st.title("💬 Consulta Interativa com Fontes Obrigatórias")
st.caption("Q&A ancorado estritamente no documento fiscal. Cada resposta apresenta trechos verbatim e número da página de suporte.")

docs = api_client.list_documents()
if not docs:
    st.warning("Nenhum documento cadastrado. Por favor, adicione um documento na página inicial.")
    st.stop()

doc_map = {f"{d['filename']} ({d['document_type']}) - {d['id'][:8]}": d["id"] for d in docs}
default_idx = 0
selected_id = st.session_state.get("selected_doc_id")
if selected_id:
    for i, (k, v) in enumerate(doc_map.items()):
        if v == selected_id:
            default_idx = i
            break

chosen = st.selectbox("Documento Fiscal Ativo:", list(doc_map.keys()), index=default_idx)
doc_id = doc_map[chosen]
st.session_state["selected_doc_id"] = doc_id

# Manage chat session ID per document in session state
session_key = f"chat_session_{doc_id}"
if session_key not in st.session_state:
    # Create or retrieve session
    new_sess = api_client.create_chat_session(doc_id, title=f"Chat - {chosen}")
    if new_sess:
        st.session_state[session_key] = new_sess["id"]

active_session_id = st.session_state.get(session_key)

# Suggested questions
st.markdown("##### 💡 Sugestões de Perguntas Rápidas:")
sug_col1, sug_col2, sug_col3, sug_col4 = st.columns(4)
selected_query = None

with sug_col1:
    if st.button("Qual o valor total e multas?", use_container_width=True):
        selected_query = "Qual o valor total da autuação e multas cobradas?"
with sug_col2:
    if st.button("Qual a tese fiscal de acusação?", use_container_width=True):
        selected_query = "Qual a tese fiscal de autuação e fatos apurados?"
with sug_col3:
    if st.button("Quais leis foram infringidas?", use_container_width=True):
        selected_query = "Quais artigos de lei e regulamento foram infringidos?"
with sug_col4:
    if st.button("Qual o prazo para impugnação?", use_container_width=True):
        selected_query = "Qual o prazo para defesa ou impugnação administrativa?"

st.divider()

# Display Chat History
if active_session_id:
    history = api_client.get_chat_history(active_session_id)
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            citations = msg.get("citations") or []
            if citations and msg["role"] == "assistant":
                with st.expander(f"📚 Fontes e Citações Verbatim do Documento ({len(citations)} trechos localizados)"):
                    for idx, cit in enumerate(citations, start=1):
                        st.markdown(
                            f"""
                            **Trecho #{idx} — Página {cit.get('page_number', 1)}**
                            *(Relevância: {cit.get('relevance_score', 1.0)})*
                            > *\"{cit.get('verbatim_excerpt')}\"*
                            """
                        )

# Input for new message
user_input = st.chat_input("Digite sua dúvida sobre o documento fiscal...")
query_to_send = selected_query or user_input

if query_to_send and active_session_id:
    with st.chat_message("user"):
        st.markdown(query_to_send)

    with st.spinner("Buscando evidências documentais e verificando ancoragem..."):
        response = api_client.query_chat_session(active_session_id, query_to_send)
        if response:
            with st.chat_message("assistant"):
                st.markdown(response["answer"])
                citations = response.get("citations") or []
                if citations:
                    with st.expander(f"📚 Fontes e Citações Verbatim ({len(citations)} trechos localizados)"):
                        for idx, cit in enumerate(citations, start=1):
                            st.markdown(
                                f"""
                                **Trecho #{idx} — Página {cit.get('page_number', 1)}**
                                *(Relevância: {cit.get('relevance_score', 1.0)})*
                                > *\"{cit.get('verbatim_excerpt')}\"*
                                """
                            )
            st.rerun()
        else:
            st.error("Erro ao consultar o assistente.")
