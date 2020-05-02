import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


def auth_and_init():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file("/Users/achintya/Downloads/client_secret.json", scopes=scopes)
    credentials = flow.run_console()
    return credentials


if __name__ == "main":
    auth_and_init()


def get_calendars(student_id):
    credentials = pickle.load(open('tokens/' + student_id + '/token.pkl', 'rb'))
    service = build('calendar', 'v3', credentials=credentials)
    result = service.calendarList().list().execute()
    return result
