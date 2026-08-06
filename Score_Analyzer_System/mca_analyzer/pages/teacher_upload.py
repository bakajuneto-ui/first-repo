"""Teacher – Upload / Enter marks (manual + Excel)."""
import streamlit as st
import pandas as pd
import io
from utils.database import (
    get_students_by_section, upsert_mark, bulk_upsert_marks,
    get_marks_by_subject_section
)
from components.ui import section_header, teacher_assignment_picker


def render():
    user = st.session_state.user_data
    t_id = user.get("teacher_id", "")

    st.markdown('<div class="page-title">📝 Upload / Enter Marks</div>', unsafe_allow_html=True)

    assignment = teacher_assignment_picker(t_id)
    if not assignment:
        return

    sub_code = assignment["subject_code"]
    sub_name = assignment["subject_name"]
    section  = assignment["section"]
    sem      = assignment["semester"]
    max_m    = assignment.get("max_marks", 100)

    st.markdown(f'<div class="page-subtitle">Subject: <b>{sub_name}</b> · Section <b>{section}</b> · Quarter <b>{sem}</b></div>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✏️ Manual Entry", "📂 Excel Upload"])

    students = get_students_by_section(section)
    existing = {m["student_id"]: m["marks_obtained"]
                for m in get_marks_by_subject_section(sub_code, section, sem)}

    # ── MANUAL ENTRY ──────────────────────────────────────────
    with tab1:
        section_header("✏️", "Manual Mark Entry", "Enter marks for each student")

        with st.form("manual_marks_form"):
            mark_inputs = {}
            cols = st.columns(2)
            for i, stu in enumerate(students):
                sid = stu["student_id"]
                default = float(existing.get(sid, 0))
                with cols[i % 2]:
                    mark_inputs[sid] = st.number_input(
                        f"{stu['name']} ({stu['roll_number']})",
                        min_value=0.0, max_value=float(max_m),
                        value=default, step=0.5, key=f"mk_{sid}"
                    )

            submitted = st.form_submit_button("💾 Save All Marks", type="primary", use_container_width=True)
            if submitted:
                saved, failed = 0, 0
                for sid, val in mark_inputs.items():
                    ok, _ = upsert_mark(sid, sub_code, sem, val, max_m)
                    if ok: saved += 1
                    else:  failed += 1
                if saved:
                    st.success(f"✅ {saved} marks saved successfully!")
                if failed:
                    st.error(f"❌ {failed} marks failed validation.")

    # ── EXCEL UPLOAD ──────────────────────────────────────────
    with tab2:
        section_header("📂", "Excel Upload", "Download template, fill marks, re-upload")

        template_rows = [{"student_id": s["student_id"],
                           "name": s["name"],
                           "roll_number": s["roll_number"],
                           "marks_obtained": existing.get(s["student_id"], 0)}
                          for s in students]
        df_tmpl = pd.DataFrame(template_rows)
        buf = io.BytesIO()
        df_tmpl.to_excel(buf, index=False)
        st.download_button(
            "⬇️ Download Template",
            data=buf.getvalue(),
            file_name=f"marks_{sub_code}_section{section}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        uploaded = st.file_uploader("📤 Upload Filled Excel", type=["xlsx", "xls", "csv"])
        if uploaded:
            try:
                df = pd.read_excel(uploaded) if uploaded.name.endswith(("xlsx","xls")) else pd.read_csv(uploaded)
                required = {"student_id", "marks_obtained"}
                if not required.issubset(set(df.columns)):
                    st.error(f"Excel must contain columns: {required}")
                else:
                    st.dataframe(df[["student_id","name","roll_number","marks_obtained"]],
                                 use_container_width=True)
                    if st.button("✅ Confirm & Save", type="primary"):
                        records = []
                        for _, row in df.iterrows():
                            records.append({
                                "student_id":    str(row["student_id"]),
                                "subject_code":  sub_code,
                                "semester":      sem,
                                "marks_obtained": float(row["marks_obtained"])
                            })
                        ok, fail = bulk_upsert_marks(records)
                        st.success(f"✅ {ok} records saved. {fail} failed.")
            except Exception as e:
                st.error(f"Error reading file: {e}")