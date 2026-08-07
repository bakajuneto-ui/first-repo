"""Student Dashboard – overview of performance."""
import streamlit as st
from components.ui import metric_card, section_header, progress_bar, grade_badge
from components.charts import pie_subject_performance, bar_subject_marks
from utils.database import calculate_student_analytics, calculate_semester_ranks


def render():
    user = st.session_state.user_data
    stu_id   = user.get("student_id", "")
    stu_name = user.get("name", "Student")
    section  = user.get("section", "A")

    # ── Page header ──────────────────────────────────────────
    st.markdown(f"""
    <div class="page-title">👋 Welcome, {stu_name}!</div>
    <div class="page-subtitle">Section {section} · Roll No. {user.get('roll_number','—')} · MCA Program</div>
    """, unsafe_allow_html=True)

    # ── Quarter selector ────────────────────────────────────
    sem = st.selectbox("📅 Select Quarter", [1, 2, 3, 4], index=0, key="dash_sem")

    analytics = calculate_student_analytics(stu_id, sem)
    ranks      = calculate_semester_ranks(sem, section)

    my_rank = next((r for r in ranks if r["student_id"] == stu_id), None)

    # ── KPI cards ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pct = analytics["percentage"] if analytics else 0
        metric_card("Overall %", f"{pct}%", "This quarter",
                    "green" if pct >= 75 else "orange" if pct >= 50 else "red")
    with col2:
        rank_val = my_rank["rank"] if my_rank else "—"
        metric_card("Quarter Rank", f"#{rank_val}", f"Out of {len(ranks)} students", "blue" if rank_val == "—" or int(rank_val) > 3 else "green")
    with col3:
        subj_count = len(analytics["marks"]) if analytics else 0
        metric_card("Subjects", subj_count, f"Quarter {sem}")
    with col4:
        total = f"{analytics['total_obtained']:.0f}/{analytics['total_max']}" if analytics else "—"
        metric_card("Total Marks", total, "Aggregate")

    st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)

    if not analytics or not analytics["marks"]:
        st.info("📭 No marks data found for this quarter.")
        return

    # ── Charts ───────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(pie_subject_performance(analytics["marks"]), use_container_width=True)
    with col_b:
        st.plotly_chart(bar_subject_marks(analytics["marks"], stu_name), use_container_width=True)

    # ── Marks table ──────────────────────────────────────────
    section_header("📋", "Subject-wise Marks", f"Quarter {sem}")
    rows_html = ""
    for m in sorted(analytics["marks"], key=lambda x: x["subject_name"]):
        pct_s = round((m["marks_obtained"] / m.get("max_marks", 100)) * 100, 1)
        badge = grade_badge(pct_s)
        rows_html += f"""
        <tr>
            <td>{m['subject_name']}</td>
            <td style="text-align:center">{m['marks_obtained']:.0f} / {m.get('max_marks',100)}</td>
            <td style="text-align:center">{pct_s}%</td>
            <td style="text-align:center">{badge}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)">
        <thead>
            <tr style="background:#1E3A8A;color:#fff;">
                <th style="padding:.75rem 1rem;text-align:left">Subject</th>
                <th style="padding:.75rem 1rem;text-align:center">Marks</th>
                <th style="padding:.75rem 1rem;text-align:center">Percentage</th>
                <th style="padding:.75rem 1rem;text-align:center">Grade</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)