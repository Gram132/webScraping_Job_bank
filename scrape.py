from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import datetime
import time

# Configure Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--remote-debugging-port=9222')

driver = webdriver.Chrome()
# Navigate to the URL
data = {'IT': {'urls': ['https://example.com/job1', 'https://example.com/job2']}}

job_data = []

for url in data['IT']['urls']:
    driver.get(url)
    try:
        apply_now_button = driver.find_element(By.ID, 'applynowbutton')
        apply_now_button.click()
        time.sleep(1)

        email_element = driver.find_element(By.XPATH, '//*[@id="howtoapply"]/p[1]/a')
        email = email_element.get_attribute("href")
        job_Title = driver.find_element(By.XPATH, '//*[@id="wb-cont"]/span[1]').text
        deadline_Date = driver.find_element(By.XPATH, '//*[@id="applynow"]/p').text

        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime('%Y-%m-%d')
        current_time = current_datetime.strftime('%H:%M:%S')

        job_details = {
            'Job_Title': job_Title,
            'Email': email,
            'Advartized_until': deadline_Date,
            'create_date': current_date,
            'create_time': current_time,
            'date_added': url,
            'is_sent': 0
        }

        job_data.append(job_details)
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Close the browser
driver.quit()

# Print job data
for job in job_data:
    print(job)
