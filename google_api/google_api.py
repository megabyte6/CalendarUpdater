import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from school import Session


def load_google_api_credentials(
    secrets_file_path: str,
    api_scopes: list[str],
    token_file_path: str = None,
) -> Credentials:
    """
    Loads the Google API credentials from the given environment variables.

    Args:
        secrets_file_path: The path to the Google API secrets file.
        api_scopes: The Google API scopes to use.
        token_file_path: The path to the Google API token file.

    Returns:
        The Google API credentials.
    """

    if token_file_path is None:
        token_file_path = "token.json"

    creds = None
    # token.json stores access and refresh tokens. It is automatically created on first run.
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, api_scopes)
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file_path, api_scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_file_path, "w") as token:
            token.write(creds.to_json())

    return creds


def add_sessions_to_calendar(
    credentials: Credentials,
    calendar_id: str,
    sessions: list[Session],
    unity_student_names: list[str] = None,
    focus_student_names: list[str] = None,
):
    """
    Adds the given sessions to the Google Calendar.

    Args:
        credentials: The Google API credentials to use.
        calendar_id: The ID of the Google Calendar to add the sessions to.
        sessions: The sessions to add to the Google Calendar.
        unity_student_names: The students in the Unity session.
        focus_student_names: The students who need extra resources to manage.

    Raises:
        HttpError: If an error occurs while adding the sessions to the Google Calendar.
    """

    if unity_student_names is None:
        unity_student_names = []
    if focus_student_names is None:
        focus_student_names = []

    try:
        service = build("calendar", "v3", credentials=credentials)

        today = datetime.datetime.today().strftime("%Y-%m-%d")

        for session in sessions:
            description = ""

            if session.instructors:
                instructor_details = [
                    f"{instructor.name} ({instructor.start_time.strftime('%I:%M%p')} - {instructor.end_time.strftime('%I:%M%p')})"
                    for instructor in session.instructors
                ]
                description += f"Instructors:\n{'\n'.join(instructor_details)}\n\n"

            unity_students = session.unity_students(unity_student_names)
            if unity_students:
                description += f"Unity:\n{'\n'.join([str(student) for student in unity_students])}\n\n"

            jr_students = session.jr_students()
            if jr_students:
                description += f"JR:\n{'\n'.join([str(student) for student in jr_students])}\n\n"

            focus_students = session.focus_students(focus_student_names)
            if focus_students:
                description += f"Focus:\n{'\n'.join([str(student) for student in focus_students])}\n\n"

            impact_students = [
                str(student)
                for student in session.create_students()
                if student not in unity_students and student not in focus_students
            ]
            description += f"IMPACT:\n{'\n'.join(impact_students)}"

            create_session_count = len(session.create_students())
            jr_session_count = len(session.jr_students())
            event = {
                "summary": f"{session.start_time.strftime('%I:%M%p')} - {create_session_count} | {jr_session_count}",
                "description": description,
                "start": {
                    "dateTime": f"{today}T{session.start_time.strftime('%H:%M')}:00",
                    "timeZone": "America/Vancouver",
                },
                "end": {
                    "dateTime": f"{today}T{session.end_time.strftime('%H:%M')}:00",
                    "timeZone": "America/Vancouver",
                },
            }
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Session event created: {event.get('htmlLink')}")

    except HttpError as e:
        print(f"ERROR: Could not add events to Google Calendar\n{e}")
        return
