import datetime

from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.support.ui import WebDriverWait

from code_ninjas import CodeNinjasClass, Curriculum, Ninja, get_class_from_time
from selenium_utils import element, element_exists, elements, hover, is_stale


def get_time_from_class_dropdown(text: str) -> datetime.time:
    """
    Gets the time from the given class dropdown text.

    Args:
        text: The class dropdown text.

    Returns:
        The time as a time object.
    """

    raw_time, time_period, *_ = text.split()
    hour, minute = raw_time.split(":")
    time = datetime.time(hour=int(hour), minute=int(minute))
    if time_period == "PM" and time.hour != 12:
        time = time.replace(hour=time.hour + 12)

    return time


def read_class_data(driver: Chrome, curriculum: Curriculum) -> list[CodeNinjasClass]:
    """
    Reads the class data from the given dropdown element.

    Args:
        curriculum: The curriculum the classes are in.

    Returns:
        The class data as a list of classes.
    """

    # Open dropdown showing classes for the day
    if curriculum == Curriculum.CREATE:
        dropdown = element(
            driver,
            selector="#i-s-container > div > div:nth-child(1) > div:nth-child(2) > div > div > "
            "div.sheduled_child_list",
        )
    else:
        dropdown = element(
            driver,
            selector="#i-s-container > div > div:nth-child(1) > div:nth-child(3) > div > div > "
            "div.sheduled_child_list",
        )
    dropdown.click()

    # Read data for today's classes
    class_data: list[CodeNinjasClass] = []
    class_elements = elements(
        driver,
        selector="div > ul > li",
        root=dropdown,
    )[1:]
    if len(class_elements) == 0:
        return class_data
    for i in range(len(class_elements)):
        time = get_time_from_class_dropdown(class_elements[i].text)
        create_class = CodeNinjasClass(time)
        class_data.append(create_class)

    # Open the first class to check student data
    class_elements[0].click()
    for i in range(len(class_elements)):
        class_dropdown_element = element(
            driver,
            selector="#class_datatable_view > div > div:nth-child(5) > div:nth-child(2) > div",
        )
        if i != 0:
            # Open the class dropdown
            class_dropdown_element.click()
            # Open the class
            element(
                driver,
                selector="#class_datatable_view > div > div:nth-child(5) > div:nth-child(2) > div > ul:nth-child(2) > "
                f"li:nth-child({i + 1})",
            ).click()

        # Get the time from the class dropdown text
        time = get_time_from_class_dropdown(class_dropdown_element.text)
        if not get_class_from_time(class_data, time):
            raise ValueError(f"Time '{time}' not found in class data")
        # Get the rows in the data table
        student_data_table = elements(
            driver,
            selector="#DataTables_Table_class_scheduler > tbody > tr",
            timeout=10,
            wait_until_visible=False,
        )
        for row in student_data_table:
            get_class_from_time(class_data, time).students.append(
                Ninja(element(driver, selector="td:nth-child(4) > span", root=row).text, curriculum)
            )

    # Return to the page showing all types of classes
    element(driver, selector="#class_datatable_view > div > span").click()

    return class_data


def create_mystudio_webdriver(
    headless: bool = True,
    keep_open_on_finished: bool = False,
    remote_browser: bool = False,
) -> Chrome:
    """
    Creates a Chrome webdriver for the MyStudio website.

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


def log_into_mystudio(driver: Chrome, username: str, password: str) -> None:
    """
    Logs into the MyStudio website.

    Args:
        driver: The Chrome driver to use.
        username: The username to login with.
        password: The password to login with.
    """

    element(driver, selector="#login_email").send_keys(username)
    element(driver, selector="#login_password").send_keys(password)
    element(
        driver,
        selector="#tooltipBgHide > div.height_auto.ng-scope > div.bg-white.height-full-vh.cont_flex.ng-scope > div > "
        "div > div > div > div:nth-child(2) > center > button",
    ).click()


def read_data_from_mystudio(
    username: str,
    password: str,
    headless_browser: bool = True,
    keep_chrome_open: bool = False,
    remote_browser: bool = False,
) -> tuple[list[CodeNinjasClass], list[CodeNinjasClass]]:
    """
    Reads today's class data from the MyStudio website.

    Args:
        username: The username to login with.
        password: The password to login with.
        headless_browser: Whether to run the browser in headless mode.
        keep_chrome_open: Whether to keep the Chrome window open after the program is done.
        remote_browser: Whether to use a remote browser (often when access a browser in a Docker container).

    Returns:
        A tuple containing the CREATE classes and the JR classes.
    """

    driver = create_mystudio_webdriver(
        headless=headless_browser,
        keep_open_on_finished=keep_chrome_open,
        remote_browser=remote_browser,
    )

    driver.get("https://cn.mystudio.io/v43/WebPortal/#/login")
    print("(MyStudio) Logging in...")
    log_into_mystudio(driver, username, password)

    # Interacting with the submenu before the rest of the page loads causes
    # Chrome to be redirected to the dashboard. Wait for the page to finish
    # loading by checking for this loading symbol.
    loading_spinner = element(
        driver,
        selector="#monthly > tbody > tr.ng-scope.parent > td:nth-child(3) > center[ng-show='sales_loading']",
        timeout=60,
        wait_until_visible=False,
    )

    WebDriverWait(driver, timeout=60).until(
        lambda _: is_stale(loading_spinner) or "none" in loading_spinner.value_of_css_property("display")
    )
    # Implicitly wait for 0.5 seconds to ensure that the data is completely loaded
    driver.implicitly_wait(0.5)

    # Hover over the sidebar menu to access submenu
    hover(driver, element(driver, selector="#operations > a > span", timeout=10))
    # Navigate to the class schedule page
    element(driver, selector="#sub_menu_class_appt_cal", timeout=5).click()

    create_classes: list[CodeNinjasClass] = []
    # Check if there are any CREATE classes today
    if element_exists(
        driver,
        selector="#i-s-container > div > div:nth-child(1) > div:nth-child(2) > div > div > div.sheduled_child_list",
        timeout=60,
    ):
        print("(MyStudio) Reading CREATE classes...")
        create_classes = read_class_data(driver, Curriculum.CREATE)

    jr_classes: list[CodeNinjasClass] = []
    # Check if there are any JR classes today. Timeout is 5 because the wait for the CREATE classes
    # dropdown should already be enough.
    if element_exists(
        driver,
        selector="#i-s-container > div > div:nth-child(1) > div:nth-child(3) > div > div > div.sheduled_child_list",
        timeout=5,
    ):
        print("(MyStudio) Reading JR classes...")
        jr_classes = read_class_data(driver, Curriculum.JR)

    print("(MyStudio) Done reading student data.")
    return create_classes, jr_classes
