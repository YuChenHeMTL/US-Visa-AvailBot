import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint
from tqdm import tqdm
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

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

client = Client(twilio_sid, twilio_token)

target = datetime.strptime("30 August, 2025", "%d %B, %Y")

driver = webdriver.Chrome()
driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")
custom_range_sleep(8, 12)
# enter email
driver.find_element("id", "user_email").send_keys(login_email)
custom_range_sleep(1, 3)
# enter password
driver.find_element("id", "user_password").send_keys(login_password)
custom_range_sleep(1, 3)
# click the confirm policy checkbox
driver.find_element(By.CLASS_NAME, "icheck-area-20").click()
# print(checkbox)
# checkbox[0].click()
# driver.find_element("id", "policy_confirmed").click()
custom_range_sleep(1, 3)
driver.find_element("name","commit").click()
custom_range_sleep(8, 12)

# click continue
driver.find_element(By.CSS_SELECTOR, "a[href*='continue_actions']").click()
custom_range_sleep(5, 8)

# click Pay Visa Fee
accordions = driver.find_elements(By.CLASS_NAME, "accordion-item")
accordions[0].click()
custom_range_sleep(2, 4)
# click Pay Visa Fee button
driver.find_element(By.CLASS_NAME, "small-only-expanded").click()
custom_range_sleep(5, 8)

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
    print(message.__dict__)

    time.sleep(1)

    self_message = client.messages.create(
        from_=from_phone_number,
        body=text_message,
        to=self_phone_number,
    )
    print(self_message.body)

driver.quit()