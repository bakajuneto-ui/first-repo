"""Admin – Deep analytics: subject averages, section comparisons, toppers."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from components.ui import section_header, metric_card
from components.charts import bar_section_comparison, scatter_rank_distribution
from utils.database import (
    get_subject_averages, calculate_semester_ranks,
    get_all_students, get_all_teachers
)


def render():
    st.markdown('<div class="page-title">📈 System Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Comprehensive academic performance insights</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Subject Averages",
        "🏆 Rank & Toppers",
        "📉 Section Comparison",
        "🔍 Student Lookup"
    ])

    # ── SUBJECT AVERAGES ──────────────────────────────────────
    with tab1:
        section_header("📊", "Subject-wise Average Marks")
        c1, c2 = st.columns(2)
        with c1:
            sem  = st.selectbox("Quarter", [1,2,3,4], key="aa_sem")
        with c2:
            sec  = st.selectbox("Section (All = system-wide)", ["All","A","B","C","D"], key="aa_sec")

        avgs = get_subject_averages(sem, None if sec=="All" else sec)
        if not avgs:
            st.info("No data available.")
        else:
            fig = go.Figure(go.Bar(
                x=[a["subject_name"] for a in avgs],
                y=[a["avg_marks"] for a in avgs],
                marker_color=[
                    "#10B981" if a["avg_percentage"]>=75 else
                    "#F59E0B" if a["avg_percentage"]>=50 else "#EF4444"
                    for a in avgs
                ],
                text=[f"{a['avg_marks']:.1f}" for a in avgs],
                textposition="outside"
            ))
            fig.update_layout(
                yaxis_range=[0, 110], xaxis_tickangle=-30,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10,r=10,t=20,b=80)
            )
            st.plotly_chart(fig, use_container_width=True)

            df_avg = pd.DataFrame([{
                "Subject": a["subject_name"], "Avg Marks": f"{a['avg_marks']:.1f}",
                "Avg %": f"{a['avg_percentage']:.1f}%", "Students": a["count"]
            } for a in avgs])
            st.dataframe(df_avg, use_container_width=True, hide_index=True)

    # ── RANK & TOPPERS ────────────────────────────────────────
    with tab2:
        section_header("🏆", "Quarter Toppers & Rank Distribution")
        c1, c2 = st.columns(2)
        with c1:
            sem2 = st.selectbox("Quarter", [1,2,3,4], key="rank_sem2")
        with c2:
            sec2 = st.selectbox("Section", ["All","A","B","C","D"], key="rank_sec2")

        ranks = calculate_semester_ranks(sem2, None if sec2=="All" else sec2)
        if not ranks:
            st.info("No data.")
        else:
            # Top 3 podium
            st.markdown("### 🎖️ Top 3 Students")
            cols = st.columns(3)
            medals = ["🥇","🥈","🥉"]
            medal_colors = ["#F59E0B","#94A3B8","#CD7F32"]
            for i, (col, medal, color) in enumerate(zip(cols, medals, medal_colors)):
                if i < len(ranks):
                    r = ranks[i]
                    with col:
                        st.markdown(f"""
                        <div style="text-align:center;background:#fff;border-radius:14px;
                                    padding:1.2rem;box-shadow:0 2px 12px rgba(0,0,0,.08);
                                    border-top:4px solid {color}">
                            <div style="font-size:2.5rem">{medal}</div>
                            <div style="font-weight:700;font-size:1rem;color:#1E3A8A">{r['name']}</div>
                            <div style="font-size:.85rem;color:#64748B">Roll: {r['roll_number']}</div>
                            <div style="font-size:1.3rem;font-weight:800;color:{color}">{r['percentage']:.1f}%</div>
                            <div style="font-size:.8rem;color:#64748B">Section {r.get('section','—')}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(scatter_rank_distribution(ranks), use_container_width=True)

            # Full table with download
            df_ranks = pd.DataFrame([{
                "Rank": r["rank"], "Name": r["name"], "Roll": r["roll_number"],
                "Section": r.get("section","—"),
                "Score": f"{r['total_obtained']:.0f}/{r['total_max']}",
                "Percentage": f"{r['percentage']:.2f}%"
            } for r in ranks])
            st.dataframe(df_ranks, use_container_width=True, hide_index=True)

            csv = df_ranks.to_csv(index=False)
            st.download_button("⬇️ Download Ranks CSV", data=csv,
                               file_name=f"ranks_sem{sem2}.csv", mime="text/csv")

    # ── SECTION COMPARISON ────────────────────────────────────
    with tab3:
        section_header("📉", "Section-wise Performance Comparison")
        sem3 = st.selectbox("Quarter", [1,2,3,4], key="comp_sem")
        section_data = {}
        for sec in ["A","B","C","D"]:
            avgs = get_subject_averages(sem3, sec)
            if avgs:
                section_data[sec] = avgs

        if len(section_data) >= 2:
            st.plotly_chart(bar_section_comparison(section_data), use_container_width=True)

            # Radar chart for section-level comparison
            sec_overall = {}
            for sec, avgs in section_data.items():
                sec_overall[sec] = round(
                    sum(a["avg_marks"] for a in avgs) / len(avgs), 2
                )

            fig_r = go.Figure()
            cats = list(next(iter(section_data.values()), [{}]))
            sub_names = [a["subject_name"] for a in next(iter(section_data.values()), [])]
            if sub_names:
                sub_names_closed = sub_names + [sub_names[0]]
                colors_r = ["#1E3A8A","#10B981","#F59E0B","#EF4444"]
                for i, (sec, avgs) in enumerate(section_data.items()):
                    vals = [a["avg_marks"] for a in avgs] + [avgs[0]["avg_marks"]]
                    fig_r.add_trace(go.Scatterpolar(
                        r=vals, theta=sub_names_closed,
                        fill="toself", name=f"Section {sec}",
                        line_color=colors_r[i],
                        opacity=0.7
                    ))
                fig_r.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                    title="Section Radar – Subject Averages",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20,r=20,t=50,b=20)
                )
                st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("Need at least 2 sections with data for comparison.")

        # Section summary table
        st.markdown("#### Section Overall Averages")
        rows_s = []
        for sec, avgs in section_data.items():
            overall = round(sum(a["avg_marks"] for a in avgs)/len(avgs), 2) if avgs else 0
            rows_s.append({"Section": sec, "Avg Marks": f"{overall:.2f}",
                           "Subjects": len(avgs)})
        if rows_s:
            st.dataframe(pd.DataFrame(rows_s), use_container_width=True, hide_index=True)

    # ── STUDENT LOOKUP ────────────────────────────────────────
    with tab4:
        section_header("🔍", "Individual Student Lookup")

        students_all = get_all_students()
        if not students_all:
            st.info("No students.")
            return

        search_q = st.text_input("Search by name or roll number", key="admin_lookup_search")
        filtered = students_all
        if search_q:
            q = search_q.lower()
            filtered = [s for s in students_all
                        if q in s.get("name","").lower() or q in s.get("roll_number","").lower()]

        if not filtered:
            st.info("No students match your search.")
            return

        stu_map = {f"{s['name']} ({s['roll_number']}) – Sec {s.get('section','')}": s
                   for s in filtered}
        chosen = st.selectbox("Select Student", list(stu_map.keys()), key="admin_stu_lookup")
        stu    = stu_map[chosen]

        from utils.database import calculate_student_analytics
        from components.charts import pie_subject_performance, bar_subject_marks

        sem_l = st.selectbox("Quarter", [1,2,3,4], key="admin_lookup_sem")
        analytics = calculate_student_analytics(stu["student_id"], sem_l)

        if not analytics or not analytics["marks"]:
            st.info(f"No marks data for {stu['name']} in Quarter {sem_l}.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Percentage",   f"{analytics['percentage']:.2f}%")
            c2.metric("Total",        f"{analytics['total_obtained']:.0f}/{analytics['total_max']}")
            c3.metric("Subjects",     len(analytics["marks"]))

            col_p, col_b = st.columns(2)
            with col_p:
                st.plotly_chart(pie_subject_performance(analytics["marks"]), use_container_width=True)
            with col_b:
                st.plotly_chart(bar_subject_marks(analytics["marks"], stu["name"]), use_container_width=True)