from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

from scraper.uic_staff import scrape_uic_staff
from scraper.uic_profile import scrape_profiles
from scraper.google_scholar import scrape_scholar_profiles
import traceback

from csv_utils import extract_single_row_from_csv, merge_csv, read_user_ids, compare_csv_files, read_csv
from scraper.custom_types import UserID
from typing import List
from download_pdfs.pdf_downloader import download_research_papers

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

try:

    # STEP 1: Scrape faculty
    # Scrapes the list of CS faculty
    # staff_links = scrape_uic_staff(driver=driver, url='https://cs.uic.edu/faculty-staff/faculty/')

    # STEP 2: Scrape individual profile
    # NOTE: You are never going to need the below option.
    # Scrapes individual profiles of each faculty member
    # scrape_profiles(driver=driver, staff_links=staff_links)

    # STEP 3: Check if configuration missing for any faculty member
    missing_names = compare_csv_files('uic_staff.csv', 'scholar_ids.csv')
    # TODO: Build a pipeline on how to handle missing names. Ideally via some notification.
    print(missing_names)

    # TODO: Build a function that handles missing data

    # STEP 4: MERGE CSVs
    # Merges the Google Scholar IDs of each professor into one csv.
    # merge_csv('uic_staff.csv', 'scholar_ids.csv', 'uic_staff_user_ids.csv', ['name'])

    # STEP 5: Scrape Google Scholar
    # user_ids: List[UserID] = read_user_ids('uic_staff_user_ids.csv')
    # scrape_scholar_profiles(driver=driver, staff_user_ids=user_ids, limit=None)

    # STEP 6: Download PDFs of research papers
    download_research_papers()
    
except Exception as e:
    traceback.print_exc()