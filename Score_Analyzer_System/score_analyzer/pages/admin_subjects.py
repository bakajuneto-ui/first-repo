"""Admin – Add / Update / Delete subjects."""
import streamlit as st
import pandas as pd
import uuid
from components.ui import section_header
from utils.database import (
    get_all_subjects, add_subject, update_subject, delete_subject
)


def render():
    st.markdown('<div class="page-title">📚 Subject Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Add, update, or remove subjects</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add Subject", "✏️ Edit / Remove"])

    # ── VIEW ALL ─────────────────────────────────────────────
    with tab1:
        section_header("📋", "All Subjects")

        sem_filter = st.selectbox("Filter by Quarter", ["All", 1, 2, 3, 4], key="sub_sem_filter")

        subjects = get_all_subjects()
        if sem_filter != "All":
            subjects = [s for s in subjects if s.get("semester") == sem_filter]

        if subjects:
            rows = [{
                "Subject ID": s.get("subject_id", ""),
                "Code":       s.get("code", ""),
                "Name":       s.get("name", ""),
                "Quarter":    s.get("semester", ""),
                "Max Marks":  s.get("max_marks", 100),
            } for s in subjects]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption(f"{len(subjects)} subject(s) found")
        else:
            st.info("No subjects found.")

    # ── ADD SUBJECT ───────────────────────────────────────────
    with tab2:
        section_header("➕", "Add New Subject")

        with st.form("add_subject_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Subject Name *")
                code = st.text_input("Subject Code *", help="Must be unique, e.g. DS101")
            with c2:
                semester  = st.selectbox("Quarter *", [1, 2, 3, 4])
                max_marks = st.number_input("Max Marks", min_value=1, value=100, step=1)

            submitted = st.form_submit_button("➕ Add Subject", type="primary", use_container_width=True)
            if submitted:
                if not all([name, code]):
                    st.error("Please fill all required (*) fields.")
                else:
                    ok, msg = add_subject({
                        "subject_id": f"SUB{uuid.uuid4().hex[:6].upper()}",
                        "code":       code.strip().upper(),
                        "name":       name.strip(),
                        "semester":   semester,
                        "max_marks":  int(max_marks),
                    })
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

    # ── EDIT / DELETE ─────────────────────────────────────────
    with tab3:
        section_header("✏️", "Edit or Remove Subject")

        subjects_all = get_all_subjects()
        if not subjects_all:
            st.info("No subjects in the system.")
        else:
            s_map  = {f"{s['name']} ({s['code']})": s for s in subjects_all}
            choice = st.selectbox("Select Subject", list(s_map.keys()), key="edit_subject_sel")
            s      = s_map[choice]

            with st.form("edit_subject_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Subject Name", value=s.get("name", ""))
                    new_code = st.text_input("Subject Code", value=s.get("code", ""))
                with c2:
                    new_sem = st.selectbox("Quarter", [1, 2, 3, 4],
                                            index=[1, 2, 3, 4].index(s.get("semester", 1)))
                    new_max = st.number_input("Max Marks", min_value=1,
                                               value=int(s.get("max_marks", 100)), step=1)

                col_s, col_d = st.columns(2)
                with col_s:
                    save = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
                with col_d:
                    delete = st.form_submit_button("🗑️ Delete", use_container_width=True)

                if save:
                    updates = {
                        "name":      new_name,
                        "code":      new_code.strip().upper(),
                        "semester":  new_sem,
                        "max_marks": int(new_max),
                    }
                    ok, msg = update_subject(s["subject_id"], updates)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

                if delete:
                    ok, msg = delete_subject(s["subject_id"])
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                    if ok:
                        st.rerun()