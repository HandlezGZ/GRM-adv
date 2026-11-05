import pandas as pd
import streamlit as st
from utils import get_health, list_failures

st.set_page_config(page_title="Qualidade e Falhas | LexFlow", page_icon="🛡️", layout="wide")

st.title("🛡️ Qualidade, Resiliência e Auditoria de Falhas")
st.caption(
    "Monitoramento de falhas de provedores de IA, timeouts e rastreabilidade de fallback determinístico."
)

# Health Indicator
health = get_health()
c1, c2, c3 = st.columns(3)
c1.metric(
    "Status da API",
    "Operacional" if health else "Indisponível",
    delta="Online" if health else "Offline",
)
c2.metric("Modo Configurado", health.get("classification_mode", "N/A") if health else "N/A")
c3.metric("Ambiente", health.get("environment", "N/A") if health else "N/A")

st.divider()

st.subheader("📋 Registro de Falhas do Modelo (Classificação)")

failures = list_failures()

if not failures:
    st.success("🎉 Nenhuma falha de classificação registrada no momento. O sistema está estável!")
else:
    st.warning(f"Foram identificadas **{len(failures)}** tentativa(s) de classificação com erro ou timeout.")

    table_data = []
    for f in failures:
        table_data.append({
            "ID Tentativa": f["id"][:8] + "...",
            "ID Solicitação": f["request_id"],
            "Provedor": f["provider"],
            "Origem": f["source"],
            "Tipo do Erro": f.get("error_type") or "Desconhecido",
            "Duração (ms)": f.get("duration_ms") or "-",
            "Data UTC": f["created_at"][:19].replace("T", " "),
        })

    df_fail = pd.DataFrame(table_data)
    st.dataframe(df_fail, use_container_width=True, hide_index=True)

st.divider()

st.subheader("💡 Como funciona a Política de Fallback no LexFlow?")
st.markdown("""
1. **Zero Downtime:** Quando o provedor LLM (OpenAI ou compatível) sofre timeout, erro de rede ou retorna JSON fora do schema, a requisição **não é descartada**.
2. **Fallback Determinístico Automático:** O sistema aciona instantaneamente o classificador por regras (`RulesClassifier`), que analisa o texto de forma local e segura.
3. **Auditoria Transparente:** O incidente é registrado na entidade `ClassificationAttempt` com status `success=False` e gravado no histórico de eventos da solicitação (`CLASSIFICATION_FAILED`).
4. **Sinalização ao Usuário:** A interface exibe aviso explícito indicando que a classificação foi executada via fallback.
""")
