from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import atexit
import sys
import time
import base64
from io import BytesIO
import os
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from PIL import Image
from pyvirtualdisplay import Display
from webdriver_manager.core.driver_cache import DriverCacheManager

os.environ['XDG_CACHE_HOME'] = '/tmp/selenium-cache'

driver = None
virtual_display = None


def init_driver():
    global driver, virtual_display
    options = Options()
    driver = webdriver.Remote(
        command_executor='http://15.207.54.183:4444/wd/hub',
        options=options
    )
    # try:
    #     if driver:
    #         driver.quit()
    #     if virtual_display:
    #         virtual_display.stop()
    # except Exception as e:
    #     print("Error during cleanup:", e)

    # virtual_display = Display(size=(1920, 1080))
    # virtual_display.start()

    # print("initiating driver")
    # firefox_options = Options()

    # service = Service(executable_path='driver/geckodriver')
    # driver = webdriver.Firefox(service=service, options=firefox_options)
    # print("driver initiated")


def set_viewport_size(driver, width, height):
    # Add some buffer for safe margin
    driver.set_window_size(width + 20, height + 120)
    driver.execute_script(f"window.resizeTo({width}, {height});")
    actual_width = driver.execute_script("return window.innerWidth")
    actual_height = driver.execute_script("return window.innerHeight")
    # If still not correct, force set viewport by adjusting window size again
    driver.set_window_size(
        width + (width - actual_width),
        height + (height - actual_height)
    )


def take_screenshot(url, template=None):
    global driver
    init_driver()

    try:
        if template is not None and template.type == 'images':
            set_viewport_size(driver, 1024, 1024)
        else:
            driver.set_window_size(1200, 900)

        driver.get(url)

        # Wait for the page to fully load by checking the document readiness
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(('tag name', 'body'))
        )

        # Save the screenshot to a BytesIO object
        screenshot_data = driver.get_screenshot_as_png()
        screenshot = BytesIO(screenshot_data)
        image = Image.open(screenshot)
        driver.quit()
        return image
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        return None
