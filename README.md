# 🎓 Student Deadline Tracker (AI Agent)

An AI-powered academic concierge that extracts, organizes, and categorizes academic deadlines from text inputs or uploaded files. This agent leverages **Google's Agent Development Kit (ADK)**, the **Gemini 2.5 Flash** model, and a **FastMCP File Reader** to automate deadline tracking.

---

## 🛠️ Architecture

```
User Input (Text / .txt file)
        │
        ▼
   Streamlit App (app.py)
        │
        ▼
 Deadline Agent (agents/deadline_agent.py)
        │
        ├── Uses ──► MCP File Reader (mcp/file_reader.py)
        ▼
 Deadline Extractor (Gemini 2.5 Flash)
        │
        ▼
 Priority Categorizer (utils/date_parser.py)
        │
        ▼
 Results Dashboard (Urgent, Upcoming, Future, Overdue)
```

---

## 📋 Features

- **Text Input**: Paste any syllabus content, course announcement, assignment checklist, or homework email.
- **File Upload**: Drop a `.txt` file containing academic information.
- **Automated Extraction**: Uses Gemini 2.5 Flash to automatically detect:
  - Event Name
  - Event Type (Assignment, Exam, Scholarship, Fee Payment, Project, Other)
  - Deadline Date (accurately resolves relative phrases like "tomorrow", "next Monday", "July 5")
- **Visual Urgency Dashboard**: Automatically groups tasks into:
  - 🚨 **Urgent**: Due within 1 day.
  - 📅 **Upcoming**: Due within 7 days.
  - 🌟 **Future**: Due in more than 7 days.
  - ⚠️ **Overdue**: Deadlines that have already passed.

---

## 📂 Project Structure

```
student-deadline-tracker/
├── app.py                     # Streamlit dashboard and UI
├── requirements.txt           # Python project dependencies
├── README.md                  # Project documentation
├── agents/
│   └── deadline_agent.py      # Google ADK agent and runner configuration
├── mcp/
│   └── file_reader.py         # FastMCP server for reading uploaded files
└── utils/
    └── date_parser.py         # Date parsing and prioritization logic
```

---

## 🚀 Quick Start & Setup

Follow these steps to run the application locally:

### 1. Prerequisites
- Python 3.10 or later
- A Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation

1. Navigate to the project folder:
   ```bash
   cd student-deadline-tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

Create a `.env` file in the root folder (`student-deadline-tracker/`) and add your Gemini API key:
```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```
*Note: You can also input your API Key directly in the Streamlit Sidebar during execution.*

### 4. Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
This will open the dashboard in your web browser (typically at `http://localhost:8501`).

---

## 💡 Example Usage

**Pasted Text Input:**
```text
Assignment submission on July 5.
Physics exam on July 10.
Scholarship application deadline July 15.
Fee payment tomorrow.
```

**Extracted Dashboard Results:**
- **Urgent**: `Fee Payment` (Due Tomorrow)
- **Future**: `Assignment submission` (Due July 5), `Physics exam` (Due July 10), `Scholarship application` (Due July 15)
