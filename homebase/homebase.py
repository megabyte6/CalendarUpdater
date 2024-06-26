from datetime import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions, Remote

from school import Instructor
from selenium_utils import element, elements


def convert_to_time(hours: int, minutes: int, period: str) -> time:
    """
    Converts the given time to a time object.

    Args:
        hours: The hours.
        minutes: The minutes.
        period: The period.

    Returns:
        The time as a time object.
    """

    if period.lower() == "pm" and hours != 12:
        hours += 12

    return time(hour=hours, minute=minutes)


def create_homebase_webdriver(
    headless: bool = True,
    keep_open_on_finished: bool = False,
    remote_browser: bool = False,
) -> Chrome:
    """
    Creates a Chrome webdriver for the Homebase website.

    Args:
        headless: Whether to run the browser in headless mode.
        keep_open_on_finished: Whether to keep the Chrome window open after the program is done.
        remote_browser: Whether to use a remote browser (often when access a browser in a Docker container).

    Returns:
        The Chrome webdriver.
    """

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--incognito")
    if headless:
        chrome_options.add_argument("--headless=new")
    if keep_open_on_finished:
        chrome_options.add_experimental_option("detach", True)
    if remote_browser:
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")

    if remote_browser:
        return Remote(command_executor="http://localhost:4444/wd/hub", options=chrome_options)
    else:
        return Chrome(options=chrome_options)


def log_into_homebase(driver: Chrome, username: str, password: str) -> None:
    """
    Logs into the Homebase website.

    Args:
        driver: The Chrome driver to use.
        username: The username to login with.
        password: The password to login with.
    """

    element(driver, selector="#account_login").send_keys(username)
    element(driver, selector="#account_password").send_keys(password)
    element(driver, selector="#new_account > button").click()


def read_data_from_homebase(
    username: str,
    password: str,
    headless_browser: bool = True,
    keep_chrome_open: bool = False,
    remote_browser: bool = False,
) -> list[Instructor]:
    """
    Reads the instructors' data from the Homebase website.

    Args:
        username: The username to login with.
        password: The password to login with.
        headless_browser: Whether to run the browser in headless mode.
        keep_chrome_open: Whether to keep the Chrome window open after the program is done.
        remote_browser: Whether to use a remote browser (often when access a browser in a Docker container).

    Returns:
        The instructors' data.
    """

    driver = create_homebase_webdriver(
        headless=headless_browser,
        keep_open_on_finished=keep_chrome_open,
        remote_browser=remote_browser,
    )

    driver.get("https://app.joinhomebase.com")
    print("(Homebase) Logging in...")
    log_into_homebase(driver=driver, username=username, password=password)

    print("(Homebase) Reading instructors' names...")
    instructor_names = []
    instructor_name_element_selectors = [
        # For medium width screens
        "#react-app-root > div > div > div > div > div > div.Box.mv4.mh4 > div > div.Box > div > div > "
        "div:nth-child(2) > div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div > "
        "div.Box.Box--row.Box--align-items-center.Box--justify-content-start.ShiftCard__name_and_role > "
        "div:nth-child(1) > span",
        # For large width screens
        "#react-app-root > div > div > div > div > div > div.Box.mr24 > div.Box > div > div > div:nth-child(2) > "
        "div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div > "
        "div.Box.Box--row.Box--align-items-center.Box--justify-content-start.ShiftCard__name_and_role > "
        "div:nth-child(1) > span",
        # For small width screens
        "#react-app-root > div > div > div > div > div > div:nth-child(2) > div > div.Box > div > div > "
        "div:nth-child(2) > div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div:nth-child(1) > "
        "div.Box.Box--row.Box--align-items-center.Box--justify-content-start.ShiftCard__name_and_role > "
        "div:nth-child(1) > span",
    ]
    for selector in instructor_name_element_selectors:
        try:
            instructor_names = [
                name.text
                for name in elements(
                    driver,
                    selector,
                    timeout=5,
                    wait_until_visible=False,
                    quit_webdriver_on_timeout=False,
                )
            ]
            break
        except TimeoutException:
            continue
    if len(instructor_names) == 0:
        driver.quit()
        raise TimeoutException("Could not find instructors' names on the Homebase website.")

    print("(Homebase) Reading instructors' shifts...")
    instructor_shift_times = []
    instructor_shift_time_element_selectors = [
        # For medium width screens
        "#react-app-root > div > div > div > div > div > div.Box.mv4.mh4 > div > div.Box > div > div > "
        "div:nth-child(2) > div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div > "
        "div.Box.Box--row.Box--align-items-center.ShiftCard__status_and_scheduled > "
        "div.Box.Box--ellipsis.ShiftCard__time-range > span",
        # For large width screens
        "#react-app-root > div > div > div > div > div > div.Box.mr24 > div.Box > div > div > div:nth-child(2) > "
        "div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div > "
        "div.Box.Box--row.Box--align-items-center.ShiftCard__status_and_scheduled > "
        "div.Box.Box--ellipsis.ShiftCard__time-range > span",
        # For small width screens
        "#react-app-root > div > div > div > div > div > div:nth-child(2) > div > div.Box > div > div > "
        "div:nth-child(2) > div > div > div.Box.ShiftsBlock > div > div:nth-child(2) > div > div > "
        "div.Box.Box--row.ShiftCard.ShiftCard--card > div.Box.Box--ellipsis > div:nth-child(1) > "
        "div.Box.Box--column.Box--justify-content-center.ShiftCard__status_and_scheduled > "
        "div.Box.Box--ellipsis.ShiftCard__time-range.mt4 > span",
    ]
    for selector in instructor_shift_time_element_selectors:
        try:
            instructor_shift_times = [
                name.text
                for name in elements(
                    driver,
                    selector,
                    timeout=5,
                    wait_until_visible=False,
                    quit_webdriver_on_timeout=False,
                )
            ]
            break
        except TimeoutException:
            continue
    if len(instructor_shift_times) == 0:
        driver.quit()
        raise TimeoutException("Could not find instructors' shifts on the Homebase website.")

    print("(Homebase) Adding instructors to sessions...")
    instructors: list[Instructor] = []
    for name, shift_time in zip(instructor_names, instructor_shift_times):
        start_time, start_time_period, _, end_time, end_time_period = shift_time.strip(" /").split(" ")
        start_time_hour, start_time_minute = start_time.split(":")
        end_time_hour, end_time_minute = end_time.split(":")
        instructors.append(
            Instructor(
                name=name,
                start_time=convert_to_time(int(start_time_hour), int(start_time_minute), start_time_period),
                end_time=convert_to_time(int(end_time_hour), int(end_time_minute), end_time_period),
            )
        )

    print("(Homebase) Done reading instructors' data.")
    return instructors
