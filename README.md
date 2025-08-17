# HR AI Agent - Automated Resume Screening System

An intelligent HR automation system that screens job applicants, ranks candidates using AI, schedules interviews, and sends confirmation emails.

## 🚀 Features

- **AI-Powered Resume Screening**: Uses HuggingFace transformers for intelligent resume analysis
- **Automated Candidate Ranking**: Scores candidates based on skills match, experience, and overall fit
- **Interview Scheduling**: Integrates with Google Calendar for automated interview scheduling
- **Email Notifications**: Sends personalized confirmation emails to selected candidates
- **Modern Web Interface**: Responsive UI built with Bootstrap 5
- **Modular Architecture**: Clean, extensible codebase with separate agent modules

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **AI/ML**: HuggingFace Transformers, Sentence Transformers, scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF Processing**: PyPDF2
- **Calendar Integration**: Google Calendar API
- **Email**: SMTP (Gmail)

## 📋 Prerequisites

- Python 3.8+
- Gmail account with App Password
- Google Cloud Project with Calendar API enabled
- Git

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hr-ai-agent.git
cd hr-ai-agent
```
2. **Create virtual environment**

bashpython -m venv hr_agent_env
source hr_agent_env/bin/activate  # On Windows: hr_agent_env\Scripts\activate

Install dependencies

bashpip install -r backend/requirements.txt

Configure environment variables

bashcp .env.example .env
# Edit .env with your credentials

Setup Google Calendar API


Download credentials.json from Google Cloud Console
Place in project root directory


3. **Run the application**

bashpython run.py
Visit http://localhost:5000 in your browser.
🎯 Usage

Post Job Description: Enter job title, description, required skills, and qualifications
Upload Resumes: Select multiple PDF resume files
AI Processing: System automatically extracts information and ranks candidates
Select Candidates: Choose top candidates for interviews
Schedule Interviews: Automatically create calendar events
Send Confirmations: Email selected candidates with interview details

🏗️ Architecture
hr_ai_agent/
├── backend/
│   ├── agents/          # AI agent modules
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   └── app.py          # Flask application
├── frontend/
│   ├── templates/       # HTML templates
│   └── static/         # CSS and JavaScript
├── config/             # Configuration files
└── uploads/            # Resume uploads
🤖 Agent Workflow

Resume Processor: Extracts text from PDFs, identifies key information
Candidate Ranker: Uses AI to score and rank candidates
Interview Scheduler: Integrates with Google Calendar
Email Agent: Sends personalized confirmation emails

📊 Scoring System
Candidates are scored based on:

Skills Match (40%): Alignment with required skills
Experience Relevance (30%): Years and type of experience
Overall Fit (30%): Resume content similarity to job description