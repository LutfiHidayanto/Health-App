import datetime
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

def create_google_meet_link():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'  # replace with your service account file path
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('calendar', 'v3', credentials=credentials)

    # Create a new event
    event = {
        'summary': 'Consultation',
        'description': 'Consultation with the doctor',
        'start': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat() + 'Z',  # In 5 minutes
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=60)).isoformat() + 'Z',  # Duration of 1 hour
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': 'some-random-string',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
        'attendees': [
            {'email': 'doctor@example.com'},  # replace with doctor's email
            {'email': 'patient@example.com'},  # replace with patient's email
        ],
    }

    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    
    meet_link = event['hangoutLink']
    return meet_link
