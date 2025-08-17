from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_sample_resume(name, skills, experience, filename):
    """Create a sample PDF resume for testing"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, name)
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, f"Email: {name.lower().replace(' ', '.')}@email.com")
    c.drawString(100, height - 150, "Phone: +1-555-0123")
    
    # Experience
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 200, "Experience:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 230, f"{experience} of experience in software development")
    
    # Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 280, "Skills:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 310, f"Technical Skills: {skills}")
    
    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 360, "Education:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 390, "Bachelor's Degree in Computer Science")
    
    c.save()

# Generate sample resumes
sample_candidates = [
    ("John Smith", "Python, Machine Learning, TensorFlow, SQL", "5 years"),
    ("Jane Doe", "Python, Django, React, PostgreSQL", "3 years"),
    ("Mike Johnson", "Java, Spring Boot, MySQL, Docker", "4 years"),
    ("Sarah Wilson", "Python, Data Science, Pandas, Scikit-learn", "6 years"),
    ("David Brown", "JavaScript, Node.js, MongoDB, AWS", "2 years")
]

os.makedirs('sample_resumes', exist_ok=True)

for name, skills, exp in sample_candidates:
    filename = f"sample_resumes/{name.replace(' ', '_')}_resume.pdf"
    create_sample_resume(name, skills, exp, filename)
    print(f"Created: {filename}")

print("Sample resumes generated successfully!")