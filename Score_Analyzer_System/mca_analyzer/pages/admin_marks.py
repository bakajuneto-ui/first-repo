"""Admin – View all student marks in table form."""
import streamlit as st
import pandas as pd
from components.ui import section_header
from utils.database import (
    get_students_by_section, calculate_student_analytics,
    calculate_semester_ranks, get_all_subjects, get_mark
)


def render():
    st.markdown('<div class="page-title">📊 All Marks Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Complete marks record – section & quarter view</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        section = st.selectbox("📍 Section", ["A","B","C","D"], key="marks_sec")
    with col2:
        semester = st.selectbox("📅 Quarter", [1,2,3,4], key="marks_sem")
    with col3:
        view_type = st.selectbox("👁️ View", ["Subject-wise Table", "Rank Table"], key="marks_view")

    students = get_students_by_section(section)
    subjects  = [s for s in get_all_subjects() if s["semester"] == semester]

    if not students:
        st.info("No students in this section.")
        return

    if view_type == "Subject-wise Table":
        section_header("📋", f"Section {section} – Quarter {semester} Marks")

        # Build wide table: rows=students, cols=subjects
        rows = []
        for stu in students:
            sid  = stu["student_id"]
            row  = {"Name": stu["name"], "Roll No": stu["roll_number"]}
            tot_obt = 0; tot_max = 0
            for sub in subjects:
                m = get_mark(sid, sub["code"], semester)
                val = m["marks_obtained"] if m else "—"
                row[sub["name"]] = val if val == "—" else f"{val:.0f}"
                if val != "—":
                    tot_obt += val
                    tot_max += m.get("max_marks", 100)
            row["Total"]  = f"{tot_obt:.0f}/{tot_max}" if tot_max else "—"
            row["Pct %"]  = f"{tot_obt/tot_max*100:.1f}%" if tot_max else "—"
            rows.append(row)

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Download
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"marks_section{section}_sem{semester}.csv",
            mime="text/csv"
        )

    else:  # Rank Table
        section_header("🏆", f"Rank Table – Section {section} Quarter {semester}")
        ranks = calculate_semester_ranks(semester, section)
        if not ranks:
            st.info("No marks data yet for ranking.")
            return

        rows = []
        for r in ranks:
            medal = "🥇" if r["rank"]==1 else "🥈" if r["rank"]==2 else "🥉" if r["rank"]==3 else ""
            rows.append({
                "Rank":       f"{medal} {r['rank']}",
                "Name":       r["name"],
                "Roll No":    r["roll_number"],
                "Total":      f"{r['total_obtained']:.0f}/{r['total_max']}",
                "Percentage": f"{r['percentage']:.2f}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Topper highlight
        if ranks:
            topper = ranks[0]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#F59E0B,#FCD34D);
                        border-radius:14px;padding:1.2rem 1.5rem;margin-top:1rem;
                        display:flex;align-items:center;gap:1rem;">
                <span style="font-size:2.5rem">🏆</span>
                <div>
                    <div style="font-weight:800;font-size:1.1rem;color:#1E3A8A">
                        Topper: {topper['name']}
                    </div>
                    <div style="color:#92400E;font-size:.9rem">
                        Roll: {topper['roll_number']} · {topper['percentage']:.2f}% · Rank #1
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)