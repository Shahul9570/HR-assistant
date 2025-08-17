from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from backend.models.candidate import Candidate, JobDescription
from backend.utils.pdf_parser import PDFParser


class ResumeProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.pdf_parser = PDFParser()
        
    def process_resumes(self, resume_files: List[str], job_description: JobDescription) -> List[Candidate]:
        """Process multiple resume files and create candidate objects"""
        candidates = []
        
        for resume_file in resume_files:
            try:
                # Extract text from PDF
                resume_text = self.pdf_parser.extract_text_from_pdf(resume_file)
                if not resume_text:
                    continue
                
                # Extract candidate information
                contact_info = self.pdf_parser.extract_contact_info(resume_text)
                name = self.pdf_parser.extract_name(resume_text)
                skills = self.pdf_parser.extract_skills(resume_text)
                experience = self.pdf_parser.extract_experience_years(resume_text)
                
                # Create candidate object
                candidate = Candidate(
                    name=name,
                    email=contact_info.get('email', 'not_provided@email.com'),
                    phone=contact_info.get('phone'),
                    experience=experience,
                    skills=skills,
                    education="Extracted from resume",
                    resume_text=resume_text,
                    filename=resume_file
                )
                
                # Generate candidate summary
                candidate.summary = self._generate_candidate_summary(candidate, job_description)
                
                candidates.append(candidate)
                
            except Exception as e:
                print(f"Error processing {resume_file}: {str(e)}")
                continue
        
        return candidates
    
    def _generate_candidate_summary(self, candidate: Candidate, job_description: JobDescription) -> str:
        """Generate AI-powered candidate summary"""
        try:
            # Create input text for summarization
            input_text = f"""
            Job Requirements: {job_description.description}
            Required Skills: {', '.join(job_description.required_skills)}
            
            Candidate Profile:
            Name: {candidate.name}
            Experience: {candidate.experience}
            Skills: {', '.join(candidate.skills)}
            Resume Content: {candidate.resume_text[:1000]}...
            """
            
            # Generate summary using BART
            summary = self.summarizer(
                input_text,
                max_length=150,
                min_length=50,
                do_sample=False
            )[0]['summary_text']
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary for {candidate.name}: {str(e)}")
            return f"Candidate with {candidate.experience} experience in {', '.join(candidate.skills[:3])}"
    
    def calculate_similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sentence transformers"""
        try:
            embeddings = self.embedding_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except:
            return 0.0