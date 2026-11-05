import streamlit as st
from utils import get_dashboard_metrics, get_health

st.set_page_config(
    page_title="LexEval | AI Quality & Evaluation Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ LexEval — Continuous AI Evaluation & Quality Monitoring")
st.caption(
    "Plataforma de benchmarking contínuo, verificação de fidelidade fática, detecção de alucinações "
    "e observabilidade para IA Jurídica."
)

health = get_health()
if health.get("status") == "healthy":
    st.sidebar.success("🟢 API Conectada (Port 8001)")
else:
    st.sidebar.warning(f"⚠️ API Offline / Inacessível: {health.get('status')}")

st.sidebar.markdown("---")
st.sidebar.info(
    "**Navegação:**\n"
    "- 📊 **Dashboard Geral** (Home)\n"
    "- 🚀 **Executar Avaliação**\n"
    "- 🔍 **Comparador A/B**\n"
    "- 🚨 **Catálogo de Falhas**\n"
    "- 📚 **Golden Datasets**"
)

metrics = get_dashboard_metrics()

if not metrics or metrics.get("total_runs", 0) == 0:
    st.info(
        "Nenhuma execução de avaliação registrada no momento. "
        "Acesse a página **'1_Executar_Avaliacao'** para disparar um benchmark ou execute o script de seed."
    )
else:
    # 1. KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label="Taxa de Aprovação Global",
            value=f"{metrics.get('avg_pass_rate', 0.0) * 100:.1f}%",
        )
    with col2:
        st.metric(
            label="Fidelidade Média (Context)",
            value=f"{metrics.get('avg_faithfulness', 0.0) * 100:.1f}%",
        )
    with col3:
        st.metric(
            label="Relevância Média",
            value=f"{metrics.get('avg_relevance', 0.0) * 100:.1f}%",
        )
    with col4:
        st.metric(
            label="Total de Avaliações",
            value=metrics.get("total_cases_evaluated", 0),
        )
    with col5:
        st.metric(
            label="Total de Falhas / Alucinações",
            value=metrics.get("total_failures", 0),
        )

    st.markdown("---")

    # 2. Charts Section
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.subheader("📈 Histórico de Qualidade por Execução")
        recent_runs = metrics.get("recent_runs", [])
        if recent_runs:
            chart_data = []
            for idx, r in enumerate(reversed(recent_runs)):
                chart_data.append(
                    {
                        "Run": f"#{idx+1} {r.get('model_name', '')[:12]}",
                        "Pass Rate": r.get("pass_rate", 0.0) * 100,
                        "Fidelidade": r.get("avg_faithfulness", 0.0) * 100,
                        "Relevância": r.get("avg_relevance", 0.0) * 100,
                    }
                )
            st.line_chart(chart_data, x="Run", y=["Pass Rate", "Fidelidade", "Relevância"])
        else:
            st.write("Sem dados de séries temporais.")

    with right_col:
        st.subheader("🚨 Distribuição de Falhas")
        failures_by_reason = metrics.get("failures_by_reason", {})
        if failures_by_reason:
            st.bar_chart(failures_by_reason)
        else:
            st.success("🎉 Nenhuma falha crítica detectada nas execuções recentes!")

    st.markdown("---")

    # 3. Recent Runs Table
    st.subheader("📋 Execuções Recentes de Benchmark")
    if recent_runs:
        table_rows = []
        for r in recent_runs:
            table_rows.append(
                {
                    "ID": r.get("id")[:8] + "...",
                    "Dataset": r.get("dataset_name") or r.get("dataset_id")[:8],
                    "Modelo / Prompt": r.get("model_name"),
                    "Casos": f"{r.get('passed_cases')}/{r.get('total_cases')}",
                    "Pass Rate": f"{r.get('pass_rate', 0.0) * 100:.1f}%",
                    "Fidelidade": f"{r.get('avg_faithfulness', 0.0) * 100:.1f}%",
                    "Status": r.get("status"),
                    "Duração (ms)": f"{r.get('duration_ms', 0):.0f}",
                }
            )
        st.dataframe(table_rows, use_container_width=True)
