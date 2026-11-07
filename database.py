import sqlite3
import hashlib
import os
import json
from datetime import datetime
from config import DB_PATH, DEPARTMENT_DETAILS, SLA_HOURS_MAP

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: str = None) -> str:
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed = stored_hash.split("$")
        check = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return check == hashed
    except Exception:
        return False

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT DEFAULT 'General',
            phone TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            student_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            priority_reason TEXT DEFAULT '',
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            attachment_path TEXT DEFAULT '',
            rag_context TEXT DEFAULT '',
            needs_review INTEGER DEFAULT 0,
            assigned_technician TEXT DEFAULT '',
            sla_hours INTEGER DEFAULT 24,
            student_rating INTEGER DEFAULT 0,
            student_feedback TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES users(id)
        )
    """)

    # Check and add any missing columns in complaints table if it already existed
    cursor.execute("PRAGMA table_info(complaints)")
    existing_cols = [row["name"] for row in cursor.fetchall()]
    if "assigned_technician" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN assigned_technician TEXT DEFAULT ''")
    if "sla_hours" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN sla_hours INTEGER DEFAULT 24")
    if "student_rating" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN student_rating INTEGER DEFAULT 0")
    if "student_feedback" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN student_feedback TEXT DEFAULT ''")
    if "completed_by_dept" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN completed_by_dept INTEGER DEFAULT 0")
    if "replaced_parts" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN replaced_parts TEXT DEFAULT ''")

    # Complaint History / Audit Trail
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            ticket_id TEXT NOT NULL,
            previous_status TEXT NOT NULL,
            new_status TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            notes TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(complaint_id) REFERENCES complaints(id)
        )
    """)

    # Resolution Notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resolution_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            ticket_id TEXT NOT NULL,
            author_name TEXT NOT NULL,
            author_role TEXT NOT NULL,
            note_text TEXT NOT NULL,
            is_internal INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(complaint_id) REFERENCES complaints(id)
        )
    """)

    # Notifications Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            recipient_role TEXT NOT NULL,
            department TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            urgency TEXT NOT NULL DEFAULT 'Medium',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed Accounts: Ensure Central Admin, Default Student, and All 7 Department accounts exist
    admin_pass = hash_password("Admin@123")
    student_pass = hash_password("Student@123")

    # Central Administrator
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, role, department, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("admin", admin_pass, "admin@campus.edu", "Campus Administrator", "admin", "Administration", "+1-555-0100"))

    # Default Student
    cursor.execute("SELECT id FROM users WHERE username = 'student1'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, role, department, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("student1", student_pass, "alex.johnson@student.campus.edu", "Alex Johnson", "student", "Computer Science", "+1-555-0199"))

    # Seed Department Officers for each of the 7 departments
    dept_seeds = [
        ("dept_lab", "Lab@123", "lab-maintenance@campus.edu", "Robert Vance (Lab Maintenance)", "admin", "Lab Maintenance"),
        ("dept_hostel", "Hostel@123", "hostel-office@campus.edu", "Dr. Sarah Jenkins (Hostel Admin)", "admin", "Hostel Administration"),
        ("dept_estate", "Estate@123", "estate-facilities@campus.edu", "David Kumar (Estate & Facilities)", "admin", "Estate & Facilities"),
        ("dept_it", "IT@123", "it-support@campus.edu", "Priya Patel (IT Support)", "admin", "IT Support"),
        ("dept_library", "Library@123", "library@campus.edu", "Prof. Michael Chang (Library Services)", "admin", "Library Services"),
        ("dept_transport", "Transport@123", "transport@campus.edu", "Capt. Arvind Singh (Transport Office)", "admin", "Transport Office"),
        ("dept_academic", "Academic@123", "academic-affairs@campus.edu", "Dean Eleanor Ross (Academic Affairs)", "admin", "Academic Affairs"),
    ]

    for u_name, u_pwd, u_email, u_full, u_role, u_dept in dept_seeds:
        cursor.execute("SELECT id FROM users WHERE username = ?", (u_name,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, full_name, role, department, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (u_name, hash_password(u_pwd), u_email, u_full, u_role, u_dept, "+1-555-0150"))

    conn.commit()
    conn.close()

def create_user(username, password, email, full_name, role="student", department="General", phone=""):
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, role, department, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, pwd_hash, email, full_name, role, department, phone))
        conn.commit()
        user_id = cursor.lastrowid
        return True, user_id, "User registered successfully."
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, None, "Username already exists."
        elif "email" in str(e):
            return False, None, "Email already exists."
        return False, None, "Registration failed: user already exists."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
    user = cursor.fetchone()
    conn.close()
    if user and verify_password(password, user["password_hash"]):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name, role, department, phone, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_next_ticket_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM complaints ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    next_num = 1 if not row else row["id"] + 1
    return f"CAMP-{next_num:04d}"

def insert_complaint(student_id, student_name, student_email, title, description,
                     category, priority, priority_reason, department,
                     attachment_path="", rag_context="", needs_review=0,
                     ticket_id=None, sla_hours=None):
    conn = get_connection()
    cursor = conn.cursor()
    if not ticket_id:
        cursor.execute("SELECT id FROM complaints ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        next_num = 1 if not row else row["id"] + 1
        ticket_id = f"CAMP-{next_num:04d}"

    if not sla_hours:
        sla_hours = SLA_HOURS_MAP.get(priority, 24)

    cursor.execute("""
        INSERT INTO complaints (
            ticket_id, student_id, student_name, student_email, title,
            description, category, priority, priority_reason, department,
            status, attachment_path, rag_context, needs_review, sla_hours,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        ticket_id, student_id, student_name, student_email, title,
        description, category, priority, priority_reason, department,
        attachment_path, rag_context, needs_review, sla_hours
    ))
    complaint_id = cursor.lastrowid

    # Record initial creation in audit history
    cursor.execute("""
        INSERT INTO complaint_history (complaint_id, ticket_id, previous_status, new_status, changed_by, notes)
        VALUES (?, ?, 'None', 'Open', ?, 'Complaint submitted and ticket generated by AI System')
    """, (complaint_id, ticket_id, student_name))

    # AUTOMATIC IN-APP NOTIFICATIONS
    # 1. Notify the assigned department administrator
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'dept_admin', ?, ?, ?, ?)
    """, (
        ticket_id,
        department,
        f"New {priority} Priority Complaint: {ticket_id}",
        f"Complaint '{title}' logged by {student_name} and routed to {department}. Target SLA: {sla_hours}h.",
        priority
    ))

    # 2. Notify Central Administration
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'admin', 'Central', ?, ?, ?)
    """, (
        ticket_id,
        f"New Ticket Ingested: {ticket_id} ({department})",
        f"AI System assigned ticket {ticket_id} ({priority}) to {department}.",
        priority
    ))

    conn.commit()
    conn.close()
    return complaint_id, ticket_id

