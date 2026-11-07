import streamlit as st
import database as db
from config import DEPARTMENT_DETAILS, get_project_zip_bytes, get_project_pdf_bytes
from ui.styles import get_custom_css
from ui.landing import render_landing_page
from ui.student_portal import render_student_portal
from ui.department_page import render_department_page
from ui.admin_dashboard import render_admin_dashboard
from ui.kb_browser import render_kb_browser
from ui.workflow_view import render_workflow_view
from ui.login_pages import (
    render_login_hub,
    render_student_login_page,
    render_dept_login_page,
    render_admin_login_page
)

# Streamlit Page Configuration (No emojis)
st.set_page_config(
    page_title="Smart Campus AI - Complaint Management System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema & Seed Data
db.init_db()

# Apply SaaS Custom Styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Navigation helper
def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

# Initialize Session State
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "landing"

if "student_user" not in st.session_state:
    st.session_state["student_user"] = None

if "dept_user" not in st.session_state:
    st.session_state["dept_user"] = None

if "admin_user" not in st.session_state:
    st.session_state["admin_user"] = None

# Sidebar Navigation (No emojis)
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 15px;">
        <strong style="color: #0F2744; font-size: 1.15rem; display: block; line-height: 1.2;">Smart Campus AI</strong>
        <span style="font-size: 0.78rem; color: #64748B; font-weight: 500;">Complaint Management System</span>
    </div>
    """, unsafe_allow_html=True)

    current = st.session_state["current_page"]

    # Core Navigation Sections
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Navigation</p>", unsafe_allow_html=True)

    nav_main = {
        "landing": "Home & Overview",
        "student": "Student Portal",
        "dept_page": "Department Operations",
        "admin": "Central Admin Console",
        "kb": "Knowledge Base & RAG",
        "workflow": "System Architecture"
    }

    for page_key, label in nav_main.items():
        is_active = (current == page_key)
        button_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=button_type):
            navigate_to(page_key)

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Dedicated Login Pages Access
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Sign In Portals</p>", unsafe_allow_html=True)

    nav_logins = {
        "login_student": "Student Sign In",
        "login_dept": "Department Staff Sign In",
        "login_admin": "Central Admin Sign In",
        "login_hub": "All Sign In Options"
    }

    for log_key, log_label in nav_logins.items():
        is_active = (current == log_key)
        button_type = "primary" if is_active else "secondary"
        if st.button(log_label, key=f"nav_{log_key}", use_container_width=True, type=button_type):
            navigate_to(log_key)

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Department Quick Switcher
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Departments</p>", unsafe_allow_html=True)
    dept_names = list(DEPARTMENT_DETAILS.keys())
    active_dept = st.session_state.get("active_dept_name", "Lab Maintenance")
    selected_dept_side = st.selectbox(
        "Select Department Workspace",
        dept_names,
        index=dept_names.index(active_dept) if active_dept in dept_names else 0,
        label_visibility="collapsed"
    )
    if selected_dept_side != active_dept:
        st.session_state["active_dept_name"] = selected_dept_side
        if current != "dept_page":
            navigate_to("dept_page")
        else:
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Demonstration Trigger Button
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Demonstration</p>", unsafe_allow_html=True)
    if st.button("Test Exam Scenario", use_container_width=True, help="Load CSE lab computers down test case"):
        st.session_state["demo_prefill"] = True
        navigate_to("student")

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Download All Files & PDF Documentation
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Download All Files</p>", unsafe_allow_html=True)
    st.download_button(
        label="Download Project (.ZIP)",
        data=get_project_zip_bytes(),
        file_name="smart_campus_ai_codebase.zip",
        mime="application/zip",
        use_container_width=True,
        help="Download clean zip of all 30 source code files"
    )
    pdf_data = get_project_pdf_bytes()
    if pdf_data:
        st.download_button(
            label="Download Code (PDF)",
            data=pdf_data,
            file_name="Smart_Campus_AI_Full_Source_Code.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Download complete 83-page compiled source code PDF"
        )

    st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Active Sessions Status & Logout
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;'>Active Sessions</p>", unsafe_allow_html=True)
    
    student_user = st.session_state.get("student_user")
    dept_user = st.session_state.get("dept_user")
    admin_user = st.session_state.get("admin_user")

    has_session = False
    if student_user:
        has_session = True
        st.markdown(f"**Student:** `{student_user['username']}`")
        if st.button("Log Out Student", key="side_logout_student"):
            st.session_state["student_user"] = None
            st.rerun()

    if dept_user:
        has_session = True
        st.markdown(f"**Dept:** `{dept_user['username']}` ({dept_user.get('department', '')})")
        if st.button("Log Out Dept Staff", key="side_logout_dept"):
            st.session_state["dept_user"] = None
            st.rerun()

    if admin_user:
        has_session = True
        st.markdown(f"**Admin:** `{admin_user['username']}`")
        if st.button("Log Out Admin", key="side_logout_admin"):
            st.session_state["admin_user"] = None
            st.rerun()

    if not has_session:
        st.caption("No active user session. Select a portal above to sign in.")

    st.markdown("<div style='margin-top: 1.8rem; font-size: 0.75rem; color: #94A3B8;'>Powered by LangGraph, ChromaDB & SQLite</div>", unsafe_allow_html=True)

# Main Application Routing
current_page = st.session_state.get("current_page", "landing")

if current_page == "landing":
    render_landing_page(navigate_to)
elif current_page == "student":
    render_student_portal()
elif current_page == "dept_page":
    render_department_page()
elif current_page == "admin":
    render_admin_dashboard()
elif current_page == "login_hub":
    render_login_hub(navigate_to)
elif current_page == "login_student":
    render_student_login_page(navigate_to)
elif current_page == "login_dept":
    render_dept_login_page(navigate_to)
elif current_page == "login_admin":
    render_admin_login_page(navigate_to)
elif current_page == "kb":
    render_kb_browser()
elif current_page == "workflow":
    render_workflow_view()
else:
    render_landing_page(navigate_to)
