"""Admin – Add / Update / Delete teachers, manage many-to-many assignments."""
import streamlit as st
import pandas as pd
import uuid
from components.ui import section_header
from utils.database import (
    get_all_teachers, add_teacher, update_teacher, delete_teacher,
    get_all_subjects, get_teacher_assignments,
    assign_subject_to_teacher, unassign_subject_from_teacher
)


def render():
    st.markdown('<div class="page-title">👩‍🏫 Teacher Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage faculty and their subject/section assignments</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Add Teacher", "✏️ Edit / Delete", "🔗 Manage Assignments"])

    # ── VIEW ALL ─────────────────────────────────────────────
    with tab1:
        section_header("📋", "All Teachers")
        teachers = get_all_teachers()

        if teachers:
            rows = []
            for t in teachers:
                assignments = get_teacher_assignments(t["teacher_id"])
                summary = ", ".join(f"{a['subject_name']} ({a['section']})" for a in assignments) or "— none —"
                rows.append({
                    "Teacher ID": t.get("teacher_id",""),
                    "Name":       t.get("name",""),
                    "Username":   t.get("username",""),
                    "Assignments": summary,
                    "Email":      t.get("email",""),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption(f"{len(teachers)} teacher(s) registered")
        else:
            st.info("No teachers found.")

    # ── ADD TEACHER ───────────────────────────────────────────
    with tab2:
        section_header("➕", "Add New Teacher")
        st.caption("Create the teacher first, then assign subjects/sections in the 'Manage Assignments' tab.")

        with st.form("add_teacher_form", clear_on_submit=True):
            name     = st.text_input("Full Name *")
            username = st.text_input("Username *")
            password = st.text_input("Password *", type="password")
            email    = st.text_input("Email")

            submitted = st.form_submit_button("➕ Add Teacher", type="primary", use_container_width=True)
            if submitted:
                if not all([name, username, password]):
                    st.error("Please fill all required (*) fields.")
                else:
                    ok, msg = add_teacher({
                        "teacher_id": f"TCH{uuid.uuid4().hex[:6].upper()}",
                        "name":       name.strip(),
                        "username":   username.strip(),
                        "password":   password,
                        "email":      email.strip(),
                    })
                    st.success(f"✅ {msg} Now go to 'Manage Assignments' to give them subjects.") if ok else st.error(f"❌ {msg}")

    # ── EDIT / DELETE ─────────────────────────────────────────
    with tab3:
        section_header("✏️", "Edit or Delete Teacher")

        teachers_all = get_all_teachers()
        if not teachers_all:
            st.info("No teachers in the system.")
        else:
            t_map  = {f"{t['name']} ({t.get('username','')})": t for t in teachers_all}
            choice = st.selectbox("Select Teacher", list(t_map.keys()), key="edit_teacher_sel")
            t      = t_map[choice]

            with st.form("edit_teacher_form"):
                new_name  = st.text_input("Full Name", value=t.get("name",""))
                new_uname = st.text_input("Username",  value=t.get("username",""))
                new_pwd   = st.text_input("New Password (blank = keep)", type="password")
                new_email = st.text_input("Email",     value=t.get("email",""))

                col_s, col_d = st.columns(2)
                with col_s:
                    save   = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
                with col_d:
                    delete = st.form_submit_button("🗑️ Delete", use_container_width=True)

                if save:
                    updates = {"name": new_name, "username": new_uname, "email": new_email}
                    if new_pwd:
                        updates["password"] = new_pwd
                    ok, msg = update_teacher(t["teacher_id"], updates)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

                if delete:
                    ok, msg = delete_teacher(t["teacher_id"])
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                    if ok:
                        st.rerun()

    # ── MANAGE ASSIGNMENTS (many-to-many) ─────────────────────
    with tab4:
        section_header("🔗", "Assign / Unassign Subjects & Sections",
                        "A teacher can hold multiple subject+section assignments")

        teachers_all2 = get_all_teachers()
        if not teachers_all2:
            st.info("No teachers available.")
        else:
            t_map2   = {t["name"]: t for t in teachers_all2}
            t_choice = st.selectbox("Teacher", list(t_map2.keys()), key="assign_t")
            t2       = t_map2[t_choice]

            current = get_teacher_assignments(t2["teacher_id"])

            st.markdown("**Current assignments:**")
            if current:
                for a in current:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"- {a['subject_name']} — Section {a['section']} (Q{a['semester']})")
                    with c2:
                        if st.button("🗑️ Remove", key=f"unassign_{a['assignment_id']}"):
                            ok, msg = unassign_subject_from_teacher(a["assignment_id"])
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()
            else:
                st.info("No assignments yet.")

            st.markdown("---")
            st.markdown("**Add a new assignment:**")

            # Quarter picked first, so the subject list below can be
            # filtered down to only that quarter's subjects.
            new_sem3 = st.selectbox("Quarter", [1, 2, 3, 4], key="assign_sem")

            subjects_list3 = [s for s in get_all_subjects() if s["semester"] == new_sem3]

            if not subjects_list3:
                st.warning(f"⚠️ No subjects exist for Quarter {new_sem3} yet. Add one under Subject Management.")
            else:
                sub_opts3 = {s["name"]: s["code"] for s in subjects_list3}

                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    new_sub3 = st.selectbox("Subject", list(sub_opts3.keys()), key="assign_sub")
                with c2:
                    new_sec3 = st.selectbox("Section", ["A","B","C","D"], key="assign_sec")
                with c3:
                    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
                    if st.button("🔗 Assign", type="primary"):
                        ok, msg = assign_subject_to_teacher(t2["teacher_id"], sub_opts3[new_sub3], new_sec3)
                        st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                        st.rerun()