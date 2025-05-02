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
    try:
        if driver:
            driver.quit()
        if virtual_display:
            virtual_display.stop()
    except Exception as e:
        print("Error during cleanup:", e)
    virtual_display = Display(size=(1920, 1080))
    virtual_display.start()
    print("initiating driver")
    firefox_options = Options()
    service = Service(executable_path='driver/geckodriver')
    driver = webdriver.Firefox(service=service, options=firefox_options)


init_driver()
