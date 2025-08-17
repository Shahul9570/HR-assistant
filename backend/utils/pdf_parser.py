import PyPDF2
import re
from typing import Dict, List, Optional

class PDFParser:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract email and phone from resume text"""
        email_matches = re.findall(self.email_pattern, text)
        phone_matches = re.findall(self.phone_pattern, text)
        
        return {
            'email': email_matches[0] if email_matches else None,
            'phone': phone_matches[0] if phone_matches else None
        }
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name (first few words of the resume)"""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 0 and not any(char.isdigit() for char in line):
                # Skip email addresses and common headers
                if '@' not in line and len(line.split()) <= 3:
                    return line
        return "Unknown"
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'sql', 'mongodb', 'postgresql', 'mysql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'data science', 'pandas', 'numpy', 'scikit-learn', 'html', 'css',
            'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
                
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience_years(self, text: str) -> str:
        """Extract years of experience from resume"""
        # Look for patterns like "5 years", "2+ years", etc.
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience[:\s]*(\d+)\+?\s*years?'
        ]
        
        text_lower = text.lower()
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                return f"{matches[0]} years"
        
        return "Not specified"