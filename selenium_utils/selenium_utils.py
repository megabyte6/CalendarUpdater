from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def element(
    driver: Chrome,
    selector: str,
    root: WebElement = None,
    locator_strategy=By.CSS_SELECTOR,
    timeout=0,
    wait_until_visible: bool = True,
) -> WebElement:
    """
    Locates the WebElement by the given selector.

    Args:
        driver: The Chrome driver to use.
        selector: The selector to locate the element.
        root: The root element to search from.
        locator_strategy: What strategy to use to locate the element.
        timeout: How long to wait for the element to be visible before stopping the program.
        wait_until_visible: Whether to wait for the element to be visible before returning it.

    Returns:
        The WebElement that the given selector points to.

    Raises:
        TimeoutException: If the element was not visible before the given timeout occurs.
    """

    if root is None:
        root = driver

    if wait_until_visible:
        # Wait for the element to be visible before returning the WebElement.
        try:
            return WebDriverWait(driver=root, timeout=timeout).until(
                expected_conditions.visibility_of_element_located((locator_strategy, selector))
            )
        except TimeoutException as e:
            driver.quit()
            raise e
    else:
        # Wait for element to be present in the DOM before returning the WebElement.
        try:
            return WebDriverWait(driver=root, timeout=timeout).until(
                expected_conditions.presence_of_element_located((locator_strategy, selector))
            )
        except TimeoutException as e:
            driver.quit()
            raise e


def elements(
    driver: Chrome,
    selector: str,
    root: WebElement = None,
    locator_strategy=By.CSS_SELECTOR,
    timeout=0,
    wait_until_visible=True,
) -> list[WebElement]:
    """
    Locates the WebElement by the given selector.

    Args:
        driver: The Chrome driver to use.
        selector: The selector to locate the element.
        root: The root element to search from.
        locator_strategy: What strategy to use to locate the element.
        timeout: How long to wait for the element to be visible before stopping the program.
        wait_until_visible: Whether to wait for the element to be visible before returning it.

    Returns:
        The list of WebElements that the given selector points to.

    Raises:
        TimeoutException: If the element was not visible before the given timeout occurs.
    """

    if root is None:
        root = driver

    if wait_until_visible:
        # Wait for the elements to be visible before returning the list of WebElements.
        try:
            return WebDriverWait(driver=root, timeout=timeout).until(
                expected_conditions.visibility_of_all_elements_located((locator_strategy, selector))
            )
        except TimeoutException as e:
            driver.quit()
            raise e
    else:
        # Wait for element to be present in the DOM before returning the WebElement.
        try:
            return WebDriverWait(driver=root, timeout=timeout).until(
                expected_conditions.presence_of_all_elements_located((locator_strategy, selector))
            )
        except TimeoutException as e:
            print(f"Timeout from {selector} not existing in the DOM")
            driver.quit()
            raise e


def element_exists(
    driver: Chrome,
    selector: str,
    timeout: int,
    root: WebElement = None,
    locator_strategy=By.CSS_SELECTOR,
) -> bool:
    """
    Checks if the given element exists or loads before the timeout occurs.

    Args:
        driver: The Chrome driver to use.
        selector: The selector to locate the element.
        timeout: How long to wait for the element to be visible before stopping the program.
        root: The root element to search from.
        locator_strategy: What strategy to use to locate the element.
    """

    try:
        element(driver, selector, root, locator_strategy, timeout, wait_until_visible=False)
        return True
    except TimeoutException:
        return False


def is_stale(element: WebElement) -> bool:
    """
    Checks if the given element is stale.

    Args:
        element: The element to check.

    Returns:
        Whether the given element is stale.
    """

    try:
        # Attempt to interact with the element
        element.is_displayed()
        return False
    except StaleElementReferenceException:
        return True


def hover(driver: Chrome, element: WebElement) -> None:
    """
    Hovers over the given element.

    Args:
        driver: The Chrome driver to use.
        element: The element to hover over.
    """

    ActionChains(driver).move_to_element(element).perform()
