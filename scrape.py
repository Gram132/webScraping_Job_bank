from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Set up Chrome options
options = Options()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Initialize ChromeDriver with the specified version
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

# Example usage
driver.get('https://example.com')
print(driver.title)

# Close the driver
driver.quit()
