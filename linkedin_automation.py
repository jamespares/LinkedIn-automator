from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
import random

# Configuration
LINKEDIN_EMAIL = 'your-email@example.com'
LINKEDIN_PASSWORD = 'your-password'
CV_FILE_PATH = '/path/to/your/cv.pdf'
COVER_LETTER_PATH = '/path/to/your/cover_letter.pdf'

# Initialize the Chrome driver
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')


def linkedin_login():
    driver.get('https://www.linkedin.com/login')

    email_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')

    email_field.send_keys(LINKEDIN_EMAIL)
    password_field.send_keys(LINKEDIN_PASSWORD)
    password_field.send_keys(Keys.RETURN)

    # Wait until the home page is loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'global-nav')))


def random_sleep(min_seconds=5, max_seconds=15):
    time_to_sleep = random.uniform(min_seconds, max_seconds)
    print(f"Sleeping for {time_to_sleep:.2f} seconds to mimic human behavior...")
    time.sleep(time_to_sleep)


def apply_to_saved_jobs():
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

                # Optionally upload the cover letter if requested
                try:
                    upload_cover_letter_input = driver.find_element(By.XPATH,
                                                                    "//input[@type='file' and @name='fileCoverLetter']")
                    upload_cover_letter_input.send_keys(COVER_LETTER_PATH)
                    random_sleep(2, 4)
                except NoSuchElementException:
                    print("Cover letter upload not required for this job.")

            except NoSuchElementException:
                print("CV upload not required for this job.")

            # Check if the application has additional questions
            try:
                submit_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
                submit_button.click()
                print("Application submitted successfully.")
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
                print("Application submitted successfully after answering the questions.")
                random_sleep(5, 10)  # Wait before proceeding to the next job

        except (NoSuchElementException, TimeoutException):
            print("Failed to apply or job does not have Easy Apply option.")

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
