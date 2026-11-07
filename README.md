# Smart Campus AI - Intelligent Complaint Management System

An enterprise-grade, agentic AI-powered complaint management web platform built with Streamlit, LangGraph, ChromaDB, and SQLite.

The system autonomously analyzes student grievances in natural language, identifies problem categories, computes multi-factor priority scores, dynamically retrieves campus policy context using Agentic RAG, dispatches real-time alerts to responsible campus departments, and provides department specialists and central administrators with dedicated management consoles.

---

## Key Capabilities

### 1. Separate Portals & Dedicated Login Pages
- **Dedicated Student Login & Registration**: Clean, separate portal with roll number, academic department, and PBKDF2 password protection.
- **Dedicated Department Officer Sign In**: Specialized portal for each of the 7 campus departments to manage localized queues, assign field technicians, and log repairs.
- **Dedicated Central Administrator Sign In**: Campus-wide governance cockpit for university leadership, compliance metrics, and cross-department escalations.
- **Authentication Gateway**: Central hub allowing direct access to any persona login screen.

### 2. Dedicated Pages for Every Department
Independent operations workspaces with custom color themes, staff rosters, and SLA targets:
1. **Lab Maintenance** (Tech Cyan - #0284C7): Computing laboratories, workstation BIOS, compiler environments, exam emergencies.
2. **Hostel Administration** (Vibrant Indigo - #4F46E5): Dormitory living, residential plumbing, dining hall hygiene, room allocation, curfew.
3. **Estate & Facilities** (Emerald Green - #059669): Civil infrastructure, classroom fixtures, electrical lines, water mains, HVAC.
4. **IT Support** (Electric Violet - #7C3AED): Campus Wi-Fi accounts, student portals, email systems, core server infrastructure.
5. **Library Services** (Warm Amber - #D97706): Quiet reading rooms, book lending kiosks, RFID turnstiles, digital research catalog.
6. **Transport Office** (Deep Sunset Orange - #EA580C): Campus transit shuttles, bus route schedules, driver coordination, vehicle breakdowns.
7. **Academic Affairs** (Rose Crimson - #E11D48): Lecture hall assignments, exam conflict escalations, faculty grievance coordination.

### 3. Department Notification & Inbound Alert System
- **Real-Time Department Alerts**: In-app notifications automatically dispatched to department administrators when complaints are routed to their queue.
- **Urgency Indicator**: Prominent alert banners for High and Critical emergencies (e.g. electrical hazards, impending exams).
- **Acknowledge & Mark Read**: Instant notification tracking and unread counter badges.

### 4. Advanced Triage & Resolution Workflow
- **Field Technician Assignment**: Assign named senior engineers and specialists from the department roster to any ticket.
- **SLA Countdown & Tracking**: Target turnaround hours calculated dynamically (Critical: 4h, High: 12h, Medium: 48h, Low: 96h).
- **Enforced Resolution Reports**: Status cannot be marked as Resolved without documented diagnostic notes.
- **Student Satisfaction Rating (1 to 5 Stars)**: Enrolled students can rate resolution quality and leave satisfaction feedback.
- **CSV Data Export**: Download department and central ticket records directly into CSV.

### 5. Five Specialized LangGraph AI Agents
1. **Agent 1 - Complaint Understanding Agent**: Parses unstructured student text to extract core issues, affected facilities, and urgency indicators.
2. **Agent 2 - Complaint Classification Agent**: Classifies tickets into canonical taxonomies (Laboratory, Hostel, Classroom, Library, Transport, Infrastructure, Other).
3. **Agent 3 - Priority Detection Agent**: Evaluates safety hazards, examination timelines, and facility disruption to assign Low, Medium, High, or Critical priority with clear rationales.
4. **Agent 4 - Department Routing Agent**: Automatically dispatches complaints to responsible departments. Flags ambiguous cases for administrator review.
5. **Agent 5 - Ticket & Resolution Tracking Agent**: Generates sequential ticket IDs (CAMP-XXXX), writes persistent records into SQLite, and dispatches department alerts.

### 6. Agentic RAG Knowledge Base (ChromaDB)
- **Agentic Router**: Workflow dynamically evaluates whether campus policy retrieval is needed before routing.
- **Campus Knowledge Base**:
  - `college_policies.md`: Code of conduct, emergency contacts, exam contingency rules.
  - `laboratory_guidelines.md`: Computing laboratory protocols, practical exam emergency readiness, lab technician contacts.
  - `hostel_rules.md`: Residential maintenance, quiet hours, plumbing, and electrical escalation.
  - `department_contacts.md`: Institutional department directory, operating hours, and locations.
  - `campus_maintenance_procedures.md`: SLA turnaround matrix.
  - `complaint_management_policies.md`: Student grievance charter and resolution procedures.
- **Zero Hallucination**: AI relies strictly on retrieved policy passages for institutional rules and technician contacts.

---

## Project Structure

```
smart_campus_ai/
├── app.py                      # Main Streamlit application entry point & routing
├── config.py                   # Central configuration & path management
├── database.py                 # SQLite database schema, password hashing & queries
├── requirements.txt            # Python dependencies (Streamlit, LangGraph, ChromaDB, etc.)
├── .env.example                # Environment variables template
├── README.md                   # Complete documentation
├── test_system.py              # Automated end-to-end verification test suite
│
├── knowledge_base/             # Campus Knowledge Base Markdown Documents
│   ├── college_policies.md                 # Campus code of conduct & exam contingency rules
│   ├── laboratory_guidelines.md            # Lab hardware maintenance & exam readiness
│   ├── hostel_rules.md                     # Residential maintenance & curfew guidelines
│   ├── department_contacts.md              # Official campus department directory & emails
│   ├── campus_maintenance_procedures.md    # SLA turnaround matrix (Critical: 4h, High: 12h)
│   └── complaint_management_policies.md    # Grievance redressal charter & verification
│
├── rag/                        # Retrieval-Augmented Generation Module
│   ├── __init__.py
│   ├── vector_store.py         # ChromaDB vector store with feature embeddings
│   └── rag_engine.py           # Agentic RAG dynamic decision router & retriever
│
├── agents/                     # LangGraph Multi-Agent Orchestration
│   ├── __init__.py
│   ├── state.py                # TypedDict ComplaintState definition
│   ├── understanding_agent.py  # Agent 1: Complaint Understanding Agent
│   ├── classification_agent.py # Agent 2: Complaint Classification Agent
│   ├── priority_agent.py       # Agent 3: Priority Detection Agent
│   ├── routing_agent.py        # Agent 4: Department Routing Agent
│   ├── ticket_agent.py         # Agent 5: Ticket and Resolution Tracking Agent
│   └── workflow.py             # Compiled LangGraph StateGraph pipeline
│
├── ui/                         # Modern SaaS Presentation Layer (Zero Emojis)
│   ├── __init__.py
│   ├── styles.py               # Color palette, responsive SaaS cards & badges
│   ├── landing.py              # Landing page, department carousel & workflow
│   ├── login_pages.py          # Dedicated login pages for Student, Dept, Admin
│   ├── student_portal.py       # Student registration/login, complaint form & rating
│   ├── department_page.py      # Dedicated operations dashboard for every department
│   ├── admin_dashboard.py      # Central KPI cards, charts, triage & global feed
│   ├── kb_browser.py           # Knowledge base viewer & live ChromaDB search
│   └── workflow_view.py        # 5-Agent architecture visualizer
│
└── uploads/                    # Local storage for user evidence attachments
```

---

## Installation & Execution

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12)

### 2. Setup Virtual Environment (Recommended)
```bash
cd smart_campus_ai
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
```bash
cp .env.example .env
```
Open `.env` and set:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
> Note: If `OPENAI_API_KEY` is omitted, the application runs on its built-in rule and NLP engine, guaranteeing 100% operational functionality without external API tokens.

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Default Accounts & Credentials

The SQLite database is pre-seeded with all departmental, student, and admin accounts:

| Portal | Username | Password | Full Name / Scope |
|---|---|---|---|
| Central Administrator | `admin` | `Admin@123` | Campus Administrator |
| Student Portal | `student1` | `Student@123` | Alex Johnson (CSE Dept) |
| Lab Maintenance | `dept_lab` | `Lab@123` | Robert Vance (Lead Engineer) |
| Hostel Administration | `dept_hostel` | `Hostel@123` | Dr. Sarah Jenkins (Chief Warden) |
| Estate & Facilities | `dept_estate` | `Estate@123` | David Kumar (Facilities Director) |
| IT Support | `dept_it` | `IT@123` | Priya Patel (Lead Network Admin) |
| Library Services | `dept_library` | `Library@123` | Prof. Michael Chang (Chief Librarian) |
| Transport Office | `dept_transport` | `Transport@123` | Capt. Arvind Singh (Transit Director) |
| Academic Affairs | `dept_academic` | `Academic@123` | Dean Dr. Eleanor Ross (Academic Dean) |

---

## Demonstration Walkthrough

1. Navigate to **Student Portal** (or click **Test Exam Scenario** in the sidebar).
2. Input:
   - **Title**: `CSE Laboratory Computers Out of Service`
   - **Description**: `The computers in the CSE laboratory are not working and we have a practical examination tomorrow.`
3. Click **Submit Complaint to AI Agent Workflow**.
4. Observe the AI output:
   - **Category**: `Laboratory`
   - **Priority**: `High`
   - **Responsible Department**: `Lab Maintenance`
   - **Reason**: `Practical examination is tomorrow and laboratory computers are unavailable.`
   - **Ticket ID**: `CAMP-0001`
   - **Status**: `Open`
   - **Department Notification**: In-app alert dispatched to Lab Maintenance.
5. Switch to **Department Operations** (select `Lab Maintenance`), view the unread alert, assign technician `Robert Vance`, update status to `In Progress`, and post resolution notes to mark it `Resolved`.
6. Return to **Student Portal** -> **Track Ticket Status** to see the technician notes and submit a 5-star resolution rating.
