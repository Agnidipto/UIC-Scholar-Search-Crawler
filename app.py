from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

from scraper.uic_profile import scrape_profiles
from scraper.uic_staff import scrape_uic_staff
from scraper.google_scholar import scrape_scholar_profiles
import traceback

from csv_utils import extract_single_row_from_csv, merge_csv, read_user_ids
from scraper.custom_types import UserID
from typing import List

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

try:
    user_ids: List[UserID] = read_user_ids('uic_staff_user_ids.csv')
    scrape_scholar_profiles(driver=driver, staff_user_ids=user_ids, limit=None)
    
except Exception as e:
    traceback.print_exc()