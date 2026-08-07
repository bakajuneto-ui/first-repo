"""Student – All Marks view."""
import streamlit as st
import pandas as pd
from components.ui import section_header, grade_badge
from utils.database import calculate_student_analytics


def render():
    user   = st.session_state.user_data
    stu_id = user.get("student_id", "")

    st.markdown('<div class="page-title">📊 My Marks</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Complete marks record across all quarters</div>',
                unsafe_allow_html=True)

    tabs = st.tabs(["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"])

    for i, tab in enumerate(tabs):
        sem = i + 1
        with tab:
            analytics = calculate_student_analytics(stu_id, sem)
            if not analytics or not analytics["marks"]:
                st.info(f"No data for Quarter {sem}")
                continue

            # Summary row
            pct = analytics["percentage"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Marks", f"{analytics['total_obtained']:.0f} / {analytics['total_max']}")
            col2.metric("Percentage",  f"{pct:.2f}%")
            col3.metric("Subjects",    len(analytics["marks"]))

            st.markdown("<br>", unsafe_allow_html=True)

            # Table
            rows = []
            for m in sorted(analytics["marks"], key=lambda x: x["subject_name"]):
                pct_s = round((m["marks_obtained"] / m.get("max_marks", 100)) * 100, 1)
                rows.append({
                    "Subject":       m["subject_name"],
                    "Marks Obtained": f"{m['marks_obtained']:.0f}",
                    "Max Marks":     m.get("max_marks", 100),
                    "Percentage":    f"{pct_s}%",
                    "Grade":         ("A+" if pct_s>=90 else "A" if pct_s>=80 else "B" if pct_s>=70 else
                                      "C" if pct_s>=60 else "D" if pct_s>=50 else "F"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
