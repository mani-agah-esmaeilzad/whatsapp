import logging
import base64
import os
import tempfile
import requests
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# آدرس سرویس API FastAPI
API_BASE_URL = "http://localhost:8000"

# تعریف stateهای مکالمه
BULK_EXCEL, BULK_MESSAGE, BULK_IMAGE, BULK_DELAY, BULK_DELAY_EVERY = range(5)
SINGLE_PHONE, SINGLE_MESSAGE, SINGLE_IMAGE = range(5, 8)

def normalize_phone_number(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith('+98'):
        phone = phone[3:]
    elif phone.startswith('0098'):
        phone = phone[4:]
    elif phone.startswith('0'):
        phone = phone[1:]
    return '+98' + phone

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # اگر کاربر هنوز وارد حساب نشده باشد، فقط دکمه ورود نمایش داده می‌شود.
    if not context.user_data.get("logged_in"):
        keyboard = [
            [InlineKeyboardButton("ورود به واتساپ", callback_data="login")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("لطفاً ابتدا وارد حساب واتساپ خود شوید.", reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("ارسال پیام گروهی", callback_data="bulk")],
            [InlineKeyboardButton("ارسال پیام تکی", callback_data="single")],
            [InlineKeyboardButton("دریافت مجدد QR کد", callback_data="qr")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

# --- بخش ورود (Login) ---

async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("در حال دریافت QR کد برای ورود، لطفاً چند لحظه صبر کنید...")
    try:
        response = requests.get(f"{API_BASE_URL}/whatsapp-qr", timeout=60)
        result = response.json()
        if result.get("success"):
            qr_code_base64 = result.get("qrCode")
            qr_code_bytes = base64.b64decode(qr_code_base64)
            keyboard = [
                [InlineKeyboardButton("ورود انجام شد", callback_data="logged_in")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_photo(
                photo=qr_code_bytes,
                caption="لطفاً QR کد را اسکن کنید و سپس روی «ورود انجام شد» کلیک کنید.",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("خطا در دریافت QR کد.")
    except Exception as e:
        await query.edit_message_text(f"خطا در دریافت QR کد: {e}")

async def logged_in_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data["logged_in"] = True
    keyboard = [
        [InlineKeyboardButton("ارسال پیام گروهی", callback_data="bulk")],
        [InlineKeyboardButton("ارسال پیام تکی", callback_data="single")],
        [InlineKeyboardButton("دریافت مجدد QR کد", callback_data="qr")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("ورود با موفقیت انجام شد. لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

# --- تابع دریافت QR کد (برای هندلر "qr") ---
async def qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("در حال دریافت QR کد، لطفاً چند لحظه صبر کنید...")
    try:
        response = requests.get(f"{API_BASE_URL}/whatsapp-qr", timeout=60)
        result = response.json()
        if result.get("success"):
            qr_code_base64 = result.get("qrCode")
            qr_code_bytes = base64.b64decode(qr_code_base64)
            await query.message.reply_photo(photo=qr_code_bytes, caption="QR کد دریافت شد. لطفاً آن را اسکن کنید:")
        else:
            await query.edit_message_text("خطا در دریافت QR کد.")
    except Exception as e:
        await query.edit_message_text(f"خطا در دریافت QR کد: {e}")
        
# --- مکالمه ارسال پیام گروهی (Bulk) ---
async def bulk_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("لطفاً فایل اکسل مخاطبین (فرمت .xlsx یا .xls) را ارسال کنید.")
    return BULK_EXCEL

async def bulk_receive_excel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    document = update.message.document
    if not document or not document.file_name.endswith(('.xlsx', '.xls')):
        await update.message.reply_text("لطفاً یک فایل اکسل معتبر ارسال کنید.")
        return BULK_EXCEL

    file = await document.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.file_name)[1]) as tmp:
        excel_path = tmp.name
        await file.download_to_drive(custom_path=excel_path)
    context.user_data["excel_path"] = excel_path
    await update.message.reply_text("فایل دریافت شد.\nحال پیام متنی را ارسال کنید (می‌توانید از {NAME} و {NUMBER} استفاده کنید).")
    return BULK_MESSAGE

async def bulk_receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text:
        await update.message.reply_text("متن پیام نمی‌تواند خالی باشد. لطفاً پیام را ارسال کنید.")
        return BULK_MESSAGE
    context.user_data["message"] = text
    await update.message.reply_text(
        "در صورت تمایل، یک تصویر جهت ارسال همراه پیام ارسال کنید.\n"
        "در غیر این صورت با ارسال دستور /skip این مرحله را رد کنید."
    )
    return BULK_IMAGE

async def bulk_receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        suffix = ".jpg"
    elif update.message.document:
        if not update.message.document.file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            await update.message.reply_text("لطفاً یک فایل تصویری معتبر ارسال کنید.")
            return BULK_IMAGE
        file = await update.message.document.get_file()
        suffix = os.path.splitext(update.message.document.file_name)[1]
    else:
        await update.message.reply_text("لطفاً یک فایل تصویری ارسال کنید یا /skip را وارد کنید.")
        return BULK_IMAGE

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        image_path = tmp.name
        await file.download_to_drive(custom_path=image_path)
    context.user_data["image_path"] = image_path
    await update.message.reply_text("تصویر دریافت شد.\nلطفاً مقدار تاخیر (به ثانیه) پس از ارسال چند پیام را وارد کنید (مثلاً 3).")
    return BULK_DELAY

async def bulk_skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["image_path"] = None
    await update.message.reply_text("تصویری دریافت نشد.\nلطفاً مقدار تاخیر (به ثانیه) پس از ارسال چند پیام را وارد کنید (مثلاً 3).")
    return BULK_DELAY

async def bulk_receive_delay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        delay = int(update.message.text)
    except ValueError:
        await update.message.reply_text("لطفاً یک عدد صحیح وارد کنید.")
        return BULK_DELAY
    context.user_data["delay"] = delay
    await update.message.reply_text("حال تعداد پیام قبل از اعمال تاخیر را وارد کنید (مثلاً 5).")
    return BULK_DELAY_EVERY

async def bulk_receive_delay_every(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        delay_every = int(update.message.text)
    except ValueError:
        await update.message.reply_text("لطفاً یک عدد صحیح وارد کنید.")
        return BULK_DELAY_EVERY
    context.user_data["delay_every"] = delay_every

    excel_path = context.user_data["excel_path"]
    data = {
        "message": context.user_data["message"],
        "delay": context.user_data["delay"],
        "delay_every": context.user_data["delay_every"],
        "telegram_id": str(update.effective_user.id)
    }
    files = {
        "excel_file": open(excel_path, "rb")
    }
    if context.user_data.get("image_path"):
        files["image"] = open(context.user_data["image_path"], "rb")

    await update.message.reply_text("در حال ارسال پیام‌ها، لطفاً چند لحظه صبر کنید...")
    try:
        response = requests.post(f"{API_BASE_URL}/send-messages", data=data, files=files, timeout=120)
        result = response.json()
        reply_text = f"نتیجه ارسال:\n{json.dumps(result, ensure_ascii=False)}"
    except Exception as e:
        reply_text = f"خطا در ارسال پیام‌ها: {e}"

    try:
        os.remove(excel_path)
    except Exception as e:
        logger.error(f"خطا در حذف فایل اکسل: {e}")
    if context.user_data.get("image_path"):
        try:
            os.remove(context.user_data["image_path"])
        except Exception as e:
            logger.error(f"خطا در حذف فایل تصویر: {e}")

    await update.message.reply_text(reply_text)
    return ConversationHandler.END

# --- مکالمه ارسال پیام تکی (Single) ---
async def single_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("لطفاً شماره تلفن مخاطب (بدون نیاز به وارد کردن کد کشور) را ارسال کنید.\n(مثلاً 9123456789)")
    return SINGLE_PHONE

async def single_receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text
    if not phone:
        await update.message.reply_text("شماره تلفن نمی‌تواند خالی باشد. لطفاً شماره را ارسال کنید.")
        return SINGLE_PHONE
    normalized = normalize_phone_number(phone)
    context.user_data["phone"] = normalized
    await update.message.reply_text(f"شماره شما به این صورت تنظیم شد: {normalized}\nحال پیام متنی را ارسال کنید.")
    return SINGLE_MESSAGE

async def single_receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text:
        await update.message.reply_text("متن پیام نمی‌تواند خالی باشد. لطفاً پیام را ارسال کنید.")
        return SINGLE_MESSAGE
    context.user_data["message"] = text
    await update.message.reply_text(
        "در صورت تمایل، یک تصویر جهت ارسال همراه پیام ارسال کنید.\n"
        "در غیر این صورت با ارسال دستور /skip این مرحله را رد کنید."
    )
    return SINGLE_IMAGE

async def single_receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        suffix = ".jpg"
    elif update.message.document:
        if not update.message.document.file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            await update.message.reply_text("لطفاً یک فایل تصویری معتبر ارسال کنید.")
            return SINGLE_IMAGE
        file = await update.message.document.get_file()
        suffix = os.path.splitext(update.message.document.file_name)[1]
    else:
        await update.message.reply_text("لطفاً یک فایل تصویری ارسال کنید یا /skip را وارد کنید.")
        return SINGLE_IMAGE

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        image_path = tmp.name
        await file.download_to_drive(custom_path=image_path)
    context.user_data["image_path"] = image_path
    return await single_send_message(update, context)

async def single_skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["image_path"] = None
    return await single_send_message(update, context)

async def single_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = {
        "phone": context.user_data["phone"],
        "message": context.user_data["message"],
        "telegram_id": str(update.effective_user.id)
    }
    await update.message.reply_text("در حال ارسال پیام، لطفاً چند لحظه صبر کنید...")
    try:
        files = {}
        if context.user_data.get("image_path"):
            files["image"] = open(context.user_data["image_path"], "rb")
        response = requests.post(f"{API_BASE_URL}/send-single-message", data=data, files=files, timeout=60)
        reply_text = "پیغام با موفقیت ارسال شد"
    except Exception as e:
        reply_text = f"خطا در ارسال پیام: {e}"
    await update.message.reply_text(reply_text)
    if context.user_data.get("image_path"):
        try:
            os.remove(context.user_data["image_path"])
        except Exception as e:
            logger.error(f"خطا در حذف فایل تصویر: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def main() -> None:
    TOKEN = "7227922627:AAHmO2VAMcaACaWjoGEif-UQ2Pz6Y0B0z9A"  # توکن ربات تلگرام خود را جایگزین کنید

    application = Application.builder().token(TOKEN).build()

    bulk_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bulk_start, pattern="^bulk$")],
        states={
            BULK_EXCEL: [MessageHandler(filters.Document.ALL, bulk_receive_excel)],
            BULK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_receive_message)],
            BULK_IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, bulk_receive_image),
                CommandHandler("skip", bulk_skip_image)
            ],
            BULK_DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_receive_delay)],
            BULK_DELAY_EVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_receive_delay_every)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
    )

    single_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(single_start, pattern="^single$")],
        states={
            SINGLE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, single_receive_phone)],
            SINGLE_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, single_receive_message)],
            SINGLE_IMAGE: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, single_receive_image),
                CommandHandler("skip", single_skip_image)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
    )

    # هندلرهای مربوط به ورود (login) و دریافت QR کد
    login_handler_cb = CallbackQueryHandler(login_handler, pattern="^login$")
    logged_in_handler_cb = CallbackQueryHandler(logged_in_handler, pattern="^logged_in$")
    qr_conv_handler = CallbackQueryHandler(qr_handler, pattern="^qr$")

    start_handler = CommandHandler("start", start)

    application.add_handler(start_handler)
    application.add_handler(login_handler_cb)
    application.add_handler(logged_in_handler_cb)
    application.add_handler(bulk_conv_handler)
    application.add_handler(single_conv_handler)
    application.add_handler(qr_conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
