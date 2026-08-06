"""Admin – Add / Update / Delete students."""
import streamlit as st
import pandas as pd
import uuid
from components.ui import section_header
from utils.database import (
    get_all_students, add_student, update_student, delete_student
)


def render():
    st.markdown('<div class="page-title">👥 Student Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Add, update, or remove student records</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add Student", "✏️ Edit / Delete"])

    # ── VIEW ALL ─────────────────────────────────────────────
    with tab1:
        section_header("📋", "All Students")

        col1, col2 = st.columns(2)
        with col1:
            sec_filter = st.selectbox("Filter by Section", ["All","A","B","C","D"], key="stu_sec_filter")
        with col2:
            search = st.text_input("🔍 Search by name / roll", key="stu_search")

        students = get_all_students()
        if sec_filter != "All":
            students = [s for s in students if s.get("section") == sec_filter]
        if search:
            q = search.lower()
            students = [s for s in students
                        if q in s.get("name","").lower() or q in s.get("roll_number","").lower()]

        if students:
            rows = [{
                "Student ID":  s.get("student_id",""),
                "Name":        s.get("name",""),
                "Username":    s.get("username",""),
                "Roll No":     s.get("roll_number",""),
                "Section":     s.get("section",""),
                "Year":        s.get("year",""),
                "Quarter":     s.get("semester",""),
                "Email":       s.get("email",""),
            } for s in students]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(students)} student(s)")
        else:
            st.info("No students found.")

    # ── ADD STUDENT ───────────────────────────────────────────
    with tab2:
        section_header("➕", "Add New Student")

        with st.form("add_student_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name     = st.text_input("Full Name *")
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                roll     = st.text_input("Roll Number *")
            with c2:
                section  = st.selectbox("Section *", ["A","B","C","D"])
                year     = st.selectbox("Year *", [1, 2])
                semester = st.selectbox("Quarter *", [1, 2, 3, 4])
                email    = st.text_input("Email")
            submitted = st.form_submit_button("➕ Add Student", type="primary", use_container_width=True)
            if submitted:
                if not all([name, username, password, roll]):
                    st.error("Please fill all required (*) fields.")
                else:
                    ok, msg = add_student({
                        "student_id":  f"STU{uuid.uuid4().hex[:6].upper()}",
                        "name":        name.strip(),
                        "username":    username.strip(),
                        "password":    password,
                        "roll_number": roll.strip(),
                        "section":     section,
                        "year":        year,
                        "semester":    semester,
                        "email":       email.strip(),
                    })
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

    # ── EDIT / DELETE ─────────────────────────────────────────
    with tab3:
        section_header("✏️", "Edit or Delete Student")

        students_all = get_all_students()
        if not students_all:
            st.info("No students in the system.")
        else:
            stu_map = {f"{s['name']} ({s['roll_number']})": s for s in students_all}
            choice  = st.selectbox("Select Student", list(stu_map.keys()), key="edit_stu_select")
            stu     = stu_map[choice]

            with st.form("edit_student_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name    = st.text_input("Full Name",    value=stu.get("name",""))
                    new_username= st.text_input("Username",     value=stu.get("username",""))
                    new_password= st.text_input("New Password (leave blank to keep)", type="password")
                    new_roll    = st.text_input("Roll Number",  value=stu.get("roll_number",""))
                with c2:
                    new_section = st.selectbox("Section", ["A","B","C","D"],
                                               index=["A","B","C","D"].index(stu.get("section","A")))
                    new_year    = st.selectbox("Year", [1,2],
                                               index=[1,2].index(stu.get("year",1)))
                    new_semester= st.selectbox("Quarter", [1,2,3,4],
                                               index=[1,2,3,4].index(stu.get("semester",1)))
                    new_email   = st.text_input("Email", value=stu.get("email",""))

                col_save, col_del = st.columns(2)
                with col_save:
                    save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with col_del:
                    delete = st.form_submit_button("🗑️ Delete Student", use_container_width=True)

                if save:
                    updates = {
                        "name":        new_name,
                        "username":    new_username,
                        "roll_number": new_roll,
                        "section":     new_section,
                        "year":        new_year,
                        "semester":    new_semester,
                        "email":       new_email,
                    }
                    if new_password:
                        updates["password"] = new_password
                    ok, msg = update_student(stu["student_id"], updates)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

                if delete:
                    ok, msg = delete_student(stu["student_id"])
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                    if ok:
                        st.rerun()
