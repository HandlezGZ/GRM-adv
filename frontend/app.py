import pandas as pd
import streamlit as st
from utils import get_health, get_metrics

st.set_page_config(
    page_title="LexFlow | Automação e Triagem Interna",
    page_icon="⚖️",
    layout="wide",
)

# Header
st.title("⚖️ LexFlow")
st.caption(
    "Sistema de Triagem e Automação de Solicitações Internas"
)

# Health Status Banner
health = get_health()
if health:
    st.success(
        f"🟢 **API Online:** {health.get('service')} v{health.get('version')} "
        f"| Modo: `{health.get('classification_mode')}` "
        f"| Ambiente: `{health.get('environment')}`"
    )
else:
    st.error(
        "🔴 **Backend Offline:** Verifique se o servidor FastAPI está ativo em `http://localhost:8000`."
    )

st.divider()

# Metrics Section
metrics = get_metrics()

if metrics:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de Solicitações", metrics.get("total_requests", 0))
    c2.metric("Em Aberto / Triagem", metrics.get("open_requests", 0))
    c3.metric("Resolvidas", metrics.get("resolved_requests", 0))
    c4.metric("Revisadas por Humano", metrics.get("reviewed_count", 0))
    c5.metric("Falhas de IA Registradas", metrics.get("ai_failure_count", 0))

    if metrics.get("avg_resolution_hours") is not None:
        st.info(f"⏱️ **Tempo Médio de Resolução:** {metrics['avg_resolution_hours']} horas")

    st.subheader("📊 Distribuição Operacional")
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("##### Solicitações por Categoria")
        by_cat = metrics.get("by_category", {})
        if by_cat:
            df_cat = pd.DataFrame(
                list(by_cat.items()), columns=["Categoria", "Quantidade"]
            ).set_index("Categoria")
            st.bar_chart(df_cat)
        else:
            st.info("Nenhuma solicitação categorizada ainda.")

    with col_right:
        st.write("##### Solicitações por Prioridade")
        by_prio = metrics.get("by_priority", {})
        if by_prio:
            df_prio = pd.DataFrame(
                list(by_prio.items()), columns=["Prioridade", "Quantidade"]
            ).set_index("Prioridade")
            st.bar_chart(df_prio)
        else:
            st.info("Nenhum registro de prioridade disponível.")

else:
    st.warning("Não foi possível carregar os dados consolidados do dashboard. Conecte o backend.")

st.divider()

st.markdown("""
### 🧭 Navegação Rápida
- **[Nova Solicitação](/Nova_Solicitacao):** Registre uma demanda operacional interna com validação em tempo real.
- **[Solicitações](/Solicitacoes):** Consulte, busque e filtre todos os chamados cadastrados.
- **[Detalhes e Revisão](/Detalhes_e_Revisao):** Visualize o histórico, altere status e realize a revisão humana ("Human-in-the-loop").
- **[Qualidade e Falhas](/Qualidade_e_Falhas):** Audite incidentes e acompanhe o fallback determinístico da IA.
""")
