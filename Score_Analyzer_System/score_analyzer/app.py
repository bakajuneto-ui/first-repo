"""
MCA Student Score Analyzer
Main entry point – handles login, self-registration, and page routing.
"""
import os
import base64
import streamlit as st
import uuid

ROOT_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(ROOT_DIR, "assets", "logo.png")
BACKGROUND_PATH = os.path.join(ROOT_DIR, "assets", "background.png")

st.set_page_config(
    page_title="Student Score Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def _get_logo_data_uri():
    if not os.path.exists(LOGO_PATH):
        return None

    ext = os.path.splitext(LOGO_PATH)[1].lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }.get(ext, "image/png")

    with open(LOGO_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def _get_background_data_uri():
    if not os.path.exists(BACKGROUND_PATH):
        return None

    with open(BACKGROUND_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"

from components.ui import inject_css, render_sidebar
from utils.database import authenticate_user, seed_database, check_connection, add_student

# Pages
from pages.student_dashboard  import render as student_dashboard
from pages.student_marks       import render as student_marks
from pages.student_analytics   import render as student_analytics
from pages.student_rank        import render as student_rank
from pages.teacher_dashboard   import render as teacher_dashboard
from pages.teacher_upload      import render as teacher_upload
from pages.teacher_edit        import render as teacher_edit
from pages.teacher_analytics   import render as teacher_analytics
from pages.teacher_performers  import render as teacher_performers
from pages.admin_dashboard     import render as admin_dashboard
from pages.admin_students      import render as admin_students
from pages.admin_teachers      import render as admin_teachers
from pages.admin_subjects      import render as admin_subjects
from pages.admin_marks         import render as admin_marks
from pages.admin_analytics     import render as admin_analytics

# Note: CSS injection is applied conditionally per-view (login vs app pages).

# ─── DB Initialization ──────────────────────────────────────
@st.cache_resource
def init_app():
    ok, msg = check_connection()
    if ok:
        seed_database()
    return ok, msg

db_ok, db_msg = init_app()

# ─── Session defaults ────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = None
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"   # "login" or "register"


# ─────────────────────────────────────────────────────────────
#  DB DOWN PANEL
# ─────────────────────────────────────────────────────────────
def render_db_error():
    st.markdown(
        f'<div style="max-width:480px;margin:4rem auto;background:#FEE2E2;border:1px solid #FECACA;'
        f'border-radius:16px;padding:2rem;text-align:center;">'
        f'<div style="font-size:3rem;">⚠️</div>'
        f'<h2 style="color:#991B1B;">Database Connection Failed</h2>'
        f'<p style="color:#7F1D1D;font-size:.9rem;">{db_msg}</p>'
        f'<p style="color:#7F1D1D;font-size:.85rem;margin-top:1rem;">'
        f'Check that the Oracle listener is reachable and that '
        f'<code style="background:#FEF2F2;padding:.15rem .4rem;border-radius:6px;">ORACLE_HOST</code>, '
        f'<code style="background:#FEF2F2;padding:.15rem .4rem;border-radius:6px;">ORACLE_PORT</code>, '
        f'<code style="background:#FEF2F2;padding:.15rem .4rem;border-radius:6px;">ORACLE_SERVICE</code>, '
        f'<code style="background:#FEF2F2;padding:.15rem .4rem;border-radius:6px;">ORACLE_USER</code> and '
        f'<code style="background:#FEF2F2;padding:.15rem .4rem;border-radius:6px;">ORACLE_PASSWORD</code> are set correctly.<br>'
        f'Quick check from a terminal:<br>'
        f'<code style="background:#FEF2F2;padding:.2rem .5rem;border-radius:6px;">sqlplus user/pass@host:port/service</code>'
        f'</p>'
        f'</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────────────────────
def render_login():
    # Apply the login background image for the auth view
    inject_css(background_image=_get_background_data_uri(), show_sidebar=False)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        logo_data_uri = _get_logo_data_uri()
        logo_html = (
            f'<img src="{logo_data_uri}" class="logo-img" alt="Logo" />'
            if logo_data_uri
            else '<div class="logo-icon">🎓</div>'
        )

        st.markdown(
            f'<div class="login-page-shell">'
            f'<div class="login-container">'
            f'<div class="login-logo">'
            f'{logo_html}'
            f'<h1>Student Score Analyzer</h1>'
            f'<p>Echague National High School · Score Management System</p>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Role selector
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        role = st.selectbox(
            "Login as",
            ["👨‍🎓 Student", "👩‍🏫 Teacher", "👩‍💼 Admin"],
            key="login_role"
        )
        role_key = role.split()[-1].lower()
        role_key = "admin" if role_key == "admin" else role_key

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(" Sign In", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = authenticate_user(username.strip(), password.strip(), role_key)
                    if user:
                        st.session_state.logged_in   = True
                        st.session_state.role        = role_key
                        st.session_state.user_id     = str(user.get("student_id") or user.get("teacher_id") or user.get("admin_id"))
                        st.session_state.user_name   = user["name"]
                        st.session_state.user_data   = dict(user)
                        # Default pages
                        default = {
                            "student":  "student_dashboard",
                            "teacher":  "teacher_dashboard",
                            "admin":    "admin_dashboard"
                        }
                        st.session_state.page = default[role_key]
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        # Register link (students only)
        st.markdown("<div style='text-align:center;margin-top:.75rem;'>", unsafe_allow_html=True)
        if st.button(" New student? Create an account", use_container_width=True):
            st.session_state.auth_view = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  REGISTRATION PAGE (students only)
# ─────────────────────────────────────────────────────────────
def render_register():
    # Apply the login/registration background image for the auth view
    inject_css(background_image=_get_background_data_uri(), show_sidebar=False)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        logo_data_uri = _get_logo_data_uri()
        logo_html = (
            f'<img src="{logo_data_uri}" class="logo-img" alt="Logo" />'
            if logo_data_uri
            else '<div class="logo-icon">📝</div>'
        )

        st.markdown(
            f'<div class="login-page-shell">'
            f'<div class="login-container">'
            f'<div class="login-logo">'
            f'{logo_html}'
            f'<h1>Create Student Account</h1>'
            f'<p>Register to access your marks, analytics, and rank</p>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                name     = st.text_input("Full Name *")
                username = st.text_input("Choose a Username *")
                password = st.text_input("Choose a Password *", type="password")
                confirm  = st.text_input("Confirm Password *", type="password")
            with c2:
                roll     = st.text_input("Roll Number *")
                section  = st.selectbox("Section *", ["A", "B", "C", "D"])
                year     = st.selectbox("Year *", [1, 2])
                semester = st.selectbox("Quarter *", [1, 2, 3, 4])
            if submitted:
                if not all([name, username, password, confirm, roll]):
                    st.error("Please fill all required (*) fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
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
                        st.success("✅ Account created! You can now sign in below.")
                        st.session_state.auth_view = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        st.markdown("<div style='text-align:center;margin-top:.5rem;'>", unsafe_allow_html=True)
        if st.button("← Back to Sign In", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────
def route():
    role = st.session_state.get("role")
    page = st.session_state.get("page")

    render_sidebar(role, st.session_state.user_name)

    routing = {
        "student_dashboard":  student_dashboard,
        "student_marks":      student_marks,
        "student_analytics":  student_analytics,
        "student_rank":       student_rank,
        "teacher_dashboard":  teacher_dashboard,
        "teacher_upload":     teacher_upload,
        "teacher_edit":       teacher_edit,
        "teacher_analytics":  teacher_analytics,
        "teacher_performers": teacher_performers,
        "admin_dashboard":    admin_dashboard,
        "admin_students":     admin_students,
        "admin_teachers":     admin_teachers,
        "admin_subjects":     admin_subjects,
        "admin_marks":        admin_marks,
        "admin_analytics":    admin_analytics,
    }

    fn = routing.get(page)
    if fn:
        fn()
    else:
        st.info("Select a page from the sidebar.")


# ─────────────────────────────────────────────────────────────
#  ENTRY
# ─────────────────────────────────────────────────────────────
if not db_ok:
    # When DB is not available, don't apply the login background
    inject_css(background_image=None, show_sidebar=False)
    render_db_error()
elif not st.session_state.logged_in:
    if st.session_state.auth_view == "register":
        render_register()
    else:
        render_login()
else:
    # Clear the login background when the user is inside the app
    inject_css(background_image=None)
    route()