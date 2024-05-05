import concurrent.futures
import json
import os.path

from selenium.common.exceptions import TimeoutException

import google_api
import homebase
import my_studio
from school import Session, Instructor, get_session_from_time


def create_settings_file() -> None:
    """
    Creates the settings.json file.
    """

    settings = {
        "useRemoteBrowser": False,
        "useHeadlessBrowser": True,
        "leaveChromeOpen": False,
        "myStudio": {
            "username": "",
            "password": "",
        },
        "homebase": {
            "username": "",
            "password": "",
        },
        "googleAPI": {
            "scopes": ["https://www.googleapis.com/auth/calendar.events"],
            "calendarID": "primary",
            "secretsFile": "credentials.json",
            "tokenFile": "token.json",
        },
        "students": {
            "unity": [],
            "focus": [],
        },
    }

    with open("settings.json", "w") as settings_file:
        json.dump(settings, settings_file, indent=4)


def combine_duplicate_sessions(*sessions: Session) -> list[Session]:
    """
    Combines sessions with the same time.

    Args:
        sessions: The sessions to combine.

    Returns:
        The combined sessions.
    """

    combined: list[Session] = []
    for session in sessions:
        existing_session = get_session_from_time(combined, session.start_time)
        if existing_session:
            existing_session.students.extend(session.students)
            existing_session.instructors.extend(session.instructors)
        else:
            combined.append(session)

    return combined


def add_instructors_to_sessions(sessions: list[Session], instructors: list[Instructor]) -> None:
    """
    Adds instructors to sessions.

    Args:
        sessions: The sessions to add instructors to.
        instructors: The instructors to add to the sessions.

    Returns:
        The sessions with instructors added.
    """

    for session in sessions:
        for instructor in instructors:
            if session.is_scheduled(instructor) and instructor not in session.instructors:
                session.instructors.append(instructor)


def main() -> None:
    """
    Main function.

    Args:
        headless_browser: Whether to run the browser in headless mode.
        keep_chrome_open: Whether to keep the Chrome window open after the program is done.
        remote_browser: Whether to use a remote browser (often when access a browser in a Docker container)
    """

    if not os.path.exists("settings.json"):
        create_settings_file()
        print("Please fill out the settings.json file and run again.")
        return
    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)

    creds = google_api.load_google_api_credentials(
        secrets_file_path=settings["googleAPI"]["secretsFile"],
        api_scopes=settings["googleAPI"]["scopes"],
        token_file_path=settings["googleAPI"]["tokenFile"],
    )

    # Use a ThreadPoolExecutor to run the functions concurrently since they
    # interact with websites and take a while to run.
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            mystudio_future = executor.submit(
                my_studio.read_data_from_mystudio,
                username=settings["myStudio"]["username"],
                password=settings["myStudio"]["password"],
                headless_browser=settings["useHeadlessBrowser"],
                keep_chrome_open=settings["leaveChromeOpen"],
                remote_browser=settings["useRemoteBrowser"],
                attempts=3,
            )
            homebase_future = executor.submit(
                homebase.read_data_from_homebase,
                username=settings["homebase"]["username"],
                password=settings["homebase"]["password"],
                headless_browser=settings["useHeadlessBrowser"],
                keep_chrome_open=settings["leaveChromeOpen"],
                remote_browser=settings["useRemoteBrowser"],
            )

            # Wait for functions to complete.
            concurrent.futures.wait([mystudio_future, homebase_future])

            create_sessions, jr_sessions = mystudio_future.result()
            instructors = homebase_future.result()

    except TimeoutException as e:
        print("An error occurred while reading data from websites.")
        print(e)
        return

    combined_sessions = combine_duplicate_sessions(*create_sessions, *jr_sessions)
    add_instructors_to_sessions(combined_sessions, instructors)

    google_api.add_sessions_to_calendar(
        credentials=creds,
        calendar_id=settings["googleAPI"]["calendarID"],
        sessions=combined_sessions,
        unity_student_names=settings["students"]["unity"],
        focus_student_names=settings["students"]["focus"],
    )
