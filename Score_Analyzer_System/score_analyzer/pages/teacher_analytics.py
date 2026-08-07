"""Teacher – Subject analytics."""
import streamlit as st
import plotly.graph_objects as go
from components.ui import metric_card, section_header, teacher_assignment_picker
from utils.database import get_marks_by_subject_section


def render():
    user = st.session_state.user_data
    t_id = user.get("teacher_id", "")

    st.markdown('<div class="page-title">📊 Subject Analytics</div>', unsafe_allow_html=True)

    assignment = teacher_assignment_picker(t_id)
    if not assignment:
        return

    sub_code = assignment["subject_code"]
    sub_name = assignment["subject_name"]
    section  = assignment["section"]
    sem      = assignment["semester"]
    max_m    = assignment.get("max_marks", 100)

    st.markdown(f'<div class="page-subtitle"><b>{sub_name}</b> · Section <b>{section}</b></div>',
                unsafe_allow_html=True)

    marks = get_marks_by_subject_section(sub_code, section, sem)
    if not marks:
        st.info("No marks data yet.")
        return

    vals = [m["marks_obtained"] for m in marks]
    avg  = round(sum(vals)/len(vals), 2)
    high = max(vals); low = min(vals)
    pass_pct = round(len([v for v in vals if v >= 40]) / len(vals) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Average",    f"{avg:.1f}", f"Class avg / {max_m}")
    with c2: metric_card("Highest",    f"{high:.0f}", "Top score", "green")
    with c3: metric_card("Lowest",     f"{low:.0f}",  "Min score", "red")
    with c4: metric_card("Pass Rate",  f"{pass_pct}%", "≥40 marks", "green" if pass_pct>=80 else "orange")

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribution histogram
    section_header("📊", "Marks Distribution")
    fig = go.Figure(go.Histogram(
        x=vals, nbinsx=10,
        marker_color="#3B82F6",
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>"
    ))
    fig.update_layout(
        xaxis_title="Marks Obtained", yaxis_title="Number of Students",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.1, margin=dict(l=20,r=20,t=20,b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Grade distribution pie
    grade_map = {"A+": 0,"A": 0,"B": 0,"C": 0,"D": 0,"F": 0}
    for v in vals:
        p = (v/max_m)*100
        g = "A+" if p>=90 else "A" if p>=80 else "B" if p>=70 else "C" if p>=60 else "D" if p>=50 else "F"
        grade_map[g] += 1

    fig2 = go.Figure(go.Pie(
        labels=list(grade_map.keys()),
        values=list(grade_map.values()),
        hole=.4,
        marker_colors=["#10B981","#3B82F6","#60A5FA","#F59E0B","#FB923C","#EF4444"],
    ))
    fig2.update_layout(title_text="Grade Distribution",
                       paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig2, use_container_width=True)