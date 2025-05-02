from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display
from selenium.webdriver.firefox.service import Service

# Start a virtual display
virtual_display = Display(size=(1920, 1080))
virtual_display.start()

print("initiating driver")
# Configure Firefox options (optional)
firefox_options = Options()

# # Set preferences directly on the options
# firefox_options.set_preference("browser.download.folderList", 2)
# firefox_options.set_preference(
#     "browser.download.manager.showWhenStarting", False)
# firefox_options.set_preference(
#     "browser.helperApps.neverAsk.saveToDisk", "application/pdf")

# Use the geckodriver present in driver/geckodriver
service = Service(executable_path='driver/geckodriver')
driver = webdriver.Firefox(service=service, options=firefox_options)

driver.get("https://www.google.com")
driver.title
