import customtkinter as ctk

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# دیکشنری زبان‌ها
languages = {
    "English": {
        "title": "WhatsApp Marketing",
        "target_label": "Target",
        "upload_excel": "Upload Excel",
        "download_sample_excel": "Download Sample Excel",
        "number_column": "Number",
        "name_column": "Name",
        "message_section": "Message",
        "message_tab": "Message",
        "polls": "Polls",
        "add_poll": "Add Poll",
        "buttons": "Buttons",
        "add_button": "Add Button",
        "attachments": "Attachments",
        "add_file": "Add File",
        "accounts": "Accounts",
        "language_option": "Language",
        "delay_settings": "Delay Settings",
        "wait_label": "Wait",
        "seconds_after_every": "seconds after every",
        "messages_label": "messages",
        "send_mode": "Send Mode",
        "manual": "Manual",
        "auto": "Automatic",
        "start_sending": "Start Sending",
        "group_send": "Group Message Sending",
        "single_send": "Single Message Sending",
        "phone_label": "Phone Number:",
        "single_message_label": "Message:",
        "send_button": "Send",
        "connection_status_default": "Connection status: Unknown",
        "error_connection": "Connection error. Please check your internet or WhatsApp login.",
        "error_empty": "No numbers, messages, or polls to send.",
        "success_sent": "All messages have been sent!",
        "error_sending": "Error sending message:",
        "exit_button": "Exit"
    },
    "Persian": {
        "title": "بازاریابی واتساپ",
        "target_label": "هدف",
        "upload_excel": "بارگذاری اکسل",
        "download_sample_excel": "دانلود فایل اکسل نمونه",
        "number_column": "شماره",
        "name_column": "نام",
        "message_section": "پیام",
        "message_tab": "پیام",
        "polls": "نظرسنجی",
        "add_poll": "افزودن نظرسنجی",
        "buttons": "دکمه‌ها",
        "add_button": "افزودن دکمه",
        "attachments": "پیوست‌ها",
        "add_file": "افزودن فایل",
        "accounts": "حساب‌ها",
        "language_option": "زبان",
        "delay_settings": "تنظیم تاخیر",
        "wait_label": "انتظار",
        "seconds_after_every": "ثانیه بعد از هر",
        "messages_label": "پیام",
        "send_mode": "نوع ارسال",
        "manual": "دستی",
        "auto": "خودکار",
        "start_sending": "شروع ارسال",
        "group_send": "ارسال پیام گروهی",
        "single_send": "ارسال پیام تکی",
        "phone_label": "شماره تلفن:",
        "single_message_label": "پیام:",
        "send_button": "ارسال",
        "connection_status_default": "وضعیت اتصال: نامشخص",
        "error_connection": "خطا در اتصال. لطفاً اینترنت یا ورود به واتساپ را بررسی کنید.",
        "error_empty": "شماره، پیام یا نظرسنجی برای ارسال وجود ندارد.",
        "success_sent": "تمام پیام‌ها ارسال شدند!",
        "error_sending": "خطا در ارسال پیام:",
        "exit_button": "خروج"
    }
}

current_lang = "English"

def get_font(size, weight="normal"):
    if current_lang == "Persian":
        return ctk.CTkFont(family="vazir", size=size, weight=weight)
    else:
        return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)

def get_ttk_font():
    if current_lang == "Persian":
        return ("vazir", 12)
    else:
        return ("Segoe UI", 12)

def get_ttk_heading_font():
    if current_lang == "Persian":
        return ("vazir", 12, "bold")
    else:
        return ("Segoe UI", 12, "bold")
