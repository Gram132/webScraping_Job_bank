import requests
from bs4 import BeautifulSoup
import json

def scrape_job_data():
    url = 'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=software+developer&locationstring='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_card in soup.find_all('article', class_='resultJobCard'):
        job_title = job_card.find('h3', class_='title').text.strip()
        company = job_card.find('div', class_='company').text.strip()
        location = job_card.find('div', class_='location').text.strip()
        jobs.append({
            'title': job_title,
            'company': company,
            'location': location
        })

    with open('job_data.json', 'w') as f:
        json.dump(jobs, f)

if __name__ == '__main__':
    scrape_job_data()
