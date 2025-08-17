from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from typing import List, Dict, Optional

from backend.agents.resume_processor import ResumeProcessor
from backend.agents.candidate_ranker import CandidateRanker
from backend.agents.scheduler import InterviewScheduler
from backend.agents.email_agent import EmailAgent
from backend.models.candidate import JobDescription
from config.config import Config

# Tell Flask to use frontend/templates and frontend/static
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config.from_object(Config)

# Initialize agents
resume_processor = ResumeProcessor()
candidate_ranker = CandidateRanker()
scheduler = InterviewScheduler()
email_agent = EmailAgent()

# Global variables to store state
current_job_description: Optional[JobDescription] = None
processed_candidates: List = []
ranked_candidates: List = []
selected_candidates: List = []

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Main page with job description input and resume upload"""
    return render_template('index.html')


@app.route('/api/process_job', methods=['POST'])
def process_job():
    """Process job description and uploaded resumes"""
    global current_job_description, processed_candidates, ranked_candidates
    
    try:
        # Get job description data
        job_data = request.form.to_dict()
        
        # Create JobDescription object
        current_job_description = JobDescription(
            title=job_data.get('job_title', ''),
            description=job_data.get('job_description', ''),
            required_skills=[s.strip() for s in job_data.get('required_skills', '').split(',') if s.strip()],
            experience_required=job_data.get('experience_required', ''),
            qualifications=job_data.get('qualifications', '')
        )
        
        # Handle uploaded files
        uploaded_files = request.files.getlist('resumes')
        resume_paths = []
        
        for file in uploaded_files:
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                resume_paths.append(file_path)
        
        if not resume_paths:
            return jsonify({'error': 'No valid PDF files uploaded'}), 400
        
        # Process resumes
        processed_candidates = resume_processor.process_resumes(
            resume_paths, current_job_description
        )
        
        # Rank candidates
        ranked_candidates = candidate_ranker.rank_candidates(
            processed_candidates, current_job_description
        )
        
        # Prepare response data
        candidates_data = []
        for candidate in ranked_candidates:
            candidates_data.append({
                'name': candidate.name,
                'email': candidate.email,
                'phone': getattr(candidate, "phone", None) or 'Not provided',
                'experience': getattr(candidate, "experience", ''),
                'skills': getattr(candidate, "skills", []),
                'skill_match_score': round(float(candidate.skill_match_score) * 100, 2),
                'experience_score': round(float(candidate.experience_score) * 100, 2),
                'overall_score': round(float(candidate.overall_score) * 100, 2),
                'summary': getattr(candidate, "summary", ''),
                'filename': os.path.basename(getattr(candidate, "filename", ""))
            })
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(candidates_data)} candidates',
            'candidates': candidates_data,
            'job_title': current_job_description.title
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/select_candidates', methods=['POST'])
def select_candidates():
    """Select top candidates for interview"""
    global selected_candidates
    
    try:
        data = request.get_json() or {}
        selected_names = data.get('selected_candidates', [])
        
        # If the frontend sends objects here by mistake, normalize to names
        if selected_names and isinstance(selected_names[0], dict):
            selected_names = [c.get('name') for c in selected_names if c.get('name')]
        
        # Get selected candidates from ranked list
        selected_candidates = [
            candidate for candidate in ranked_candidates 
            if candidate.name in selected_names
        ]
        
        return jsonify({
            'success': True,
            'message': f'Selected {len(selected_candidates)} candidates for interview',
            'selected_count': len(selected_candidates)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule_interviews', methods=['POST'])
def schedule_interviews():
    """Schedule interviews for selected candidates based on HR's chosen start date."""
    global selected_candidates
    
    try:
        if not selected_candidates:
            return jsonify({'error': 'No candidates selected'}), 400
        
        data = request.get_json() or {}
        start_date_str = data.get('start_date')
        
        if not start_date_str:
            return jsonify({'error': 'Start date not provided'}), 400

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Schedule interviews (auto spread by scheduler.py)
        scheduling_result = scheduler.schedule_interviews(
            selected_candidates,
            start_date=start_date
        )
        
        # Get interview summary
        interview_summary = scheduler.get_interview_summary(selected_candidates)
        
        return jsonify({
            'success': True,
            'message': f'Scheduled {scheduling_result["scheduled_count"]} interviews',
            'scheduling_result': scheduling_result,
            'interview_summary': interview_summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/send_confirmations', methods=['POST'])
def send_confirmations():
    """Send interview confirmation emails"""
    global selected_candidates
    
    try:
        if not selected_candidates:
            return jsonify({'error': 'No candidates selected'}), 400
        
        # Send confirmation emails
        email_result = email_agent.send_interview_confirmations(selected_candidates)
        
        return jsonify({
            'success': True,
            'message': f'Sent {email_result["sent_count"]} confirmation emails',
            'email_result': email_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_status')
def get_status():
    """Get current processing status"""
    return jsonify({
        'job_posted': current_job_description is not None,
        'candidates_processed': len(processed_candidates),
        'candidates_ranked': len(ranked_candidates),
        'candidates_selected': len(selected_candidates),
        'interviews_scheduled': len([c for c in selected_candidates if getattr(c, "interview_scheduled", False)])
    })


if __name__ == '__main__':
    # Note: app still serves templates from ../frontend/templates and static from ../frontend/static
    app.run(debug=True, host='0.0.0.0', port=5000)
