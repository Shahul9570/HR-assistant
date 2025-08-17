# 🤖 HR AI Agent – Automated Resume Screening & Interview Scheduler

An AI-powered HR Assistant that automates **resume screening, candidate ranking, and interview scheduling** with Google Calendar integration and email confirmations.  

---

## ✨ Features
- 📄 **Resume Processing**: Upload multiple resumes in PDF format.
- 🧠 **AI-based Candidate Ranking**: Matches skills, experience, and job requirements.
- 📊 **Candidate Dashboard**: Displays ranking, scores, and extracted details.
- 📅 **Smart Scheduling**:
  - HR selects a start date.
  - Interviews are auto-assigned from 9 AM – 5 PM (Mon–Fri).
  - Remaining candidates spill over to next working day.
- 📧 **Email Confirmations**: Sends interview invites & Google Meet links.
- 🔒 **Secure Configuration**: Uses `.env` for sensitive credentials.

---

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML, Bootstrap, JavaScript
- **AI**: NLP-based resume screening and ranking
- **Database**: (In-memory for MVP, can be extended to MongoDB/Postgres)
- **Integrations**:
  - Google Calendar API (for scheduling)
  - Gmail SMTP (for sending confirmation emails)

---

## 📂 Project Structure
hr_ai_agent/
│── backend/
│ ├── agents/ # AI agents (resume processor, ranker, scheduler, email agent)
│ ├── models/ # Candidate & job description models
│ └── utils/ # Calendar & helper utilities
│
│── config/
│ └── config.py # Config management (loads .env)
│
│── frontend/
│ ├── static/
│ │ ├── script.js # Frontend logic
│ │ └── style.css # Custom styling
│ └── templates/
│ └── index.html # Main UI template
│
│── uploads/ # Resume uploads (ignored by git)
│── app.py # Flask app entrypoint
│── requirements.txt # Python dependencies
│── .env.example # Example env file
│── .gitignore # Git ignore rules
│── README.md # Project docs


---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/hr_ai_agent.git
cd hr_ai_agent

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # Mac/Linux
3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
UPLOAD_FOLDER=uploads

# Google API
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback

# Gmail SMTP
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

5️⃣ Run the App
python app.py


App will start at → http://127.0.0.1:5000

📌 Usage

Enter Job Description.

Upload PDF resumes.

Click Process Resumes → AI ranks candidates.

Select candidates.

Choose a start date → System auto schedules interviews (9–5, Mon–Fri).

Send confirmation emails with Google Meet links.