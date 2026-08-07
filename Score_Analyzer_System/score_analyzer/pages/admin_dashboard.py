"""Admin – Main dashboard with system overview."""
import streamlit as st
import plotly.graph_objects as go
from components.ui import metric_card, section_header
from components.charts import donut_section_counts, bar_section_comparison
from utils.database import (
    get_admin_overview, get_subject_averages, calculate_semester_ranks
)


def render():
    st.markdown('<div class="page-title">👩‍💼 Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">System-wide overview and analytics</div>',
                unsafe_allow_html=True)

    overview = get_admin_overview()

    # ── KPI row ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Students", overview["total_students"], "Enrolled")
    with c2: metric_card("Total Teachers", overview["total_teachers"], "Faculty")
    with c3: metric_card("Mark Records",   overview["total_marks"],    "Entries")
    with c4: metric_card("Sections",       4,                          "A, B, C, D")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section distribution + semester rank distribution ────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(donut_section_counts(overview["section_counts"]), use_container_width=True)

    with col2:
        sem = st.selectbox("Quarter for Rank Chart", [1,2,3,4], key="admin_sem_rank")
        ranks = calculate_semester_ranks(sem)
        if ranks:
            fig = go.Figure(go.Bar(
                x=[r["name"] for r in ranks[:10]],
                y=[r["percentage"] for r in ranks[:10]],
                marker_color="#3B82F6",
                text=[f"{r['percentage']:.1f}%" for r in ranks[:10]],
                textposition="outside"
            ))
            fig.update_layout(
                title_text=f"Top 10 Students – Quarter {sem}",
                yaxis_range=[0, 110],
                xaxis_tickangle=-30,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=40, b=60)
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Subject averages across sections ─────────────────────
    section_header("📊", "Subject Averages by Section")
    sem2 = st.selectbox("Quarter", [1,2,3,4], key="admin_sub_avg_sem")
    section_data = {}
    for sec in ["A","B","C","D"]:
        avgs = get_subject_averages(sem2, sec)
        if avgs:
            section_data[sec] = avgs

    if len(section_data) >= 2:
        st.plotly_chart(bar_section_comparison(section_data), use_container_width=True)
    else:
        for sec, avgs in section_data.items():
            st.write(f"**Section {sec}**")
            import pandas as pd
            st.dataframe(pd.DataFrame(avgs)[["subject_name","avg_marks","avg_percentage"]],
                         use_container_width=True, hide_index=True)
