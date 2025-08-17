import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # HuggingFace Models
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
    
    # Google Calendar API
    GOOGLE_CREDENTIALS_FILE = 'credentials.json'
    GOOGLE_TOKEN_FILE = 'token.json'
    
    # Email settings
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')