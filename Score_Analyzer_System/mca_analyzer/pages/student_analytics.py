"""Student – Analytics / charts."""
import streamlit as st
from components.ui import section_header
from components.charts import pie_subject_performance, bar_subject_marks
from utils.database import calculate_student_analytics


def render():
    user   = st.session_state.user_data
    stu_id = user.get("student_id", "")

    st.markdown('<div class="page-title">📈 Performance Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visual breakdown of your academic performance</div>',
                unsafe_allow_html=True)

    sem = st.selectbox("📅 Quarter", [1, 2, 3, 4], key="analytics_sem")
    analytics = calculate_student_analytics(stu_id, sem)

    if not analytics or not analytics["marks"]:
        st.info("No marks data for this quarter.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(pie_subject_performance(analytics["marks"]), use_container_width=True)
    with col2:
        st.plotly_chart(bar_subject_marks(analytics["marks"]), use_container_width=True)

    # Quarter comparison
    section_header("📊", "Quarter-wise Percentage Trend")
    import plotly.graph_objects as go
    sems, pcts = [], []
    for s in [1, 2, 3, 4]:
        a = calculate_student_analytics(stu_id, s)
        if a:
            sems.append(f"Quarter {s}")
            pcts.append(a["percentage"])

    if len(sems) > 1:
        fig = go.Figure(go.Scatter(
            x=sems, y=pcts, mode="lines+markers+text",
            text=[f"{p:.1f}%" for p in pcts],
            textposition="top center",
            line=dict(color="#1E3A8A", width=3),
            marker=dict(size=10, color="#3B82F6")
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 105], title="Percentage (%)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