def get_complaint_by_ticket_id(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_complaints_by_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE student_id = ? ORDER BY id DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_complaints_by_department(dept_name, search=None, category=None, priority=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM complaints WHERE department = ?"
    params = [dept_name]

    if search:
        query += " AND (ticket_id LIKE ? OR title LIKE ? OR description LIKE ? OR student_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_complaints(search=None, category=None, priority=None, status=None, department=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if search:
        query += " AND (ticket_id LIKE ? OR title LIKE ? OR description LIKE ? OR student_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if department and department != "All":
        query += " AND department = ?"
        params.append(department)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_complaint_status(ticket_id, new_status, changed_by, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, department, student_name FROM complaints WHERE ticket_id = ?", (ticket_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False, "Complaint ticket not found."

    old_status = complaint["status"]
    cursor.execute("""
        UPDATE complaints
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (new_status, ticket_id))

    cursor.execute("""
        INSERT INTO complaint_history (complaint_id, ticket_id, previous_status, new_status, changed_by, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (complaint["id"], ticket_id, old_status, new_status, changed_by, notes))

    if notes:
        cursor.execute("""
            INSERT INTO resolution_notes (complaint_id, ticket_id, author_name, author_role, note_text, is_internal)
            VALUES (?, ?, ?, 'Staff', ?, 0)
        """, (complaint["id"], ticket_id, changed_by, notes))

    # Add notification for status change
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'student', ?, ?, ?, 'Medium')
    """, (
        ticket_id,
        complaint["department"],
        f"Ticket {ticket_id} Status: {new_status}",
        f"Status changed from {old_status} to {new_status} by {changed_by}."
    ))

    conn.commit()
    conn.close()
    return True, f"Status updated to '{new_status}' successfully."

def mark_complaint_completed(ticket_id, completed_by, notes="", replaced_parts=""):
    """
    Called when Department Portal marks a complaint as COMPLETED.
    Directly updates the ticket status to 'Resolved' so the Central Admin Portal
    and Student Portal immediately reflect it as RESOLVED.
    Dispatches immediate alert to Central Admin.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, department, title, student_name FROM complaints WHERE ticket_id = ?", (ticket_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False, "Complaint ticket not found."

    old_status = complaint["status"]
    dept = complaint["department"]

    # Mark status as Resolved and record completed_by_dept flag
    cursor.execute("""
        UPDATE complaints
        SET status = 'Resolved',
            completed_by_dept = 1,
            replaced_parts = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (replaced_parts.strip(), ticket_id))

    audit_note = f"Work marked COMPLETED by {dept} ({completed_by}). Ticket officially marked as RESOLVED in Central Admin. Diagnostic Notes: {notes}."
    if replaced_parts:
        audit_note += f" Hardware / Parts Replaced: {replaced_parts}."

    cursor.execute("""
        INSERT INTO complaint_history (complaint_id, ticket_id, previous_status, new_status, changed_by, notes)
        VALUES (?, ?, ?, 'Resolved', ?, ?)
    """, (complaint["id"], ticket_id, old_status, completed_by, audit_note))

    # Add official technician resolution report
    note_content = f"Work marked COMPLETED by {completed_by} ({dept}). {notes}"
    if replaced_parts:
        note_content += f" | Parts / Equipment Swapped: {replaced_parts}"

    cursor.execute("""
        INSERT INTO resolution_notes (complaint_id, ticket_id, author_name, author_role, note_text, is_internal)
        VALUES (?, ?, ?, 'Department Specialist', ?, 0)
    """, (complaint["id"], ticket_id, completed_by, note_content))

    # Dispatch alert to Central Administration
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'admin', 'Central', ?, ?, 'Low')
    """, (
        ticket_id,
        f"Ticket {ticket_id} Completed by {dept}",
        f"Department '{dept}' marked work COMPLETED for '{complaint['title']}'. The ticket is now marked as RESOLVED across Central Admin."
    ))

    # Dispatch alert to Student
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'student', ?, ?, ?, 'Low')
    """, (
        ticket_id,
        dept,
        f"Ticket {ticket_id} Resolved",
        f"{dept} has completed work on your complaint '{complaint['title']}'. Status is RESOLVED. Please submit your resolution satisfaction rating."
    ))

    conn.commit()
    conn.close()
    return True, f"Ticket {ticket_id} successfully marked as COMPLETED by {dept}. Central Admin and Student portals updated to RESOLVED."

def assign_technician_to_ticket(ticket_id, technician_name, assigned_by, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, department FROM complaints WHERE ticket_id = ?", (ticket_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False, "Complaint ticket not found."

    cursor.execute("""
        UPDATE complaints
        SET assigned_technician = ?, updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (technician_name, ticket_id))

    change_desc = f"Assigned Technician: {technician_name}. {notes}".strip()
    cursor.execute("""
        INSERT INTO complaint_history (complaint_id, ticket_id, previous_status, new_status, changed_by, notes)
        VALUES (?, ?, 'Assigned', 'Assigned', ?, ?)
    """, (complaint["id"], ticket_id, assigned_by, change_desc))

    conn.commit()
    conn.close()
    return True, f"Assigned technician '{technician_name}' to ticket {ticket_id}."

def submit_student_feedback(ticket_id, rating, feedback_text=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints
        SET student_rating = ?, student_feedback = ?, updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (rating, feedback_text.strip(), ticket_id))
    conn.commit()
    conn.close()
    return True, "Feedback submitted successfully. Thank you!"

def update_complaint_assignment(ticket_id, new_department, new_priority, changed_by, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, department, priority FROM complaints WHERE ticket_id = ?", (ticket_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False, "Complaint ticket not found."

    sla = SLA_HOURS_MAP.get(new_priority, 24)
    cursor.execute("""
        UPDATE complaints
        SET department = ?, priority = ?, sla_hours = ?, needs_review = 0, updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (new_department, new_priority, sla, ticket_id))

    change_desc = f"Updated assignment: Department -> {new_department}, Priority -> {new_priority}. {notes}".strip()
    cursor.execute("""
        INSERT INTO complaint_history (complaint_id, ticket_id, previous_status, new_status, changed_by, notes)
        VALUES (?, ?, 'Modified', 'Modified', ?, ?)
    """, (complaint["id"], ticket_id, changed_by, change_desc))

    # Trigger notification to the newly assigned department
    cursor.execute("""
        INSERT INTO notifications (ticket_id, recipient_role, department, title, message, urgency)
        VALUES (?, 'dept_admin', ?, ?, ?, ?)
    """, (
        ticket_id,
        new_department,
        f"Reassigned Ticket: {ticket_id} ({new_priority})",
        f"Ticket reassigned to {new_department} by {changed_by}.",
        new_priority
    ))

    conn.commit()
    conn.close()
    return True, "Complaint reassigned successfully."

def add_resolution_note(ticket_id, author_name, author_role, note_text, is_internal=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM complaints WHERE ticket_id = ?", (ticket_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False, "Complaint ticket not found."

    cursor.execute("""
        INSERT INTO resolution_notes (complaint_id, ticket_id, author_name, author_role, note_text, is_internal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (complaint["id"], ticket_id, author_name, author_role, note_text, is_internal))

    conn.commit()
    conn.close()
    return True, "Resolution note added."

def get_complaint_history(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaint_history WHERE ticket_id = ? ORDER BY id ASC", (ticket_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_resolution_notes(ticket_id, include_internal=False):
    conn = get_connection()
    cursor = conn.cursor()
    if include_internal:
        cursor.execute("SELECT * FROM resolution_notes WHERE ticket_id = ? ORDER BY id ASC", (ticket_id,))
    else:
        cursor.execute("SELECT * FROM resolution_notes WHERE ticket_id = ? AND is_internal = 0 ORDER BY id ASC", (ticket_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# NOTIFICATION SYSTEM QUERIES
def get_notifications(department=None, role=None, unread_only=False):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM notifications WHERE 1=1"
    params = []

    if department:
        query += " AND (department = ? OR department = 'All')"
        params.append(department)
    if role:
        query += " AND (recipient_role = ? OR recipient_role = 'all')"
        params.append(role)
    if unread_only:
        query += " AND is_read = 0"

    query += " ORDER BY id DESC LIMIT 50"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notification_as_read(notif_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()

def mark_all_notifications_read(department=None):
    conn = get_connection()
    cursor = conn.cursor()
    if department:
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE department = ?", (department,))
    else:
        cursor.execute("UPDATE notifications SET is_read = 1")
    conn.commit()
    conn.close()

def get_analytics_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Open'")
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority IN ('High', 'Critical')")
    high_critical = cursor.fetchone()[0]

    cursor.execute("SELECT department, COUNT(*) as count FROM complaints GROUP BY department")
    dept_rows = cursor.fetchall()
    by_dept = {r["department"]: r["count"] for r in dept_rows}

    cursor.execute("SELECT category, COUNT(*) as count FROM complaints GROUP BY category")
    cat_rows = cursor.fetchall()
    by_cat = {r["category"]: r["count"] for r in cat_rows}

    cursor.execute("SELECT priority, COUNT(*) as count FROM complaints GROUP BY priority")
    prio_rows = cursor.fetchall()
    by_priority = {r["priority"]: r["count"] for r in prio_rows}

    conn.close()
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_critical": high_critical,
        "by_dept": by_dept,
        "by_cat": by_cat,
        "by_priority": by_priority,
    }

def get_department_analytics(dept_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE department = ?", (dept_name,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE department = ? AND status = 'Open'", (dept_name,))
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE department = ? AND status = 'In Progress'", (dept_name,))
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE department = ? AND status = 'Resolved'", (dept_name,))
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE department = ? AND priority IN ('High', 'Critical')", (dept_name,))
    high_critical = cursor.fetchone()[0]

    cursor.execute("SELECT priority, COUNT(*) as count FROM complaints WHERE department = ? GROUP BY priority", (dept_name,))
    prio_rows = cursor.fetchall()
    by_priority = {r["priority"]: r["count"] for r in prio_rows}

    cursor.execute("SELECT AVG(student_rating) FROM complaints WHERE department = ? AND student_rating > 0", (dept_name,))
    avg_rating = cursor.fetchone()[0] or 0.0

    conn.close()
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_critical": high_critical,
        "by_priority": by_priority,
        "avg_rating": round(float(avg_rating), 1)
    }
