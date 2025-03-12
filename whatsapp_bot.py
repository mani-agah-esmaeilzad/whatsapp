from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SESSION_FILE = "whatsapp_session.json"

def initiate_connection():
    chrome_options = Options()
    # حالت قابل مشاهده برای اسکن QR
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com")
    print("Please scan the QR code in the opened browser window.")
    input("Press Enter after scanning the QR code...")
    # ذخیره کوکی‌ها
    cookies = driver.get_cookies()
    with open(SESSION_FILE, "w") as f:
        json.dump(cookies, f)
    driver.quit()
    return cookies

def load_driver_headless():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com")
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] is None:
                cookie["sameSite"] = "Strict"
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print("Error adding cookie:", e)
        driver.refresh()
    time.sleep(5)  # صبر برای بارگذاری نشست
    return driver

def send_message(driver, phone, message):
    url = f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}"
    driver.get(url)
    time.sleep(5)  # صبر برای بارگذاری صفحه
    try:
        # پیدا کردن جعبه ورودی و ارسال کلید Enter جهت ارسال پیام
        input_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
        )
        time.sleep(2)
    except Exception as e:
        print("Error sending message:", e)
