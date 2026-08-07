"""Student – Quarter Rank view."""
import streamlit as st
import pandas as pd
from components.ui import section_header
from components.charts import scatter_rank_distribution
from utils.database import calculate_semester_ranks


def render():
    user    = st.session_state.user_data
    stu_id  = user.get("student_id", "")
    section = user.get("section", "A")

    st.markdown('<div class="page-title">🏆 Quarter Rank</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your standing within the section</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sem = st.selectbox("📅 Quarter", [1, 2, 3, 4], key="rank_sem")
    with col2:
        scope = st.selectbox("📍 Scope", ["My Section", "All Sections"], key="rank_scope")

    sec_filter = section if scope == "My Section" else None
    ranks = calculate_semester_ranks(sem, sec_filter)

    my_rank = next((r for r in ranks if r["student_id"] == stu_id), None)

    # Highlight your rank
    if my_rank:
        col1, col2, col3 = st.columns(3)
        col1.metric("Your Rank",       f"#{my_rank['rank']}")
        col2.metric("Your Percentage", f"{my_rank['percentage']:.2f}%")
        col3.metric("Total Students",  len(ranks))

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(scatter_rank_distribution(ranks), use_container_width=True)

    # Full table
    section_header("📋", "Full Rank List")
    rows = []
    for r in ranks:
        medal = "🥇" if r["rank"]==1 else "🥈" if r["rank"]==2 else "🥉" if r["rank"]==3 else ""
        rows.append({
            "Rank":       f"{medal} {r['rank']}",
            "Name":       r["name"] + (" ← You" if r["student_id"]==stu_id else ""),
            "Roll No":    r["roll_number"],
            "Section":    r.get("section","—"),
            "Percentage": f"{r['percentage']:.2f}%",
            "Score":      f"{r['total_obtained']:.0f}/{r['total_max']}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
