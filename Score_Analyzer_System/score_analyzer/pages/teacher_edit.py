"""Teacher – Edit / update individual marks."""
import streamlit as st
from utils.database import (
    get_students_by_section, get_marks_by_subject_section, upsert_mark
)
from components.ui import section_header, teacher_assignment_picker


def render():
    user = st.session_state.user_data
    t_id = user.get("teacher_id", "")

    st.markdown('<div class="page-title">✏️ Edit Marks</div>', unsafe_allow_html=True)

    assignment = teacher_assignment_picker(t_id)
    if not assignment:
        return

    sub_code = assignment["subject_code"]
    sub_name = assignment["subject_name"]
    section  = assignment["section"]
    sem      = assignment["semester"]
    max_m    = assignment.get("max_marks", 100)

    st.markdown(f'<div class="page-subtitle">Update marks for <b>{sub_name}</b> · Section <b>{section}</b></div>',
                unsafe_allow_html=True)

    students = get_students_by_section(section)
    existing = {m["student_id"]: m["marks_obtained"]
                for m in get_marks_by_subject_section(sub_code, section, sem)}

    stu_names = [f"{s['name']} ({s['roll_number']})" for s in students]
    choice    = st.selectbox("👤 Select Student", stu_names, key="edit_stu")
    stu_idx   = stu_names.index(choice)
    stu       = students[stu_idx]
    sid       = stu["student_id"]

    current = existing.get(sid, 0.0)

    section_header("📝", f"Edit marks for {stu['name']}")

    col1, col2 = st.columns([2, 1])
    with col1:
        new_marks = st.number_input(
            f"Marks (out of {max_m})",
            min_value=0.0, max_value=float(max_m),
            value=float(current), step=0.5, key="edit_mark_val"
        )
    with col2:
        st.markdown(f"""
        <div style="padding:1rem;background:#F0F4FF;border-radius:10px;margin-top:1.6rem;">
            <div style="font-size:.8rem;color:#64748B;">Current Marks</div>
            <div style="font-size:1.8rem;font-weight:700;color:#1E3A8A;">{current:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("💾 Update Marks", type="primary"):
        ok, msg = upsert_mark(sid, sub_code, sem, new_marks, max_m)
        if ok:
            st.success(f"✅ Marks updated to {new_marks:.0f} for {stu['name']}")
        else:
            st.error(f"❌ {msg}")