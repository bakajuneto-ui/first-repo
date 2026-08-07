# 🎓 MCA Student Score Analyzer

A full-featured, multi-role academic performance management system built with **Python + Streamlit + MongoDB**.

---

## 📸 Features at a Glance

| Role | Capabilities |
|------|-------------|
| 👨‍🎓 **Student** | View marks, percentage, rank, subject charts |
| 👩‍🏫 **Teacher** | Upload/edit marks, view performers, subject analytics |
| 👩‍💼 **Admin** | Full CRUD for students & teachers, system-wide analytics |

---

## 🗂️ Project Structure

```
mca_analyzer/
├── app.py                    # Main entry point (login + routing)
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Theme & server config
│
├── utils/
│   └── database.py           # MongoDB connection, CRUD, analytics
│
├── components/
│   ├── ui.py                 # CSS, sidebar, metric cards
│   └── charts.py             # Plotly chart helpers
│
└── pages/
    ├── student_dashboard.py  # Overview + charts
    ├── student_marks.py      # All-semester marks table
    ├── student_analytics.py  # Performance trend charts
    ├── student_rank.py       # Rank within section/all
    │
    ├── teacher_dashboard.py  # Subject overview
    ├── teacher_upload.py     # Manual entry + Excel upload
    ├── teacher_edit.py       # Edit individual marks
    ├── teacher_analytics.py  # Distribution + grade charts
    ├── teacher_performers.py # Top / avg / low performers
    │
    ├── admin_dashboard.py    # System KPIs + charts
    ├── admin_students.py     # Add/edit/delete students
    ├── admin_teachers.py     # Add/edit/delete/assign teachers
    ├── admin_marks.py        # All marks table view
    └── admin_analytics.py    # Deep analytics + lookup
```

---

## 🗄️ Database Schema (MongoDB Collections)

### `students`
```json
{
  "student_id": "STU1001",
  "name": "Aarav Sharma",
  "username": "aarav1001",
  "password": "<sha256>",
  "roll_number": "1001",
  "section": "A",
  "year": 1,
  "semester": 1,
  "email": "aarav1001@mca.edu"
}
```

### `teachers`
```json
{
  "teacher_id": "TCH001",
  "name": "Prof. Anand Kumar",
  "username": "t_anand",
  "password": "<sha256>",
  "subject_code": "DS101",
  "section": "A",
  "email": "t_anand@mca.edu"
}
```

### `subjects`
```json
{
  "subject_id": "SUB001",
  "code": "DS101",
  "name": "Data Structures",
  "semester": 1,
  "max_marks": 100
}
```

### `marks`
```json
{
  "student_id": "STU1001",
  "subject_code": "DS101",
  "semester": 1,
  "marks_obtained": 87.5,
  "max_marks": 100
}
```

### `admins`
```json
{
  "name": "Dr. Admin",
  "username": "admin",
  "password": "<sha256>"
}
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.9+
- MongoDB 6.0+ (Community Edition)

### 2. Install MongoDB

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Windows:**
Download from https://www.mongodb.com/try/download/community and run the installer.

**Verify:**
```bash
mongosh   # should open MongoDB shell
```

### 3. Clone / Download the Project

```bash
# If using git:
git clone <repo-url>
cd mca_analyzer

# Or just navigate to the project folder:
cd path/to/mca_analyzer
```

### 4. Create a Virtual Environment

```bash
python -m venv venv

# Activate:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure MongoDB URI (Optional)

By default the app connects to `mongodb://localhost:27017/`.

To use a remote MongoDB (e.g., MongoDB Atlas):
```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
```
Or set it in a `.env` file and load with `python-dotenv`.

### 7. Run the App

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 🔐 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| 👨‍🎓 Student | `aarav1001` | `pass1001` |
| 👩‍🏫 Teacher | `t_anand` | `tpass1` |
| 👩‍💼 Admin | `admin` | `admin123` |

> All 40 student accounts follow the pattern: `<firstname><roll>` / `pass<roll>`  
> e.g., `bhavya1002` / `pass1002`, `chirag1003` / `pass1003`

---

## 👥 Sample Data Overview

| Entity | Count |
|--------|-------|
| Students | 40 (4 sections × 10) |
| Sections | A, B, C, D |
| Quarters | 4 |
| Subjects | 16 (4 per quarter) |
| Teachers | 12 |
| Mark Records | 640 (auto-generated) |

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.32+, Custom CSS |
| Charts | Plotly Express & Graph Objects |
| Backend | Python 3.9+ |
| Database | MongoDB 6+ |
| Auth | SHA-256 password hashing |
| Data | Pandas, OpenPyXL |

---

## 📊 Feature Checklist

### Student
- [x] Multi-role login with toggle
- [x] Subject-wise marks view (all semesters)
- [x] Overall percentage calculation
- [x] Semester-wise rank
- [x] Pie chart (subject distribution)
- [x] Bar chart (marks comparison)
- [x] Semester trend line chart

### Teacher
- [x] Manual mark entry (form)
- [x] Excel upload (template download + upload)
- [x] Edit individual student marks
- [x] View assigned subject & section only
- [x] Top performers list + chart
- [x] Average performers list
- [x] Least performers list
- [x] Marks distribution histogram
- [x] Grade distribution pie chart
- [x] Class average, high, low, pass rate KPIs

### Admin
- [x] Add / update / delete students
- [x] Add / update / delete teachers
- [x] Assign subjects & sections to teachers
- [x] View all marks (section + semester filter)
- [x] Rank table with topper highlight
- [x] CSV export for marks/ranks
- [x] Section comparison bar chart
- [x] Section radar chart
- [x] Subject averages across sections
- [x] Top 3 podium display
- [x] Individual student lookup with charts
- [x] System-wide KPI dashboard

---

## 🔧 Customization

**Add a new subject:**
```python
db.subjects.insert_one({
    "subject_id": "SUB017",
    "code": "AI501",
    "name": "Artificial Intelligence",
    "semester": 3,
    "max_marks": 100
})
```

**Change max marks for a subject:**
```python
db.subjects.update_one(
    {"code": "DS101"},
    {"$set": {"max_marks": 75}}
)
```

**Reset database:**
```bash
mongosh mca_analyzer --eval "db.dropDatabase()"
# Restart the app – it will re-seed automatically
```

---

## 🚀 Deployment (Optional)

### Streamlit Community Cloud
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect repo, set `app.py` as entry point
4. Add `MONGO_URI` in Secrets

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `Connection refused` to MongoDB | Run `mongod` or `brew services start mongodb-community` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| App shows blank page | Check terminal for errors; try `streamlit run app.py --logger.level=debug` |
| Login fails | Make sure DB is running; app auto-seeds on first launch |
| Charts not showing | Ensure `plotly` is installed: `pip install plotly` |

---

## 📄 License

MIT License – free to use, modify, and distribute.

---

*Built with ❤️ using Python + Streamlit + MongoDB*
