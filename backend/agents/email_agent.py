import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
from backend.models.candidate import Candidate
from config.config import Config


class EmailAgent:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        
    def send_interview_confirmations(self, candidates: List[Candidate]) -> Dict[str, any]:
        """Send interview confirmation emails to selected candidates"""
        
        sent_count = 0
        failed_sends = []
        
        for candidate in candidates:
            if candidate.interview_scheduled:
                success = self._send_individual_confirmation(candidate)
                if success:
                    sent_count += 1
                else:
                    failed_sends.append(candidate.name)
        
        return {
            'sent_count': sent_count,
            'total_candidates': len([c for c in candidates if c.interview_scheduled]),
            'failed_sends': failed_sends
        }
    
    def _send_individual_confirmation(self, candidate: Candidate) -> bool:
        """Send confirmation email to individual candidate"""
        try:
            # Create email content
            subject = f"Interview Confirmation - {candidate.name}"
            body = self._generate_email_body(candidate)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = candidate.email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                text = msg.as_string()
                server.sendmail(self.email_address, candidate.email, text)
            
            return True
            
        except Exception as e:
            print(f"Error sending email to {candidate.email}: {str(e)}")
            return False
    
    def _generate_email_body(self, candidate: Candidate) -> str:
        """Generate personalized email body for candidate"""
        
        interview_date = "Not scheduled"
        interview_time = "Not scheduled"
        
        if candidate.interview_datetime:
            interview_date = candidate.interview_datetime.strftime('%B %d, %Y')
            interview_time = candidate.interview_datetime.strftime('%H:%M %Z')
        
        meet_link = candidate.interview_link or "Will be provided separately"
        
        email_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
                .footer {{ text-align: center; padding: 20px; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Interview Confirmation</h1>
                </div>
                
                <div class="content">
                    <p>Dear {candidate.name},</p>
                    
                    <p>Congratulations! We are pleased to inform you that you have been selected for an interview based on your application and qualifications.</p>
                    
                    <div class="details">
                        <h3>Interview Details:</h3>
                        <p><strong>Date:</strong> {interview_date}</p>
                        <p><strong>Time:</strong> {interview_time}</p>
                        <p><strong>Duration:</strong> Approximately 1 hour</p>
                        <p><strong>Format:</strong> Video Conference</p>
                        <p><strong>Meeting Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
                    </div>
                    
                    <p>Please confirm your attendance by replying to this email. If you need to reschedule, please let us know as soon as possible.</p>
                    
                    <p><strong>What to expect:</strong></p>
                    <ul>
                        <li>Technical discussion about your experience</li>
                        <li>Questions about your skills and projects</li>
                        <li>Opportunity to ask questions about the role and company</li>
                    </ul>
                    
                    <p>We look forward to speaking with you!</p>
                    
                    <p>Best regards,<br>
                    HR Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply directly to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return email_body

