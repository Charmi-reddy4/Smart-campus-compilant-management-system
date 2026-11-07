"""
Smart Campus AI - PDF Source Code Generator
Compiles all 30 codebase files into a single publication-grade PDF document.
Uses ReportLab with custom NumberedCanvas for professional pagination.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(BASE_DIR, "Smart_Campus_AI_Full_Source_Code.pdf")

# Ordered list of all project files categorized by module
PROJECT_MODULES = [
    {
        "module_name": "Module 1: Core System Runtime & Database Engine",
        "description": "Main application router, central configuration, SQLite persistence, and test harness.",
        "files": [
            ("app.py", "Streamlit Multi-Page Entry Point, Session State & Navigation Router", "Python"),
            ("config.py", "System Constants, Department Directories, SLA Matrix & Seed Users", "Python"),
            ("database.py", "SQLite Database Schema, PBKDF2 Password Hashing, CRUD & Analytics", "Python"),
            ("test_system.py", "Automated 9-Stage Multi-Agent System Verification Test Suite", "Python"),
            ("requirements.txt", "Python Runtime Dependencies & Package Versions", "Config"),
            (".env.example", "Environment Variables Configuration Template", "Config"),
            (".gitignore", "Git Exclusion Rules for Repository Cleanliness", "Config"),
        ]
    },
    {
        "module_name": "Module 2: LangGraph 5-Agent Multi-Agent System",
        "description": "Autonomous cooperative agents orchestrating complaint understanding, taxonomy, priority scoring, department routing, and ticket generation.",
        "files": [
            ("agents/state.py", "TypedDict ComplaintState Schema for LangGraph Workflow", "Python"),
            ("agents/understanding_agent.py", "Agent 1: Natural Language Complaint Understanding & Intent Extraction", "Python"),
            ("agents/classification_agent.py", "Agent 2: Academic & Facility Taxonomy Classification", "Python"),
            ("agents/priority_agent.py", "Agent 3: Multi-Factor Priority Detection (Low, Med, High, Critical)", "Python"),
            ("agents/routing_agent.py", "Agent 4: Autonomous Department Routing & Ambiguity Detection", "Python"),
            ("agents/ticket_agent.py", "Agent 5: Ticket Creation, Sequential ID Generator & Persistent Alert Dispatch", "Python"),
            ("agents/workflow.py", "LangGraph StateGraph Coordinator with Agentic RAG Dynamic Conditional Edges", "Python"),
        ]
    },
    {
        "module_name": "Module 3: Agentic RAG & Campus Knowledge Base",
        "description": "ChromaDB vector store with feature embedding function, dynamic RAG router, and campus policy documents.",
        "files": [
            ("rag/vector_store.py", "ChromaDB Vector Store with Fast Local Vectorizer & Resilient Fallback", "Python"),
            ("rag/rag_engine.py", "Agentic RAG Dynamic Router, Heuristic Trigger & Context Retriever", "Python"),
            ("knowledge_base/college_policies.md", "Campus Code of Conduct, Student Responsibilities & Exam Contingencies", "Markdown"),
            ("knowledge_base/laboratory_guidelines.md", "Computing Laboratories, Workstation Protocols & Hardware Guidelines", "Markdown"),
            ("knowledge_base/hostel_rules.md", "Residential Living, Maintenance Protocols & Curfew Regulations", "Markdown"),
            ("knowledge_base/department_contacts.md", "Official Campus Department Directory, Room Numbers & Helpdesks", "Markdown"),
            ("knowledge_base/campus_maintenance_procedures.md", "Campus Maintenance SLA Turnaround Matrix & Escalation Levels", "Markdown"),
            ("knowledge_base/complaint_management_policies.md", "Student Grievance Redressal Charter, SLA Guarantees & Appeals", "Markdown"),
        ]
    },
    {
        "module_name": "Module 4: SaaS Presentation Layer & Dedicated Portals",
        "description": "Modern SaaS responsive user interfaces for Students, 7 Department Operations Stations, Central Admin Console, Knowledge Base Browser, and Architecture Visualizer.",
        "files": [
            ("ui/styles.py", "Global SaaS CSS Styling, Metric Card Themes, Badges & Color Palette", "Python"),
            ("ui/landing.py", "Enterprise SaaS Landing Page, Feature Highlights, Department Carousel & Workflow Overview", "Python"),
            ("ui/login_pages.py", "Dedicated Portal Sign-In Screens for Student, Department Staff & Central Admin", "Python"),
            ("ui/student_portal.py", "Student Portal: Complaint Submission, AI Execution Trace, Status Tracking & 5-Star Rating", "Python"),
            ("ui/department_page.py", "Department Operations Field Station: Alerts, Roster Dispatch, Hardware Logs & Work Completion Trigger", "Python"),
            ("ui/admin_dashboard.py", "Central Executive Governance Console: KPIs, Department Analytics, Ticket Triage & Audit Feed", "Python"),
            ("ui/kb_browser.py", "Campus Knowledge Base Browser & Live ChromaDB Semantic Search Engine", "Python"),
            ("ui/workflow_view.py", "Interactive Multi-Agent Architecture Viewer & LangGraph State Machine Diagram", "Python"),
        ]
    }
]

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers and headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Omit headers/footers on cover page
        if self._pageNumber == 1:
            return

        self.saveState()
        page_w, page_h = letter

        # Running Header
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, page_h - 28, "SMART CAMPUS AI - COMPLETE SYSTEM SOURCE CODE SPECIFICATION")
        self.drawRightString(page_w - 36, page_h - 28, "RELEASE: PRODUCTION READY")
        
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(36, page_h - 34, page_w - 36, page_h - 34)

        # Running Footer
        self.line(36, 40, page_w - 36, 40)
        self.setFont("Helvetica", 7.5)
        self.drawString(36, 28, "Smart Campus AI | Python 3.12 - LangGraph - ChromaDB - Streamlit - SQLite")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - 36, 28, page_str)
        self.restoreState()


def build_pdf():
    print(f"[PDF Generator] Output target: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F2744"),
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        alignment=TA_CENTER
    )

    desc_style = ParagraphStyle(
        "CoverDesc",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F2744"),
        spaceBefore=14,
        spaceAfter=6
    )

    file_header_style = ParagraphStyle(
        "FileHeader",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E40AF"),
    )

    file_sub_style = ParagraphStyle(
        "FileSub",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#475569")
    )

    code_style = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=6.5,
        leading=8.0,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("SMART CAMPUS AI", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("INTELLIGENT COMPLAINT MANAGEMENT SYSTEM", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Complete Technical Source Code & Multi-Agent Architecture Specification", desc_style))
    story.append(Spacer(1, 20))

    # Decorative line
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=25, spaceBefore=5))

    # Meta table
    meta_data = [
        ["Project Name", "Smart Campus AI - Intelligent Complaint Management System"],
        ["Primary Stacks", "Python 3.12 | Streamlit | LangGraph | ChromaDB | SQLite"],
        ["Architecture", "5 Cooperative AI Agents + Dynamic Agentic RAG Vector Retrieval"],
        ["Portals Included", "Student Portal | 7 Department Workspaces | Central Admin Console"],
        ["Target Version", "v2.4.0 (GitHub Ready Production Codebase)"],
        ["Database", "SQLite with PBKDF2 Password Hashing & Full Audit Trail"],
        ["Total Codebase", "30 Files | 4,544 Total Lines of Clean Python & Markdown Code"],
        ["Repository Status", "Initialized on 'main' branch, clean .gitignore, zero emojis"]
    ]

    t_meta = Table(meta_data, colWidths=[130, 390])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor("#F8FAFC")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#0F2744")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#1E293B")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
    ]))
    story.append(t_meta)

    story.append(Spacer(1, 25))

    # Architecture summary block
    arch_summary_text = (
        "<b>SYSTEM OVERVIEW:</b> Smart Campus AI is an enterprise-grade academic grievance redressal platform. "
        "It features five cooperative LangGraph agents: <i>Agent 1 (Understanding)</i> decomposes natural-language text; "
        "<i>Agent 2 (Classification)</i> categorizes grievances into 7 campus domains; <i>Agent 3 (Priority)</i> computes "
        "multi-factor urgency scores (Low, Medium, High, Critical) with clear rationales; <i>Agent 4 (Department Routing)</i> "
        "assigns responsible departments and detects ambiguity; and <i>Agent 5 (Ticket & Tracking)</i> generates sequential ticket "
        "identifiers (CAMP-XXXX), writes transactional records, and dispatches in-app alerts to department queues.<br/><br/>"
        "Agentic RAG integrates ChromaDB with campus policy documents to ground priority escalations and department procedures. "
        "Operational field stations for all 7 departments allow technician dispatch, hardware replacement tracking, and immediate "
        "work completion triggers that synchronize across the university governance cockpit."
    )
    p_arch = Paragraph(arch_summary_text, ParagraphStyle('Summary', fontName='Helvetica', fontSize=8, leading=11.5, textColor=colors.HexColor('#334155'), alignment=TA_JUSTIFY))
    
    t_arch = Table([[p_arch]], colWidths=[520])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ('LEFTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # ==========================================
    # 2. TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("TABLE OF CODEBASE MODULES & FILES", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0F2744"), spaceAfter=12, spaceBefore=4))

    toc_data = [["#", "File Path", "Type", "Lines", "Module / Purpose"]]
    item_counter = 1

    for mod in PROJECT_MODULES:
        for rel_path, file_desc, ftype in mod["files"]:
            full_p = os.path.join(BASE_DIR, rel_path)
            line_c = 0
            if os.path.exists(full_p):
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                    line_c = len(f.readlines())
            toc_data.append([
                str(item_counter),
                rel_path,
                ftype,
                f"{line_c} lines",
                file_desc[:58] + "..." if len(file_desc) > 58 else file_desc
            ])
            item_counter += 1

    t_toc = Table(toc_data, colWidths=[20, 140, 45, 55, 260])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F2744")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_toc)

    story.append(PageBreak())

    # ==========================================
    # 3. CODE FILES ITERATION
    # ==========================================
    for mod_idx, mod in enumerate(PROJECT_MODULES, start=1):
        # Module Banner
        story.append(Paragraph(mod["module_name"].upper(), h1_style))
        story.append(Paragraph(f"<b>Overview:</b> {mod['description']}", ParagraphStyle('ModSub', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#475569"))))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=14, spaceBefore=4))

        for rel_path, file_desc, ftype in mod["files"]:
            full_path = os.path.join(BASE_DIR, rel_path)
            if not os.path.exists(full_path):
                continue

            with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                file_lines = fp.readlines()

            line_count = len(file_lines)

            # File Header Table
            fhead_data = [
                [
                    Paragraph(f"<b>FILE: {rel_path}</b>", file_header_style),
                    Paragraph(f"<b>Type:</b> {ftype} | <b>Lines:</b> {line_count}", file_sub_style)
                ],
                [
                    Paragraph(f"<i>{file_desc}</i>", file_sub_style),
                    Paragraph(f"Path: <code>smart_campus_ai/{rel_path}</code>", file_sub_style)
                ]
            ]
            t_fhead = Table(fhead_data, colWidths=[330, 190])
            t_fhead.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor("#CBD5E1")),
            ]))

            story.append(Spacer(1, 6))
            story.append(t_fhead)
            story.append(Spacer(1, 4))

            # Code blocks in chunks of 40 lines to ensure seamless page pagination
            chunk_size = 40
            numbered_lines = [f"{i+1:04d} | {line.rstrip()}" for i, line in enumerate(file_lines)]

            for start_idx in range(0, len(numbered_lines), chunk_size):
                chunk = "\n".join(numbered_lines[start_idx:start_idx + chunk_size])
                pre_block = Preformatted(chunk, code_style)
                
                # Wrap pre_block in a clean bordered container
                t_code = Table([[pre_block]], colWidths=[520])
                t_code.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
                    ('BOX', (0, 0), (0, 0), 0.5, colors.HexColor("#E2E8F0")),
                    ('TOPPADDING', (0, 0), (0, 0), 3),
                    ('BOTTOMPADDING', (0, 0), (0, 0), 3),
                    ('LEFTPADDING', (0, 0), (0, 0), 5),
                    ('RIGHTPADDING', (0, 0), (0, 0), 5),
                ]))
                story.append(t_code)
                story.append(Spacer(1, 3))

            story.append(Spacer(1, 10))
            story.append(PageBreak())

    print(f"[PDF Generator] Compiling story with {len(story)} flowables...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PDF Generator] Successfully generated: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
