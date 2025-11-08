from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from typing import List, Dict, Union, Literal
import csv

import time
from .custom_types import StaffLink

def profile_to_csv(profile_links: List[StaffLink], filename: str='uic_staff.csv'):
    headers = ['name', 'link', 'academic_title', 'department', 'phone', 'email']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(profile_links)
    
    print(f"Successfully saved {len(profile_links)} profiles to {filename}")

def find_safe_element_text(element: Union[WebDriver, WebElement], by, match: str) -> str:
    try:
        text = element.find_element(by, match).get_attribute('innerText') or ''
        return text.strip()
    except NoSuchElementException as e:
        return ''

def scrape_uic_staff(driver: WebDriver, url: str):

    profile_links: List[StaffLink] = []

    try:
    
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "directory-list"))
        )

        time.sleep(5)

        directory_list = driver.find_element(By.CLASS_NAME, 'directory-list')

        articles = directory_list.find_elements(By.CLASS_NAME, 'profile-teaser')

        for article in articles:

            name_element = article.find_element(By.CLASS_NAME, '_name')

            name = (name_element.get_attribute('innerText') or '').strip()
            link = name_element.find_element(By.TAG_NAME, 'a').get_attribute('href') or ''
            academic_title = article.find_element(By.CLASS_NAME, '_academic-title').get_attribute('innerText') or ''
            department = article.find_element(By.CLASS_NAME, '_department').get_attribute('innerText') or ''
            phone = find_safe_element_text(article, By.CLASS_NAME, '_phone').replace('.', '')
            email = find_safe_element_text(article, By.CLASS_NAME, '_email')

            profile: StaffLink = {
                'name': name,
                'link': link,
                'academic_title': academic_title,
                'department': department,
                'phone': phone,
                'email': email
            }
            profile_links.append(profile)
        
        profile_to_csv(profile_links=profile_links)

    except TimeoutException:
        print("Page took too long to load")
    except NoSuchElementException:
        print("Element not found on page")
    
    return profile_links