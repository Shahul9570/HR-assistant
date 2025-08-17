import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from ..models.candidate import Candidate, JobDescription

class CandidateRanker:
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.weights = {
            'skills_match': 0.4,
            'experience_relevance': 0.3,
            'overall_fit': 0.3
        }
    
    def rank_candidates(self, candidates: List[Candidate], job_description: JobDescription) -> List[Candidate]:
        """Rank candidates based on job description matching"""
        
        for candidate in candidates:
            # Calculate individual scores
            skills_score = self._calculate_skills_match(candidate, job_description)
            experience_score = self._calculate_experience_relevance(candidate, job_description)
            overall_fit_score = self._calculate_overall_fit(candidate, job_description)
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * self.weights['skills_match'] +
                experience_score * self.weights['experience_relevance'] +
                overall_fit_score * self.weights['overall_fit']
            )
            
            # Update candidate scores
            candidate.skill_match_score = skills_score
            candidate.experience_score = experience_score
            candidate.overall_score = overall_score
        
        # Sort candidates by overall score (descending)
        ranked_candidates = sorted(candidates, key=lambda x: x.overall_score, reverse=True)
        
        return ranked_candidates
    
    def _calculate_skills_match(self, candidate: Candidate, job_description: JobDescription) -> float:
        """Calculate how well candidate skills match job requirements"""
        try:
            if not candidate.skills or not job_description.required_skills:
                return 0.0
            
            candidate_skills_text = ' '.join(candidate.skills).lower()
            required_skills_text = ' '.join(job_description.required_skills).lower()
            
            # Use embedding similarity
            similarity = self._get_text_similarity(candidate_skills_text, required_skills_text)
            
            # Also check for direct skill matches
            matched_skills = 0
            for req_skill in job_description.required_skills:
                for cand_skill in candidate.skills:
                    if req_skill.lower() in cand_skill.lower() or cand_skill.lower() in req_skill.lower():
                        matched_skills += 1
                        break
            
            direct_match_score = matched_skills / len(job_description.required_skills) if job_description.required_skills else 0
            
            # Combine similarity and direct matches
            final_score = 0.6 * similarity + 0.4 * direct_match_score
            return min(final_score, 1.0)
            
        except Exception as e:
            print(f"Error calculating skills match for {candidate.name}: {str(e)}")
            return 0.0
    
    def _calculate_experience_relevance(self, candidate: Candidate, job_description: JobDescription) -> float:
        """Calculate experience relevance score"""
        try:
            # Extract years from experience string
            experience_years = self._extract_years_from_text(candidate.experience)
            required_years = self._extract_years_from_text(job_description.experience_required)
            
            if experience_years == 0:
                return 0.3  # Some base score for unclear experience
            
            if required_years == 0:
                return 0.7  # Default score when requirement is unclear
            
            # Calculate score based on experience match
            if experience_years >= required_years:
                # Bonus for more experience, but with diminishing returns
                excess_years = experience_years - required_years
                bonus = min(excess_years * 0.05, 0.3)  # Max 30% bonus
                return min(1.0, 0.8 + bonus)
            else:
                # Penalty for less experience
                shortage = required_years - experience_years
                penalty = min(shortage * 0.15, 0.6)  # Max 60% penalty
                return max(0.1, 0.8 - penalty)
                
        except Exception as e:
            print(f"Error calculating experience relevance for {candidate.name}: {str(e)}")
            return 0.5
    
    def _calculate_overall_fit(self, candidate: Candidate, job_description: JobDescription) -> float:
        """Calculate overall fit using resume text and job description"""
        try:
            # Use first 1000 characters of resume for efficiency
            candidate_text = candidate.resume_text[:1000]
            job_text = job_description.description
            
            similarity = self._get_text_similarity(candidate_text, job_text)
            return similarity
            
        except Exception as e:
            print(f"Error calculating overall fit for {candidate.name}: {str(e)}")
            return 0.0
    
    def _get_text_similarity(self, text1: str, text2: str) -> float:
        """Get similarity between two texts using sentence transformers"""
        try:
            embeddings = self.embedding_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def _extract_years_from_text(self, text: str) -> int:
        """Extract number of years from text"""
        if not text:
            return 0
            
        import re
        # Look for patterns like "5 years", "2+ years", etc.
        pattern = r'(\d+)\+?\s*years?'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            return int(matches[0])
        
        return 0
    
    def get_top_candidates(self, ranked_candidates: List[Candidate], top_n: int = 5) -> List[Candidate]:
        """Get top N candidates"""
        return ranked_candidates[:top_n]