import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import database as db
from agents.workflow import run_complaint_pipeline

def test_full_system():
    print("==================================================")
    print("SMART CAMPUS AI - END-TO-END VALIDATION TEST")
    print("==================================================")

    # 1. Database Init
    print("\n[Step 1] Initializing SQLite database...")
    db.init_db()
    print("[OK] Database initialized successfully.")

    # 2. Authentication Checks for All Personas
    print("\n[Step 2] Testing User Authentication for All Personas...")
    admin = db.authenticate_user("admin", "Admin@123")
    assert admin is not None, "Admin authentication failed!"
    assert admin["role"] == "admin"
    print(f"[OK] Central Admin authenticated: {admin['full_name']} (Role: {admin['role']})")

    student = db.authenticate_user("student1", "Student@123")
    assert student is not None, "Student authentication failed!"
    assert student["role"] == "student"
    print(f"[OK] Student authenticated: {student['full_name']} (Role: {student['role']})")

    dept_officer = db.authenticate_user("dept_lab", "Lab@123")
    assert dept_officer is not None, "Department officer authentication failed!"
    print(f"[OK] Department Officer authenticated: {dept_officer['full_name']} (Dept: {dept_officer['department']})")

    # 3. Test LangGraph 5-Agent Workflow with User's Demonstration Case
    print("\n[Step 3] Running 5-Agent LangGraph Workflow with Demonstration Case:")
    test_title = "CSE Laboratory Computers Down"
    test_desc = "The computers in the CSE laboratory are not working and we have a practical examination tomorrow."
    print(f"  Input: '{test_desc}'")

    result = run_complaint_pipeline(
        student_id=student["id"],
        student_name=student["full_name"],
        student_email=student["email"],
        title=test_title,
        description=test_desc
    )

    ticket_id = result["ticket_id"]
    category = result["category"]
    priority = result["priority"]
    dept = result["department"]
    reason = result["priority_reason"]
    status = result["status"]
    needs_rag = result["needs_rag"]
    retrieved_count = len(result.get("retrieved_docs", []))

    print(f"[OK] Ticket Generated: {ticket_id}")
    print(f"[OK] Category: {category} (Expected: Laboratory)")
    print(f"[OK] Priority: {priority} (Expected: High)")
    print(f"[OK] Department: {dept} (Expected: Lab Maintenance)")
    print(f"[OK] Reason: {reason}")
    print(f"[OK] Status: {status} (Expected: Open)")
    print(f"[OK] Agentic RAG Triggered: {needs_rag} (Retrieved: {retrieved_count} docs)")

    assert category == "Laboratory", f"Category mismatch: {category}"
    assert priority == "High", f"Priority mismatch: {priority}"
    assert dept == "Lab Maintenance", f"Department mismatch: {dept}"
    assert "practical examination" in reason.lower() or "examination" in reason.lower(), f"Reason unexpected: {reason}"
    assert status == "Open", f"Status mismatch: {status}"
    assert needs_rag is True, "Agentic RAG should have triggered for examination laboratory scenario"

    # 4. Check In-App Department Notification Generation
    print("\n[Step 4] Verifying Department Alerts & Notifications...")
    lab_notifs = db.get_notifications(department="Lab Maintenance")
    assert len(lab_notifs) >= 1, "Department notification was not generated!"
    print(f"[OK] Lab Maintenance received {len(lab_notifs)} notification(s).")
    print(f"     Title: {lab_notifs[0]['title']}")
    print(f"     Message: {lab_notifs[0]['message']}")

    # 5. Department Officer Assigning Technician
    print("\n[Step 5] Department Officer Assigning Field Technician...")
    ok, msg = db.assign_technician_to_ticket(
        ticket_id=ticket_id,
        technician_name="Robert Vance (Senior Systems Engineer)",
        assigned_by=dept_officer["full_name"],
        notes="Dispatched to CSE Lab 1 to diagnose workstation power supplies and switch."
    )
    assert ok, f"Failed to assign technician: {msg}"
    print(f"[OK] {msg}")

    # 6. Status Transition: Open -> In Progress
    print("\n[Step 6] Updating Status to 'In Progress'...")
    ok, msg = db.update_complaint_status(
        ticket_id=ticket_id,
        new_status="In Progress",
        changed_by=dept_officer["full_name"],
        notes="Engineer on-site inspecting network switch switch-CSE-04 and power lines."
    )
    assert ok, f"Failed to update status: {msg}"
    print(f"[OK] {msg}")

    # 7. Department Portal clicks 'Mark Work Completed' -> Admin Portal marked as RESOLVED
    print("\n[Step 7] Department Officer clicking 'Mark Work Completed'...")
    ok, msg = db.mark_complaint_completed(
        ticket_id=ticket_id,
        completed_by=dept_officer["full_name"],
        notes="Replaced faulty network switch switch-CSE-04 and rebooted 24 workstations. All systems verified and practical exam ready.",
        replaced_parts="24-Port Gigabit Switch (Model GS-24), 4x Cat6 RJ45 Patch Cables"
    )
    assert ok, f"Failed to mark complaint completed: {msg}"
    print(f"[OK] {msg}")

    # Verify Central Admin Portal sees it as RESOLVED
    print("\n[Step 7b] Verifying Central Admin sees status as RESOLVED...")
    admin_view_complaint = db.get_complaint_by_ticket_id(ticket_id)
    assert admin_view_complaint["status"] == "Resolved", f"Status in Central Admin is not Resolved! Got: {admin_view_complaint['status']}"
    assert admin_view_complaint["completed_by_dept"] == 1, "completed_by_dept flag was not set to 1"
    assert "GS-24" in admin_view_complaint["replaced_parts"], "Replaced parts not recorded"
    print(f"[OK] Central Admin confirms ticket {ticket_id} status is: {admin_view_complaint['status']} [Completed by Dept]")

    # Check notification sent to Admin Portal
    admin_notifs = db.get_notifications(role="admin")
    completed_notif = [n for n in admin_notifs if f"Completed by {dept}" in n["title"] or f"Ticket {ticket_id}" in n["title"]]
    assert len(completed_notif) >= 1, "Admin alert for completed ticket was not dispatched!"
    print(f"[OK] Admin Portal received completion notification: '{completed_notif[0]['title']}'")

    # 8. Student Rating and Feedback Submission
    print("\n[Step 8] Student submitting 5-star rating and feedback...")
    ok, msg = db.submit_student_feedback(
        ticket_id=ticket_id,
        rating=5,
        feedback_text="Extremely fast response before our exam! All machines are operational."
    )
    assert ok, f"Failed to submit rating: {msg}"
    print(f"[OK] {msg}")

    # 9. Verify Department Analytics
    print("\n[Step 9] Verifying Department Analytics...")
    dept_stats = db.get_department_analytics("Lab Maintenance")
    print(f"[OK] Lab Maintenance Stats: Total={dept_stats['total']}, Resolved={dept_stats['resolved']}, Rating={dept_stats['avg_rating']}")
    assert dept_stats["total"] >= 1
    assert dept_stats["resolved"] >= 1
    assert dept_stats["avg_rating"] == 5.0

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! NO EMOJIS, 100% FUNCTIONAL")
    print("==================================================")

if __name__ == "__main__":
    test_full_system()
