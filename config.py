import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "smart_campus.db"
UPLOAD_DIR = BASE_DIR / "uploads"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"

# Create directories if they do not exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# AI Configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Complaint Categories
CATEGORIES = [
    "Laboratory",
    "Hostel",
    "Classroom",
    "Library",
    "Transport",
    "Infrastructure",
    "Other",
]

# Priority Levels
PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Status States
STATUS_LEVELS = ["Open", "In Progress", "Resolved"]

# Canonical Departments
DEPARTMENTS = [
    "Lab Maintenance",
    "Hostel Administration",
    "Estate & Facilities",
    "IT Support",
    "Library Services",
    "Transport Office",
    "Academic Affairs",
    "Unassigned / Review Needed",
]

# Department Detailed Metadata: Themes, Staff Rosters & Contacts
DEPARTMENT_DETAILS = {
    "Lab Maintenance": {
        "slug": "lab_maintenance",
        "head": "Eng. Robert Vance",
        "email": "lab-maintenance@campus.edu",
        "location": "Technology Tower, Ground Floor, Room TT-012",
        "color": "#0284C7",
        "bg_color": "#E0F2FE",
        "border_color": "#7DD3FC",
        "technicians": [
            "Robert Vance (Senior Systems Engineer)",
            "Anita Sharma (Hardware Specialist)",
            "David Miller (Network Technician)",
            "Sunil Rao (Lab Assistant)"
        ],
        "default_username": "dept_lab",
        "description": "Supervises computer laboratories, hardware maintenance, software environments, and exam workstation readiness."
    },
    "Hostel Administration": {
        "slug": "hostel_admin",
        "head": "Dr. Sarah Jenkins (Chief Warden)",
        "email": "hostel-office@campus.edu",
        "location": "Central Student Center, 1st Floor",
        "color": "#4F46E5",
        "bg_color": "#EEF2FF",
        "border_color": "#A5B4FC",
        "technicians": [
            "Dr. Sarah Jenkins (Chief Warden)",
            "Michael Ross (Resident Inspector)",
            "Priya Nair (Sanitation Supervisor)",
            "James Wilson (Hostel Caretaker)"
        ],
        "default_username": "dept_hostel",
        "description": "Governs dormitory allocations, residential plumbing, dining hall hygiene, room maintenance, and hostel curfew."
    },
    "Estate & Facilities": {
        "slug": "estate_facilities",
        "head": "Mr. David Kumar (Director)",
        "email": "estate-facilities@campus.edu",
        "location": "Maintenance Yard, Operations Building",
        "color": "#059669",
        "bg_color": "#ECFDF5",
        "border_color": "#6EE7B7",
        "technicians": [
            "David Kumar (Facilities Director)",
            "Carlos Santana (Senior Electrician)",
            "Sunita Verma (Civil & Water Works)",
            "Alan Baker (HVAC Technician)"
        ],
        "default_username": "dept_estate",
        "description": "Oversees physical campus buildings, classroom air conditioning, electrical grid, plumbing mains, and civil infrastructure."
    },
    "IT Support": {
        "slug": "it_support",
        "head": "Ms. Priya Patel (Lead Admin)",
        "email": "it-support@campus.edu",
        "location": "Tech Building, 2nd Floor, Room TB-205",
        "color": "#7C3AED",
        "bg_color": "#F5F3FF",
        "border_color": "#C4B5FD",
        "technicians": [
            "Priya Patel (Lead Network Admin)",
            "Alex Chen (Systems Administrator)",
            "Kevin Wright (Student Helpdesk)",
            "Fatima Zahra (Cybersecurity Analyst)"
        ],
        "default_username": "dept_it",
        "description": "Manages campus Wi-Fi credentials, student portals, email accounts, institutional servers, firewalls, and digital services."
    },
    "Library Services": {
        "slug": "library_services",
        "head": "Prof. Michael Chang",
        "email": "library@campus.edu",
        "location": "Central Library, Main Circulation Desk",
        "color": "#D97706",
        "bg_color": "#FFFBEB",
        "border_color": "#FCD34D",
        "technicians": [
            "Prof. Michael Chang (Chief Librarian)",
            "Sarah Lin (Digital Catalog Admin)",
            "Rajiv Verma (Circulation Officer)",
            "Emily Watson (Reading Room Supervisor)"
        ],
        "default_username": "dept_library",
        "description": "Manages book lending kiosks, RFID turnstiles, quiet reading halls, research databases, and library air conditioning."
    },
    "Transport Office": {
        "slug": "transport_office",
        "head": "Capt. Arvind Singh",
        "email": "transport@campus.edu",
        "location": "Gate 2 Administration Complex",
        "color": "#EA580C",
        "bg_color": "#FFF7ED",
        "border_color": "#FDBA74",
        "technicians": [
            "Capt. Arvind Singh (Transit Director)",
            "Harpreet Singh (Fleet Supervisor)",
            "Suresh Rao (Route Coordinator)",
            "Vikram Seth (Mechanic In-Charge)"
        ],
        "default_username": "dept_transport",
        "description": "Administers campus shuttle buses, route timings, driver rosters, transit passes, and shuttle breakdown response."
    },
    "Academic Affairs": {
        "slug": "academic_affairs",
        "head": "Dean Dr. Eleanor Ross",
        "email": "academic-affairs@campus.edu",
        "location": "Academic Block A, Deanery Suite",
        "color": "#E11D48",
        "bg_color": "#FFF1F2",
        "border_color": "#FDA4AF",
        "technicians": [
            "Dean Dr. Eleanor Ross (Academic Dean)",
            "Rachel Green (Examination Coordinator)",
            "Marcus Bell (Registrar Assistant)",
            "Clara Oswald (Lecture Hall Allocator)"
        ],
        "default_username": "dept_academic",
        "description": "Manages lecture schedules, mid-term & practical examination schedules, faculty disputes, and academic appeals."
    }
}

# SLA Target Timelines
SLA_HOURS_MAP = {
    "Critical": 4,
    "High": 12,
    "Medium": 48,
    "Low": 96
}

def get_project_zip_bytes() -> bytes:
    """Build an in-memory zip archive of all clean source code files and PDF documentation."""
    import io
    import zipfile
    buf = io.BytesIO()
    src_root = str(BASE_DIR)
    exclude_dirs = {"__pycache__", ".git", "chroma_db", "venv", ".venv"}
    exclude_exts = {".pyc", ".db", ".sqlite3"}

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in exclude_exts:
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, src_root)
                z.write(full_path, arcname=os.path.join("smart_campus_ai", rel_path))
    buf.seek(0)
    return buf.getvalue()

def get_project_pdf_bytes() -> bytes:
    """Return bytes of the generated source code PDF if present."""
    pdf_p = BASE_DIR / "Smart_Campus_AI_Full_Source_Code.pdf"
    if pdf_p.exists():
        with open(pdf_p, "rb") as f:
            return f.read()
    return b""

