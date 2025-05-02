import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
# Make the browser headless
options.add_argument("--headless")

start_time = time.time()

driver = webdriver.Remote(
    command_executor='http://15.207.54.183:4444/wd/hub',
    options=options
)

end_time = time.time()
print(f"WebDriver initialization took {end_time - start_time} seconds")

driver.get("https://www.99testimonials.com")
print(driver.title)
driver.quit()
