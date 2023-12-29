import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from code_ninjas import CodeNinjasClass


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
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_file_path, api_scopes
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_file_path, "w") as token:
            token.write(creds.to_json())

    return creds


def add_classes_to_calendar(
    credentials: Credentials,
    calendar_id: str,
    classes: list[CodeNinjasClass],
    unity_student_names: list[str] = None,
    focus_student_names: list[str] = None,
):
    """
    Adds the given classes to the Google Calendar.

    Args:
        credentials: The Google API credentials to use.
        calendar_id: The ID of the Google Calendar to add the classes to.
        classes: The classes to add to the Google Calendar.
        unity_student_names: The students in the Unity class.
        focus_student_names: The students who need extra resources to manage.

    Raises:
        HttpError: If an error occurs while adding the classes to the Google Calendar.
    """

    if unity_student_names is None:
        unity_student_names = []
    if focus_student_names is None:
        focus_student_names = []

    try:
        service = build("calendar", "v3", credentials=credentials)

        today = datetime.datetime.today().strftime("%Y-%m-%d")

        for code_ninjas_class in classes:
            description = ""

            if code_ninjas_class.senseis:
                sensei_details = [
                    f"{sensei.name} ({sensei.start_time.strftime('%I:%M%p')} - {sensei.end_time.strftime('%I:%M%p')})"
                    for sensei in code_ninjas_class.senseis
                ]
                description += f"Sensei:\n{'\n'.join(sensei_details)}\n\n"

            unity_students = code_ninjas_class.unity_students(unity_student_names)
            if unity_students:
                description += f"Unity:\n{'\n'.join([str(student) for student in unity_students])}\n\n"

            jr_students = code_ninjas_class.jr_students()
            if jr_students:
                description += (
                    f"JR:\n{'\n'.join([str(student) for student in jr_students])}\n\n"
                )

            focus_students = code_ninjas_class.focus_students(focus_student_names)
            if focus_students:
                description += f"Focus:\n{'\n'.join([str(student) for student in focus_students])}\n\n"

            impact_students = [
                str(student)
                for student in code_ninjas_class.create_students()
                if student not in unity_students and student not in focus_students
            ]
            description += f"IMPACT:\n{'\n'.join(impact_students)}"

            create_class_count = len(code_ninjas_class.create_students())
            jr_class_count = len(code_ninjas_class.jr_students())
            event = {
                "summary": f"{code_ninjas_class.start_time.strftime('%I:%M%p')} - {create_class_count} | {jr_class_count}",
                "description": description,
                "start": {
                    "dateTime": f"{today}T{code_ninjas_class.start_time.strftime('%H:%M')}:00",
                    "timeZone": "America/Vancouver",
                },
                "end": {
                    "dateTime": f"{today}T{code_ninjas_class.end_time.strftime('%H:%M')}:00",
                    "timeZone": "America/Vancouver",
                },
            }
            event = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )
            print(f"Class event created: {event.get('htmlLink')}")

    except HttpError as e:
        print(f"ERROR: Could not add events to Google Calendar\n{e}")
        return
