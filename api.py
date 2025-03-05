import json
import os
import tempfile
import time
import requests
import openpyxl
import pywhatkit
import base64

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from flask import Flask, jsonify, send_file
from datetime import datetime, timezone
import uvicorn
from pymongo import MongoClient

# برای دریافت QR کد با استفاده از Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------------
from selenium.webdriver.chrome.service import Service  # اضافه کنید
import traceback  # برای نمایش خطای کامل در لاگ‌ها

from fastapi import FastAPI
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64

# اتصال به MongoDB
uri = "mongodb://localhost:27017"
try:
    mongo_client = MongoClient(uri)
    db = mongo_client.whatsapp_marketing
    messages_collection = db.messages
    print("اتصال به MongoDB موفقیت‌آمیز بود.")
except Exception as e:
    raise Exception(f"خطا در اتصال به MongoDB: {e}")

app = FastAPI(title="WhatsApp Marketing API")

# ----------------------------
# ارسال پیام‌های گروهی (Bulk)
# ----------------------------
@app.post("/send-messages")
async def send_messages(
    excel_file: UploadFile = File(...),
    message: str = Form(...),
    image: UploadFile = File(None),
    delay: int = Form(3),
    delay_every: int = Form(5),
    telegram_id: str = Form(None)
):
    try:
        # ذخیره فایل اکسل به صورت موقت
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await excel_file.read())
            excel_path = tmp.name

        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook.active
        contacts = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0]:
                phone = str(row[0]).strip()
                name = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                contacts.append({"phone": phone, "name": name})
        
        if not contacts:
            raise HTTPException(status_code=400, detail="هیچ مخاطبی در فایل اکسل یافت نشد.")
        
        image_path = None
        if image:
            _, ext = os.path.splitext(image.filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as img_tmp:
                img_tmp.write(await image.read())
                image_path = img_tmp.name

        total = len(contacts)
        results = []
        for idx, contact in enumerate(contacts, start=1):
            phone = contact["phone"]
            personalized_message = message.replace("{NAME}", contact["name"]).replace("{NUMBER}", phone)
            try:
                if image_path:
                    pywhatkit.sendwhats_image(phone, image_path, caption=personalized_message, wait_time=20, tab_close=True, close_time=6)
                else:
                    pywhatkit.sendwhatmsg_instantly(phone, personalized_message, wait_time=10, tab_close=True, close_time=5)
                status = "Success"
                results.append({"phone": phone, "status": status})
            except Exception as e:
                status = f"Failed: {str(e)}"
                results.append({"phone": phone, "status": status})
            
            record = {
                "telegram_id": telegram_id,
                "phone": phone,
                "name": contact["name"],
                "message": personalized_message,
                "status": status,
                "type": "bulk",
                "timestamp": datetime.now(timezone.utc)
            }
            messages_collection.insert_one(record)
            
            if idx % delay_every == 0 and idx < total:
                time.sleep(delay)

        os.remove(excel_path)
        if image_path:
            os.remove(image_path)

        return JSONResponse(content={"detail": "ارسال پیام‌ها به اتمام رسید.", "results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ----------------------------
# ارسال پیام تکی (Single)
# ----------------------------
@app.post("/send-single-message")
async def send_single_message(
    phone: str = Form(..., description="شماره تلفن مخاطب"),
    message: str = Form(..., description="متن پیام جهت ارسال"),
    image: UploadFile = File(None, description="فایل تصویری اختیاری جهت ارسال همراه پیام"),
    telegram_id: str = Form(None, description="شناسه تلگرام کاربر")
):
    try:
        image_path = None
        if image:
            _, ext = os.path.splitext(image.filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(await image.read())
                image_path = tmp.name
            try:
                pywhatkit.sendwhats_image(phone, image_path, caption=message, wait_time=20, tab_close=True, close_time=5)
            finally:
                os.remove(image_path)
        else:
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=5)
        
        record = {
            "telegram_id": telegram_id,
            "phone": phone,
            "message": message,
            "status": "Success",
            "type": "single",
            "timestamp": datetime.now(timezone.utc)
        }
        messages_collection.insert_one(record)
        
        return JSONResponse(content={"detail": "پیام ارسال شد", "phone": phone, "status": "Success"})
    except Exception as e:
        record = {
            "telegram_id": telegram_id,
            "phone": phone,
            "message": message,
            "status": f"Failed: {str(e)}",
            "type": "single",
            "timestamp": datetime.now(timezone.utc)
        }
        messages_collection.insert_one(record)
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# دریافت QR کد واتساپ (با Selenium)

app = FastAPI()
@app.get("/whatsapp-qr")
async def get_whatsapp_qr():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')

    try:
        wait = WebDriverWait(driver, 30)
        canvas = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'canvas')))
        qr_code_base64 = canvas.screenshot_as_base64
        driver.quit()
        return JSONResponse(content={"success": True, "qrCode": qr_code_base64})
    except Exception as e:
        driver.quit()
        return JSONResponse(content={"success": False, "error": f"Failed to retrieve QR code: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/health")
def health_check():
    return {"status": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
