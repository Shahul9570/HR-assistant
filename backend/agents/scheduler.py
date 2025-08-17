from datetime import datetime, timedelta
from typing import List, Optional, Dict
from backend.models.candidate import Candidate
from backend.utils.calendar_integration import GoogleCalendarIntegration


class InterviewScheduler:
    def __init__(self):
        self.calendar_integration = GoogleCalendarIntegration()

    def _get_next_working_day(self, date: datetime) -> datetime:
        """Skip weekends and return next working day (Mon-Fri)."""
        while date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            date += timedelta(days=1)
        return date

    def schedule_interviews(
        self,
        candidates: List[Candidate],
        start_date: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        Schedule interviews:
        - 1-hour slots, 9 AM to 5 PM (8 slots per day).
        - Continue on next working day if more candidates.
        """
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)

        # Ensure starting date is a working day
        current_date = self._get_next_working_day(start_date)

        scheduled_count = 0
        failed_schedules = []
        interview_slots = []

        slot_index = 0
        for candidate in candidates:
            # Reset slots after 8 interviews, move to next working day
            if slot_index >= 8:
                current_date += timedelta(days=1)
                current_date = self._get_next_working_day(current_date)
                slot_index = 0

            # Assign time slot (9 AM + slot_index hours)
            interview_time = current_date.replace(
                hour=9 + slot_index, minute=0, second=0, microsecond=0
            )
            slot_index += 1

            # Create calendar event
            event_details = self.calendar_integration.create_interview_event(
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                start_time=interview_time,
                duration_minutes=60
            )

            if event_details:
                candidate.interview_scheduled = True
                candidate.interview_datetime = interview_time
                candidate.interview_link = event_details.get("meet_link")
                scheduled_count += 1
                interview_slots.append({
                    "candidate": candidate.name,
                    "datetime": interview_time.strftime("%Y-%m-%d %H:%M"),
                    "meet_link": candidate.interview_link
                })
            else:
                failed_schedules.append(candidate.name)

        return {
            "scheduled_count": scheduled_count,
            "total_candidates": len(candidates),
            "failed_schedules": failed_schedules,
            "schedule_details": interview_slots
        }

    def get_interview_summary(self, candidates: List[Candidate]) -> Dict[str, any]:
        """Return a summary of scheduled interviews."""
        scheduled_interviews = [c for c in candidates if getattr(c, "interview_scheduled", False)]

        interview_schedule = []
        for candidate in scheduled_interviews:
            dt_str = (
                candidate.interview_datetime.strftime("%Y-%m-%d %H:%M")
                if getattr(candidate, "interview_datetime", None)
                else "Not scheduled"
            )
            interview_schedule.append({
                "candidate_name": candidate.name,
                "email": candidate.email,
                "datetime": dt_str,
                "meet_link": getattr(candidate, "interview_link", None) or "Not available"
            })

        return {
            "total_scheduled": len(scheduled_interviews),
            "schedule_details": interview_schedule
        }
