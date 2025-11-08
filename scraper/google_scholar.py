from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Dict, List
from urllib.parse import urlparse, parse_qs

from .custom_types import UserID, ResearchPaper
import csv
from tqdm import tqdm
from selenium.webdriver.remote.webelement import WebElement
import time


def research_papers_to_csv(data: List[ResearchPaper], filename: str='research_paper.csv'):
    headers = ['year', 'paper_title', 'paper_link','name', 'link', 'academic_title', 'department', 'phone', 'email', 'user_id']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Successfully saved {len(data)} research papers to {filename}")

def get_safe_element(root_element: WebElement, by, match: str, attribute: str) -> str:
    try:
        return root_element.find_element(by, match).get_attribute(attribute) or ''
    except NoSuchElementException:
        return ''

def get_profile_data(driver: WebDriver, staff_user_id: UserID) -> List[ResearchPaper]:

    user_id = staff_user_id['user_id']

    if user_id == '' or user_id is None :
        return []

    research_papers: List[ResearchPaper] = []
    
    try:
        url = f'https://scholar.google.com/citations?view_op=list_mandates_page_export&user={user_id}'

        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'gs_mnde_one_art'))
        )

        articles = driver.find_elements(By.CLASS_NAME, 'gs_mnde_one_art')
        for article in articles:
            link_element = article.find_elements(By.CLASS_NAME, 'gs_mnde_p')[-1]
            conference_element = article.find_elements(By.CLASS_NAME, 'gs_mnde_p')[-2]
            year = (conference_element.get_attribute('innerText') or '').split(',')[-1].strip()
            research_paper: ResearchPaper = {
                'name': staff_user_id['name'],
                'link': staff_user_id['link'],
                'academic_title': staff_user_id['academic_title'],
                'department': staff_user_id['department'],
                'phone': staff_user_id['phone'],
                'email': staff_user_id['email'],
                'user_id': user_id,
                'paper_title': get_safe_element(article, By.CLASS_NAME, 'gs_mnde_ttl', 'innerText'),
                'paper_link': get_safe_element(link_element, By.CLASS_NAME, 'gs_gray', 'innerText'),
                'year': year
            }
            research_papers.append(research_paper)

    except TimeoutException:
        print("Page took too long to load", staff_user_id['name'])
    except NoSuchElementException:
        print("Element not found on page", staff_user_id['name'])
    
    return research_papers

def scrape_scholar_profiles(driver: WebDriver, staff_user_ids: List[UserID], limit = None):

    profile_data: List[ResearchPaper] = []

    progress_bar = tqdm(staff_user_ids[:limit], desc="Processing staff profiles from Google Scholar")

    for staff_user_id in progress_bar:
        progress_bar.set_description(f"Processing: {staff_user_id['name']}")
        profile_data.extend(get_profile_data(driver=driver, staff_user_id=staff_user_id))
        time.sleep(10)
    
    research_papers_to_csv(profile_data)
    return profile_data