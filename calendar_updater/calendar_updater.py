import concurrent.futures
import json
import os.path

import google_api
import homebase
import my_studio
from code_ninjas import CodeNinjasClass, get_class_from_time


def create_settings_file() -> None:
    """
    Creates the settings.json file.
    """

    settings = {
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


def combine_duplicate_classes(*classes: CodeNinjasClass) -> list[CodeNinjasClass]:
    """
    Combines classes with the same time.

    Args:
        classes: The classes to combine.

    Returns:
        The combined classes.
    """

    combined: list[CodeNinjasClass] = []
    for code_ninjas_class in classes:
        existing_class = get_class_from_time(combined, code_ninjas_class.start_time)
        if existing_class:
            existing_class.students.extend(code_ninjas_class.students)
            existing_class.senseis.extend(code_ninjas_class.senseis)
        else:
            combined.append(code_ninjas_class)


def main(headless_browser: bool = True, keep_chrome_open: bool = False) -> None:
    """
    Main function.

    Args:
        headless_browser: Whether to run the browser in headless mode.
        keep_chrome_open: Whether to keep the Chrome window open after the program is done.
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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        mystudio_future = executor.submit(
            my_studio.read_data_from_mystudio,
            username=settings["myStudio"]["username"],
            password=settings["myStudio"]["password"],
            headless_browser=headless_browser,
            keep_chrome_open=keep_chrome_open,
        )
        homebase_future = executor.submit(
            homebase.read_data_from_homebase,
            username=settings["homebase"]["username"],
            password=settings["homebase"]["password"],
            headless_browser=headless_browser,
            keep_chrome_open=keep_chrome_open,
        )

        # Wait for functions to complete.
        concurrent.futures.wait([mystudio_future, homebase_future])

        create_classes, jr_classes = mystudio_future.result()
        homebase_classes = homebase_future.result()

    google_api.add_classes_to_calendar(
        credentials=creds,
        calendar_id=settings["googleAPI"]["calendarID"],
        classes=combine_duplicate_classes(*create_classes, *jr_classes, *homebase_classes),
        unity_student_names=settings["students"]["unity"],
        focus_student_names=settings["students"]["focus"],
    )
