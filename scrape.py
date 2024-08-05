import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

# List of URLs to scrape
urls = ['https://www.jobbank.gc.ca/jobsearch/jobpostingtfw/41480404;jsessionid=C19B7A626490D35D896834EFAD0F254B.jobsearch74?source=searchresults',
 'https://www.jobbank.gc.ca/jobsearch/jobpostingtfw/41477064;jsessionid=C19B7A626490D35D896834EFAD0F254B.jobsearch74?source=searchresults',
 'https://www.jobbank.gc.ca/jobsearch/jobpostingtfw/41459537;jsessionid=C19B7A626490D35D896834EFAD0F254B.jobsearch74?source=searchresults' ]

data = []

for url in urls:
    driver.get(url)
    try:
        apply_now_button = driver.find_element(By.XPATH, '//*[@id="applynowbutton"]')
        apply_now_button.click()
        time.sleep(1)
        
        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the email in the <a> element
        email_element = soup.select_one('#howtoapply > p:nth-of-type(1) > a')
        email = email_element['href'] if email_element else 'N/A'
        
        job_title = soup.select_one('#wb-cont > span:nth-of-type(1)').text if soup.select_one('#wb-cont > span:nth-of-type(1)') else 'N/A'
        deadline_date = soup.select_one('#applynow > p').text if soup.select_one('#applynow > p') else 'N/A'
        
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime('%Y-%m-%d')  # Format as 'YYYY-MM-DD'
        current_time = current_datetime.strftime('%H:%M:%S')

        job_details = {
            'Job_Title': job_title,
            'Email': email,
            'Advartized_until': deadline_date,
            'create_date': current_date,
            'create_time': current_time,
            'date_added': url,  # Assuming `date_added` should be the URL
            'is_sent': 0
        }
        data.append(job_details)
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# Close the browser
driver.quit()

# Print the results
for job in data:
    print(job)
