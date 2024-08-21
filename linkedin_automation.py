import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize the Chrome driver using WebDriverManager with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Fetch the LinkedIn email and password from environment variables
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# Ensure that the email and password are properly set
if LINKEDIN_EMAIL is None or LINKEDIN_PASSWORD is None:
    raise ValueError("LinkedIn email or password environment variables are not set")

# Correct usage of os.getenv to retrieve file paths
CV_FILE_PATH = os.getenv('CV_FILE_PATH', '/Users/jamespares/Downloads/PMO - CV-15.pdf')
COVER_LETTER_PATH = os.getenv('COVER_LETTER_PATH', '/Users/jamespares/Downloads/PM - Cover Letter.pdf')

# Check if file paths exist
if not os.path.exists(CV_FILE_PATH):
    logging.error(f"CV file not found at path: {CV_FILE_PATH}")
    exit(1)
if not os.path.exists(COVER_LETTER_PATH):
    logging.warning(f"Cover letter file not found at path: {COVER_LETTER_PATH}")


def linkedin_login():
    logging.info("Logging into LinkedIn...")
    driver.get('https://www.linkedin.com/login')

    email_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')

    email_field.send_keys(LINKEDIN_EMAIL)
    password_field.send_keys(LINKEDIN_PASSWORD)
    password_field.send_keys(Keys.RETURN)

    # Wait until the home page is loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'global-nav')))
    logging.info("Logged in successfully.")

def random_sleep(min_seconds=5, max_seconds=15):
    time_to_sleep = random.uniform(min_seconds, max_seconds)
    logging.info(f"Sleeping for {time_to_sleep:.2f} seconds to mimic human behavior...")
    time.sleep(time_to_sleep)

def apply_to_saved_jobs():
    logging.info("Navigating to saved jobs...")
    driver.get('https://www.linkedin.com/my-items/saved-jobs/')
    random_sleep(3, 5)

    saved_jobs = driver.find_elements(By.XPATH, "//a[contains(@href, '/jobs/view')]")

    for job in saved_jobs:
        try:
            job.click()
            random_sleep(3, 6)

            easy_apply_button = driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
            easy_apply_button.click()

            random_sleep(2, 4)  # Wait for the application dialog to load

            # Upload CV and cover letter if required
            try:
                upload_cv_input = driver.find_element(By.XPATH, "//input[@type='file' and @name='file']")
                upload_cv_input.send_keys(CV_FILE_PATH)
                random_sleep(2, 4)

                if COVER_LETTER_PATH and os.path.exists(COVER_LETTER_PATH):
                    try:
                        upload_cover_letter_input = driver.find_element(By.XPATH, "//input[@type='file' and @name='fileCoverLetter']")
                        upload_cover_letter_input.send_keys(COVER_LETTER_PATH)
                        random_sleep(2, 4)
                    except NoSuchElementException:
                        logging.info("Cover letter upload not required for this job.")
                else:
                    logging.warning("Cover letter path is not set or file does not exist.")

            except NoSuchElementException:
                logging.info("CV upload not required for this job.")

            # Check if the application has additional questions
            try:
                submit_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
                submit_button.click()
                logging.info("Application submitted successfully.")
                random_sleep(5, 10)  # Wait before proceeding to the next job

            except NoSuchElementException:
                # Handle additional questions
                question_fields = driver.find_elements(By.XPATH, "//input[@aria-label]")

                for field in question_fields:
                    question_text = field.get_attribute('aria-label')
                    answer = input(f"Question: {question_text}\nYour answer: ")
                    field.send_keys(answer)

                submit_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
                submit_button.click()
                logging.info("Application submitted successfully after answering the questions.")
                random_sleep(5, 10)  # Wait before proceeding to the next job

        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Failed to apply or job does not have Easy Apply option. Error: {e}")

        finally:
            # Go back to the list of saved jobs
            driver.get('https://www.linkedin.com/my-items/saved-jobs/')
            random_sleep(10, 20)  # Longer wait before going back to the list of saved jobs

def main():
    linkedin_login()
    apply_to_saved_jobs()
    driver.quit()

if __name__ == "__main__":
    main()
