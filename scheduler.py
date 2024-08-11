import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint
from tqdm import tqdm
from datetime import datetime
from twilio.rest import Client
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import logging
import redis

load_dotenv()

logging.basicConfig(filename='logs.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def custom_sleep(seconds):
    for _ in tqdm(range(seconds), desc="Sleeping"):
        time.sleep(1)

def custom_range_sleep(start, end):
    for _ in tqdm(range(randint(start, end)), desc="Sleeping"):
        time.sleep(1)

twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
login_email = os.environ.get("SCHEDULE_EMAIL")
login_password = os.environ.get("SCHEDULE_PASSWORD")
target_phone_number = os.environ.get("TARGET_PHONE_NUMBER")
self_phone_number = os.environ.get("SELF_PHONE_NUMBER")
from_phone_number = os.environ.get("FROM_PHONE_NUMBER")
message_service_id = os.environ.get("MESSAGE_SERVICE_ID")

client = Client(twilio_sid, twilio_token)

target = datetime.strptime("30 August, 2025", "%d %B, %Y")

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# success_count = int(r.get('success_count'))
# failure_count = int(r.get('failure_count'))
# exception_count = int(r.get('exception_count'))
# time_spend = float(r.get('time_spend'))
success_count = 15
failure_count = 1424
exception_count = 241
time_spend = 77902.30569982529

chrome_options = Options()
# chrome_options.add_argument("--headless=new") # for Chrome >= 109
timeout_delay = 6

def schedule(location, target_time):
    try:
        start = time.time()
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.ID, "user_email")))
        except TimeoutException:
            print("Initial Loading took too much time!")

        driver.find_element("id", "user_email").send_keys(login_email)
        custom_range_sleep(1, 1)
        # enter password
        driver.find_element("id", "user_password").send_keys(login_password)
        custom_range_sleep(1, 1)
        # click the confirm policy checkbox
        driver.find_element(By.CLASS_NAME, "icheck-area-20").click()
        # print(checkbox)
        # checkbox[0].click()
        # driver.find_element("id", "policy_confirmed").click()
        custom_range_sleep(1, 1)
        driver.find_element("name","commit").click()
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='continue_actions']")))
        except TimeoutException:
            print("Second Loading took too much time!")
        
        # click continue
        driver.find_element(By.CSS_SELECTOR, "a[href*='continue_actions']").click()
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.CLASS_NAME, "accordion-item")))
        except TimeoutException:
            print("Accordion Loading took too much time!")
            
        accordions = driver.find_elements(By.CLASS_NAME, "accordion-item")
        accordions[0].click()
        custom_range_sleep(1, 1)
        # click Pay Visa Fee button
        driver.find_element(By.CLASS_NAME, "small-only-expanded").click()
        # custom_range_sleep(2, 4)

        # find location dropdown
        # location_dropdown = driver.find_element(By.ID, "appointments_consulate_appointment_facility_id")
        # # check if target location is already selected
        # if location_dropdown.text != location:
        #     location_dropdown.click()
            
        #     # find location within dropdown options
        #     location_options = location_dropdown.find_elements(By.TAG_NAME, "option")
        #     for option in location_options:
        #         if option.text == location:
        #             custom_sleep(3)
        #             option.click()
        #             custom_sleep(3)
        #             break
        
        # find time dropdown
        custom_sleep(5)
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.ID, "appointments_consulate_appointment_date_input")))
        except TimeoutException:
            print("Date Input Loading took too much time!")
        time_dropdown = driver.find_element(By.ID, "appointments_consulate_appointment_date_input")
        time_dropdown.click()
        custom_sleep(1)

        # find month and year in calendar selector
        # if not, click the next month button
        calendar = driver.find_element(By.ID, "ui-datepicker-div")
        calendar_header = calendar.find_element(By.CLASS_NAME, "ui-corner-right")
        calendar_date = datetime.strptime(str(calendar_header.text.split("\n")[1]), "%B %Y")
        while calendar_date.month != target_time.month or calendar_date.year != target_time.year:
            calendar_header.find_element(By.CLASS_NAME, "ui-datepicker-next").click()
            calendar_header = calendar.find_element(By.CLASS_NAME, "ui-corner-right")
            calendar_date = datetime.strptime(str(calendar_header.text.split("\n")[1]), "%B %Y")
            time.sleep(0.2)
            # print(calendar_date, target_time)
            # custom_sleep(1)
        # 
        custom_sleep(10)
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        print(f"Exception occurred: {e}")

schedule("Toronto", target)