"""Teacher – Dashboard overview."""
import streamlit as st
from components.ui import metric_card, section_header, teacher_assignment_picker
from utils.database import get_marks_by_subject_section, get_students_by_section


def render():
    user   = st.session_state.user_data
    t_name = user.get("name", "Teacher")
    t_id   = user.get("teacher_id", "")

    st.markdown(f'<div class="page-title">👩‍🏫 {t_name}</div>', unsafe_allow_html=True)

    assignment = teacher_assignment_picker(t_id)
    if not assignment:
        return  # picker already showed the "no assignments" warning

    sub_code = assignment["subject_code"]
    sub_name = assignment["subject_name"]
    section  = assignment["section"]
    sem      = assignment["semester"]

    st.markdown(f'<div class="page-subtitle">Subject: <b>{sub_name}</b> · Section: <b>{section}</b> · Quarter: <b>{sem}</b></div>',
                unsafe_allow_html=True)

    marks = get_marks_by_subject_section(sub_code, section, sem)
    students = get_students_by_section(section)

    total_students = len(students)
    entered_marks  = len(marks)
    avg_marks = round(sum(m["marks_obtained"] for m in marks)/len(marks), 2) if marks else 0
    topper = max(marks, key=lambda x: x["marks_obtained"]) if marks else None

    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card("Section Students", total_students, f"Section {section}")
    with col2: metric_card("Marks Entered",    entered_marks,  f"of {total_students}", "green" if entered_marks==total_students else "orange")
    with col3: metric_card("Class Average",    f"{avg_marks:.1f}", f"/{100}", "green" if avg_marks>=75 else "orange")
    with col4: metric_card("Topper",           topper["student_name"] if topper else "—", f"{topper['marks_obtained']:.0f}/100" if topper else "", "green")

    st.markdown("<br>", unsafe_allow_html=True)

    section_header("📋", "Mark Entry Status", f"{sub_name} – Section {section}")
    for stu in students:
        sid = stu["student_id"]
        m = next((x for x in marks if x["student_id"]==sid), None)
        status = f"✅ {m['marks_obtained']:.0f}/100" if m else "⏳ Pending"
        st.markdown(f"**{stu['name']}** ({stu['roll_number']}) — {status}")

    # Bonus: show this teacher's full workload across all assignments,
    # proving the many-to-many at a glance.
    from utils.database import get_teacher_assignments, get_students_taught_by_teacher
    all_assignments = get_teacher_assignments(t_id)
    all_students = get_students_taught_by_teacher(t_id)
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📊", "Your Full Teaching Load")
    st.caption(f"{len(all_assignments)} assignment(s) across {len(all_students)} distinct student(s)")
    for a in all_assignments:
        st.markdown(f"- **{a['subject_name']}** — Section {a['section']} (Sem {a['semester']})")