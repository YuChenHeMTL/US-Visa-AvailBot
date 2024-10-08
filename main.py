import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint
from tqdm import tqdm
from datetime import datetime
from twilio.rest import Client
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
login_email = os.environ.get("LOGIN_EMAIL")
login_password = os.environ.get("LOGIN_PASSWORD")
target_phone_number = os.environ.get("TARGET_PHONE_NUMBER")
self_phone_number = os.environ.get("SELF_PHONE_NUMBER")
from_phone_number = os.environ.get("FROM_PHONE_NUMBER")
message_service_id = os.environ.get("MESSAGE_SERVICE_ID")
# print(twilio_sid, twilio_token, login_email, login_password, target_phone_number, self_phone_number, from_phone_number, message_service_id)

client = Client(twilio_sid, twilio_token)

target = datetime.strptime("30 August, 2025", "%d %B, %Y")

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

success_count = int(r.get('success_count'))
failure_count = int(r.get('failure_count'))
exception_count = int(r.get('exception_count'))
time_spend = float(r.get('time_spend'))
# success_count = 9
# failure_count = 1318
# exception_count = 241
# time_spend = 74823.70827031136

chrome_options = Options()
chrome_options.add_argument("--headless=new") # for Chrome >= 109
service = Service("/usr/lib/chromium-browser/chromedriver")
timeout_delay = 6

while True:
    try:
        start = time.time()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.ID, "user_email")))
        except TimeoutException:
            print("Initial Loading took too much time!")
            failure_count += 1
        # custom_range_sleep(6, 10)
        # enter email
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
            failure_count += 1
            continue
        # custom_range_sleep(2, 4)

        # click continue
        driver.find_element(By.CSS_SELECTOR, "a[href*='continue_actions']").click()
        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.CLASS_NAME, "accordion-item")))
        except TimeoutException:
            print("Accordion Loading took too much time!")
            failure_count += 1
            continue
        # custom_range_sleep(2, 4)

        # click Pay Visa Fee
        accordions = driver.find_elements(By.CLASS_NAME, "accordion-item")
        accordions[0].click()
        custom_range_sleep(1, 1)
        # click Pay Visa Fee button
        driver.find_element(By.CLASS_NAME, "small-only-expanded").click()
        # custom_range_sleep(2, 4)

        try:
            WebDriverWait(driver, timeout_delay).until(EC.presence_of_element_located((By.CLASS_NAME, "for-layout")))
        except TimeoutException:
            print("Table Loading took too much time!")
            failure_count += 1
            continue

        # find table
        table = driver.find_element(By.CLASS_NAME, "for-layout")
        rows = table.find_elements(By.TAG_NAME, "tr")

        text_message = ""

        for row in rows:
            # for each row, find all td
            cols = row.find_elements(By.TAG_NAME, "td")
            city = cols[0].text
            app_time = cols[1].text
            try:
                formatted_app_time = datetime.strptime(app_time, "%d %B, %Y")
                if (formatted_app_time < target):
                    text_message += f"City: {city}, Appointment Time: {app_time} found \n"
            except:
                pass

        if text_message != "":
            print(text_message)

            message = client.messages.create(
                from_=from_phone_number,
                body=text_message,
                to=target_phone_number,
            )

            time.sleep(1)

            self_message = client.messages.create(
                from_=from_phone_number,
                body=text_message,
                to=self_phone_number,
            )

            success_count += 1
            logging.info("Earlier appointment found: " + text_message)
            print("Earlier appointment found: " + text_message)
        else:
            logging.info("No earlier appointment found")
            print("No earlier appointment found")
            failure_count += 1

        driver.close()
        end = time.time()
        time_spend += end - start
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        print(f"Exception occurred: {e}")
        exception_count += 1

    total_count = success_count + failure_count + exception_count
    print(f"Success Count: {success_count}/{total_count}")
    print(f"Failure Count: {failure_count}/{total_count}")
    print(f"Exception Count: {exception_count}/{total_count}")
    print(f"Total time spent: {time_spend}")

    r.set('success_count', success_count)
    r.set('failure_count', failure_count)
    r.set('exception_count', exception_count)
    r.set('time_spend', time_spend)

    logging.info(f"Success Count: {success_count}/{total_count}")
    logging.info(f"Failure Count: {failure_count}/{total_count}")
    logging.info(f"Exception Count: {exception_count}/{total_count}")
    logging.info(f"Total time spent: {time_spend}")

    custom_range_sleep(10, 15)