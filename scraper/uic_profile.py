from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Dict, List

from .custom_types import StaffLink
import csv
from tqdm import tqdm

def section_headers_to_csv(data: List[Dict], filename: str='section_headers.csv'):
    headers = ['name', 'sections']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Successfully saved {len(data)} profiles to {filename}")

def get_section_headers(driver: WebDriver, staff_link: StaffLink) -> Dict:

    url = staff_link['link']
    name = staff_link['name']
    if url == '' or name == '':
        return {}
    
    data = {}
    data['name'] = name

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "_academic-title"))
        )

        all_headers = map(lambda x: x.get_attribute('innerText') or '', driver.find_elements(By.CLASS_NAME, '_section-title'))
        data['sections'] = '\t'.join(all_headers)

    except TimeoutException:
        print("Page took too long to load")
    except NoSuchElementException:
        print("Element not found on page")
    
    return data

def scrape_profiles(driver: WebDriver, staff_links: List[StaffLink]):

    profile_section_headers = []

    progress_bar = tqdm(staff_links, desc="Processing staff profiles")
    for staff_link in progress_bar:
        progress_bar.set_description(f"Processing: {staff_link['name']}")
        section_header = get_section_headers(driver=driver, staff_link=staff_link)
        profile_section_headers.append(section_header)
    section_headers_to_csv(profile_section_headers)