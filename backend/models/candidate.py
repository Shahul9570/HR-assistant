from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Candidate:
    name: str
    email: str
    phone: Optional[str]
    experience: str
    skills: List[str]
    education: str
    resume_text: str
    filename: str
    
    # Scoring attributes
    skill_match_score: float = 0.0
    experience_score: float = 0.0
    overall_score: float = 0.0
    summary: str = ""
    
    # Interview attributes
    interview_scheduled: bool = False
    interview_datetime: Optional[datetime] = None
    interview_link: Optional[str] = None

@dataclass
class JobDescription:
    title: str
    description: str
    required_skills: List[str]
    experience_required: str
    qualifications: str