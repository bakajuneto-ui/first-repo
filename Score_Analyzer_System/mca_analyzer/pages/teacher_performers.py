"""Teacher – Top / Average / Least performers."""
import streamlit as st
import pandas as pd
from components.ui import section_header, teacher_assignment_picker
from components.charts import bar_performers
from utils.database import get_marks_by_subject_section


def render():
    user = st.session_state.user_data
    t_id = user.get("teacher_id", "")

    st.markdown('<div class="page-title">🏆 Performer Analysis</div>', unsafe_allow_html=True)

    assignment = teacher_assignment_picker(t_id)
    if not assignment:
        return

    sub_code = assignment["subject_code"]
    sub_name = assignment["subject_name"]
    section  = assignment["section"]
    sem      = assignment["semester"]
    max_m    = assignment.get("max_marks", 100)

    st.markdown(f'<div class="page-subtitle"><b>{sub_name}</b> – Section <b>{section}</b></div>',
                unsafe_allow_html=True)

    marks = get_marks_by_subject_section(sub_code, section, sem)
    if not marks:
        st.info("No marks data yet.")
        return

    sorted_marks = sorted(marks, key=lambda x: x["marks_obtained"], reverse=True)
    ranked = [{"name": m["student_name"], "roll": m["roll_number"],
               "marks": m["marks_obtained"], "percentage": round(m["marks_obtained"]/max_m*100,2)}
              for m in sorted_marks]

    top_n  = ranked[:5]
    bot_n  = ranked[-5:][::-1]
    avg_lo = [r for r in ranked if 40 <= r["marks"] < 70][:5]

    tab1, tab2, tab3 = st.tabs(["🥇 Top Performers", "📊 Average Performers", "⚠️ Needs Attention"])

    with tab1:
        st.plotly_chart(bar_performers(top_n, "Top 5 Performers", "#10B981"), use_container_width=True)
        df = pd.DataFrame(top_n)
        df.insert(0, "Rank", range(1, len(df)+1))
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        if avg_lo:
            st.plotly_chart(bar_performers(avg_lo, "Average Performers (40-70)", "#F59E0B"), use_container_width=True)
            st.dataframe(pd.DataFrame(avg_lo), use_container_width=True, hide_index=True)
        else:
            st.info("No students in the 40–70 range.")

    with tab3:
        st.plotly_chart(bar_performers(bot_n, "Bottom 5 Performers", "#EF4444"), use_container_width=True)
        df_bot = pd.DataFrame(bot_n)
        st.dataframe(df_bot, use_container_width=True, hide_index=True)
        if any(r["marks"] < 40 for r in bot_n):
            st.warning("⚠️ Some students scored below 40 – may need additional support.")