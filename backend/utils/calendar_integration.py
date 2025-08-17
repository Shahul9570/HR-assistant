import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class GoogleCalendarIntegration:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def create_interview_event(self, 
                             candidate_name: str,
                             candidate_email: str,
                             start_time: datetime,
                             duration_minutes: int = 60) -> Optional[Dict]:
        """Create a calendar event for interview"""
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': f'Interview with {candidate_name}',
                'description': f'Job interview with candidate {candidate_name}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': candidate_email},
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"interview_{candidate_name}_{int(start_time.timestamp())}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }
            
            event = self.service.events().insert(
                calendarId='primary', 
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            return {
                'event_id': event['id'],
                'html_link': event['htmlLink'],
                'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
            }
            
        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return None
    
    def get_available_slots(self, days_ahead: int = 7) -> List[datetime]:
        """Get available time slots for interviews"""
        try:
            now = datetime.utcnow()
            end_date = now + timedelta(days=days_ahead)
            
            # Get busy times
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generate available slots (9 AM to 5 PM, weekdays only)
            available_slots = []
            current_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
            
            for day in range(days_ahead):
                if current_date.weekday() < 5:  # Monday to Friday
                    for hour in range(9, 17):  # 9 AM to 5 PM
                        slot_start = current_date.replace(hour=hour)
                        slot_end = slot_start + timedelta(hours=1)
                        
                        # Check if slot is free
                        is_free = True
                        for event in events:
                            event_start = datetime.fromisoformat(
                                event['start'].get('dateTime', event['start'].get('date'))
                            )
                            event_end = datetime.fromisoformat(
                                event['end'].get('dateTime', event['end'].get('date'))
                            )
                            
                            if (slot_start < event_end and slot_end > event_start):
                                is_free = False
                                break
                        
                        if is_free:
                            available_slots.append(slot_start)
                
                current_date += timedelta(days=1)
            
            return available_slots[:10]  # Return first 10 available slots
            
        except Exception as e:
            print(f"Error getting available slots: {str(e)}")
            return []