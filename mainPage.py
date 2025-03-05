import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import openpyxl
import requests
import webbrowser
import pywhatkit
import pyautogui
import time
import os
import threading
from io import BytesIO
from PIL import Image
import win32clipboard
from deep_translator import GoogleTranslator 
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

# تنظیمات فونت
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

# کپی تصویر به کلیپ‌بورد
def copy_image_to_clipboard(image_path):
    try:
        image = Image.open(image_path)
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"خطا در کپی تصویر به کلیپ‌بورد: {e}")

# کلاس جایگزین برای Spinbox
class SpinboxAlternative(ctk.CTkFrame):
    def __init__(self, parent, from_=1, to=9999, width=60, textvariable=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.from_ = from_
        self.to = to
        if textvariable is None:
            self.var = tk.IntVar(value=self.from_)
        else:
            self.var = textvariable
        self.btn_minus = ctk.CTkButton(self, text="-", width=30, command=self.decrement, corner_radius=5)
        self.btn_minus.grid(row=0, column=0, padx=2)
        self.entry = ctk.CTkEntry(self, width=width, textvariable=self.var)
        self.entry.grid(row=0, column=1, padx=2)
        self.btn_plus = ctk.CTkButton(self, text="+", width=30, command=self.increment, corner_radius=5)
        self.btn_plus.grid(row=0, column=2, padx=2)

    def increment(self):
        try:
            value = int(self.var.get())
        except ValueError:
            value = self.from_
        if value < self.to:
            value += 1
        self.var.set(value)

    def decrement(self):
        try:
            value = int(self.var.get())
        except ValueError:
            value = self.from_
        if value > self.from_:
            value -= 1
        self.var.set(value)

# پنجره‌ی افزودن نظرسنجی
class PollWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Add Poll" if current_lang == "English" else "افزودن نظرسنجی")
        self.geometry("400x400")
        question_label = ctk.CTkLabel(self, text=("Poll Question:" if current_lang == "English" else "سوال نظرسنجی:"), font=get_font(14, "bold"))
        question_label.pack(padx=10, pady=10)
        self.question_entry = ctk.CTkEntry(self, font=get_font(14))
        self.question_entry.pack(padx=10, pady=10, fill="x")
        options_label = ctk.CTkLabel(self, text=("Poll Options (one per line):" if current_lang == "English" else "گزینه‌های نظرسنجی (هر گزینه در یک خط):"), font=get_font(14, "bold"))
        options_label.pack(padx=10, pady=10)
        self.options_textbox = ctk.CTkTextbox(self, font=get_font(14), height=150, wrap="word")
        self.options_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        add_button = ctk.CTkButton(self, text=("Add Poll" if current_lang == "English" else "افزودن نظرسنجی"), command=self.add_poll, fg_color="#0078AA", corner_radius=5, font=get_font(14, "bold"))
        add_button.pack(padx=10, pady=10)

    def add_poll(self):
        question = self.question_entry.get().strip()
        options_text = self.options_textbox.get("1.0", "end").strip()
        if not question or not options_text:
            messagebox.showerror("Error" if current_lang == "English" else "خطا", 
                                 "Please enter both question and options." if current_lang == "English" else "لطفاً سوال و گزینه‌ها را وارد کنید.")
            return
        options = [opt.strip() for opt in options_text.splitlines() if opt.strip()]
        if len(options) < 2:
            messagebox.showerror("Error" if current_lang == "English" else "خطا", 
                                 "Please enter at least two options." if current_lang == "English" else "لطفاً حداقل دو گزینه وارد کنید.")
            return
        poll_data = {"question": question, "options": options}
        self.master.polls_list.append(poll_data)
        messagebox.showinfo("Info" if current_lang == "English" else "اطلاع", 
                            "Poll added successfully." if current_lang == "English" else "نظرسنجی با موفقیت افزوده شد.")
        self.destroy()

# پنجره‌ی فرآیند ارسال
class SendProcessWindow(ctk.CTkToplevel):
    def __init__(self, parent, numbers_list, messages, attachments, polls, delay_seconds, delay_every_msgs, mode):
        super().__init__(parent)
        self.attributes("-fullscreen", False)
        self.transient(parent)
        self.lift()
        self.grab_set()
        self.title("Run")
        self.geometry("900x550")
        self.numbers_list = numbers_list
        self.messages = messages
        self.attachments = attachments
        self.polls = polls
        self.delay_seconds = delay_seconds
        self.delay_every_msgs = delay_every_msgs
        self.mode = mode
        self.paused = False
        self.stopped = False
        self.current_index = 0

        top_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        top_frame.pack(fill="x", pady=10, padx=10)
        initiate_label = ctk.CTkLabel(top_frame, text="Initiate WhatsApp & Scan QR Code from your mobile", font=get_font(14, "bold"), text_color="white")
        initiate_label.pack(side="left", padx=10, pady=10)
        self.status_label = ctk.CTkLabel(top_frame, text="Status: Indicated", font=get_font(14), text_color="white")
        self.status_label.pack(side="right", padx=10)
        self.initiate_button = ctk.CTkButton(top_frame, text="CLICK TO INITIATE", fg_color="#0078AA", command=self.initiate_connection, corner_radius=5)
        self.initiate_button.pack(side="left", padx=10)

        middle_frame = ctk.CTkFrame(self, fg_color="#20232a", corner_radius=10)
        middle_frame.pack(fill="x", pady=10, padx=10)
        self.start_button = ctk.CTkButton(middle_frame, text="START", fg_color="#4CAF50", command=self.start_sending, corner_radius=5, font=get_font(14, "bold"))
        self.start_button.pack(side="left", padx=5)
        self.pause_button = ctk.CTkButton(middle_frame, text="PAUSE", fg_color="#FF9800", command=self.pause_sending, corner_radius=5, font=get_font(14, "bold"))
        self.pause_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(middle_frame, text="STOP", fg_color="#F44336", command=self.stop_sending, corner_radius=5, font=get_font(14, "bold"))
        self.stop_button.pack(side="left", padx=5)
        self.progress_label = ctk.CTkLabel(middle_frame, text="0% Completed [0/{}]".format(len(self.numbers_list)), font=get_font(14), text_color="white")
        self.progress_label.pack(side="right", padx=10)

        log_frame = ctk.CTkFrame(self, fg_color="#20232a", corner_radius=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_tree = tk.ttk.Treeview(log_frame, columns=("chat_name", "status"), show="headings", style="Custom.Treeview")
        self.log_tree.heading("chat_name", text="Chat Name")
        self.log_tree.heading("status", text="Status")
        self.log_tree.column("chat_name", width=300)
        self.log_tree.column("status", width=200)
        self.log_tree.pack(fill="both", expand=True, padx=10, pady=10)

        notes_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        notes_frame.pack(fill="x", padx=10, pady=10)
        notes_label = ctk.CTkLabel(notes_frame, text=("Important Notes:\n1) Make sure your WhatsApp Web is logged in.\n2) Keep your phone connected to the internet.\n3) Do not close the browser tab during sending.\n"), font=get_font(12), justify="left", text_color="white")
        notes_label.pack(side="left", padx=10, pady=10)

    def initiate_connection(self):
        try:
            response = requests.get("https://web.whatsapp.com", timeout=5)
            if response.status_code == 200:
                self.status_label.configure(text="Status: Connected")
                webbrowser.open("https://web.whatsapp.com")
            else:
                self.status_label.configure(text="Status: Disconnected")
                messagebox.showwarning("Warning", "Connection error. Check internet or WhatsApp login.")
        except Exception as e:
            self.status_label.configure(text="Status: Disconnected")
            messagebox.showerror("Error", f"Connection error: {e}")

    def start_sending(self):
        self.paused = False
        self.stopped = False
        self.start_button.configure(state="disabled")
        send_thread = threading.Thread(target=self.send_messages)
        send_thread.start()

    def pause_sending(self):
        self.paused = True

    def stop_sending(self):
        self.stopped = True

    def send_messages(self):
        total = len(self.numbers_list)
        for idx, contact in enumerate(self.numbers_list, start=1):
            if self.stopped:
                break
            while self.paused and not self.stopped:
                time.sleep(0.5)
            phone = contact["number"]
            self.update_log(phone, "Sending...")
            try:
                if self.attachments:
                    caption_text = ""
                    if self.messages:
                        caption_text = "\n".join([
                            msg.replace("{NAME}", contact.get("name", "")).replace("{NUMBER}", contact.get("number", ""))
                            for msg in self.messages
                        ])
                    for file in self.attachments:
                        pywhatkit.sendwhats_image(phone, file, caption=caption_text, wait_time=20, tab_close=True, close_time=3)
                        time.sleep(2)
                        copy_image_to_clipboard(file)
                        time.sleep(1)
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(1)
                        pyautogui.press("enter")
                        time.sleep(5)
                elif self.messages:
                    for msg in self.messages:
                        personalized_msg = msg.replace("{NAME}", contact.get("name", "")).replace("{NUMBER}", contact.get("number", ""))
                        pywhatkit.sendwhatmsg_instantly(phone, personalized_msg, wait_time=10, tab_close=True, close_time=3)
                        time.sleep(5)
                        pyautogui.press("enter")
                if self.polls:
                    for poll in self.polls:
                        poll_text = "Poll: " + poll["question"] + "\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(poll["options"])])
                        pywhatkit.sendwhatmsg_instantly(phone, poll_text, wait_time=10, tab_close=True, close_time=3)
                        time.sleep(5)
                        pyautogui.press("enter")
                self.update_log(phone, "Success")
            except Exception as e:
                self.update_log(phone, f"Failed: {e}")
            percent = int((idx / total) * 100)
            self.progress_label.configure(text=f"{percent}% Completed [{idx}/{total}]")
            if (idx % self.delay_every_msgs == 0) and (idx < total):
                time.sleep(self.delay_seconds)
        self.start_button.configure(state="normal")
        messagebox.showinfo("Info", "Sending process finished!")

    def update_log(self, chat_name, status):
        self.log_tree.insert("", tk.END, values=(chat_name, status))
        self.log_tree.update_idletasks()

# پنجره‌ی ارسال پیام تکی
class SingleMessageWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.attributes("-fullscreen", False)
        self.transient(parent)
        self.lift()
        self.grab_set()
        if current_lang == "Persian":
            self.title("ارسال پیام تکی")
        else:
            self.title("Send Single Message")
        self.geometry("500x400")
        phone_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        phone_frame.pack(fill="x", padx=10, pady=10)
        phone_label = ctk.CTkLabel(phone_frame, text=languages[current_lang]["phone_label"], font=get_font(14, "bold"), text_color="white")
        phone_label.pack(side="left", padx=10, pady=10)
        self.phone_entry = ctk.CTkEntry(phone_frame, font=get_font(14))
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        message_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)
        message_label = ctk.CTkLabel(message_frame, text=languages[current_lang]["single_message_label"], font=get_font(14, "bold"), text_color="white")
        message_label.pack(anchor="nw", padx=10, pady=10)
        self.message_textbox = ctk.CTkTextbox(message_frame, font=get_font(14), wrap="word")
        self.message_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        send_button = ctk.CTkButton(self, text=languages[current_lang]["send_button"], command=self.send_single_message, fg_color="#0078AA", corner_radius=5, font=get_font(14, "bold"))
        send_button.pack(padx=10, pady=10)

    def send_single_message(self):
        phone = self.phone_entry.get().strip()
        message = self.message_textbox.get("1.0", "end").strip()
        if not phone or not message:
            messagebox.showerror("Error", languages[current_lang]["error_empty"])
            return
        try:
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=3)
            time.sleep(5)
            pyautogui.press("enter")
            messagebox.showinfo("Info", languages[current_lang]["success_sent"])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"{languages[current_lang]['error_sending']} {e}")

# کلاس اصلی برنامه
class WhatsAppMarketingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.state("zoomed")
        self.bind("<F11>", self.toggle_fullscreen)
        self.title(languages[current_lang]["title"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.numbers_list = []
        self.attachments_list = []
        self.polls_list = []
        self.delay_seconds = tk.IntVar(value=3)
        self.delay_every_msgs = tk.IntVar(value=5)
        self.send_mode_var = tk.StringVar(value="Manual")
        self.textboxes = []
        self.create_ui()
        self.apply_fullscreen_style()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", background="#0b0c10", foreground="white", fieldbackground="#0b0c10", font=get_ttk_font())
        style.configure("Custom.Treeview.Heading", background="#1f2833", foreground="white", font=get_ttk_heading_font())
        style.map("Custom.Treeview", background=[("selected", "#3a3f47")])

    def toggle_fullscreen(self, event=None):
        if self.state() == "zoomed":
            self.state("normal")
            self.apply_normal_style()
        else:
            self.state("zoomed")
            self.apply_fullscreen_style()

    def apply_fullscreen_style(self):
        self.configure(bg="#2c3e50")

    def apply_normal_style(self):
        self.configure(bg="#f0f0f0")

    def create_ui(self):
        top_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1f2833")
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        accounts_label = ctk.CTkLabel(top_frame, text="Accounts", font=get_font(22, "bold"), text_color="white")
        accounts_label.pack(side="left", padx=10, pady=10)
        top_right_frame = ctk.CTkFrame(top_frame, corner_radius=0, fg_color="#1f2833")
        top_right_frame.pack(side="right", padx=10, pady=10)
        appearance_option_menu = ctk.CTkOptionMenu(top_right_frame, values=["Light", "Dark"], command=self.change_appearance_mode, width=120, font=get_font(14))
        appearance_option_menu.set("Dark")
        appearance_option_menu.pack(side="left", padx=5)
        language_option_menu = ctk.CTkOptionMenu(top_right_frame, values=["English", "Persian"], command=self.change_language, width=120, font=get_font(14))
        language_option_menu.set(languages[current_lang]["language_option"])
        language_option_menu.pack(side="left", padx=5)
        main_frame = ctk.CTkFrame(self, fg_color="#20232a", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        left_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#3a3f47")
        left_frame.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        target_label = ctk.CTkLabel(left_frame, text=languages[current_lang]["target_label"], font=get_font(20, "bold"), text_color="white")
        target_label.grid(row=0, column=0, padx=10, pady=10)
        button_frame = ctk.CTkFrame(left_frame, fg_color="#3a3f47")
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="we")
        upload_button = ctk.CTkButton(button_frame, text=languages[current_lang]["upload_excel"], command=self.upload_excel, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        upload_button.pack(side="left", padx=5)
        download_sample_button = ctk.CTkButton(button_frame, text=languages[current_lang]["download_sample_excel"], command=self.download_sample_excel, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        download_sample_button.pack(side="left", padx=5)
        self.numbers_listbox = ctk.CTkFrame(left_frame, fg_color="#3a3f47")
        self.numbers_listbox.grid(row=2, column=0, padx=10, pady=5, sticky="nswe")
        self.numbers_tree = tk.ttk.Treeview(self.numbers_listbox, columns=("number", "name"), show="headings", style="Custom.Treeview", height=15)
        self.numbers_tree.heading("number", text=languages[current_lang]["number_column"])
        self.numbers_tree.heading("name", text=languages[current_lang]["name_column"])
        self.numbers_tree.column("number", width=120)
        self.numbers_tree.column("name", width=120)
        self.numbers_tree.pack(fill="both", expand=True, padx=10, pady=10)
        center_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#3a3f47")
        center_frame.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        message_label = ctk.CTkLabel(center_frame, text=languages[current_lang]["message_section"], font=get_font(20, "bold"), text_color="white")
        message_label.grid(row=0, column=0, padx=10, pady=10)
        self.message_notebook = ctk.CTkTabview(center_frame, width=400, height=300)
        self.message_notebook.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")
        self.textboxes = []
        for i in range(1, 6):
            tab_name = f"{languages[current_lang]['message_tab']} {i}"
            tab = self.message_notebook.add(tab_name)
            textbox = ctk.CTkTextbox(tab, width=380, height=200, wrap="word", font=get_font(14))
            textbox.pack(fill="both", expand=True, padx=10, pady=10)
            self.textboxes.append(textbox)

        # بخش ترجمه به عربی
        translate_frame = ctk.CTkFrame(center_frame, fg_color="#3a3f47")
        translate_frame.grid(row=3, column=0, padx=10, pady=5, sticky="we")
        self.translate_var = tk.BooleanVar(value=False)
        translate_checkbox = ctk.CTkCheckBox(
            translate_frame,
            text="arabic",
            variable=self.translate_var,
            command=self.translate_to_arabic,
            font=get_font(14),
            text_color="white"
        )
        translate_checkbox.pack(side="left", padx=5)

        translate_frameEnglish = ctk.CTkFrame(center_frame, fg_color="#3a3f47")
        translate_frameEnglish.grid(row=3, column=1, padx=10, pady=5, sticky="we")
        self.translate_var = tk.BooleanVar(value=False)
        translate_checkbox = ctk.CTkCheckBox(
            translate_frameEnglish,
            text="english",
            variable=self.translate_var,
            command=self.translate_to_english,
            font=get_font(14),
            text_color="white"
        )
        translate_checkbox.pack(side="left", padx=5)

        polls_buttons_frame = ctk.CTkFrame(center_frame, fg_color="#3a3f47")
        polls_buttons_frame.grid(row=2, column=0, padx=10, pady=5, sticky="we")
        polls_label = ctk.CTkLabel(polls_buttons_frame, text=languages[current_lang]["polls"], font=get_font(16), text_color="white")
        polls_label.pack(side="left", padx=5)
        add_poll_button = ctk.CTkButton(polls_buttons_frame, text=languages[current_lang]["add_poll"], width=100, command=self.open_poll_window, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        add_poll_button.pack(side="left", padx=5)
        buttons_label = ctk.CTkLabel(polls_buttons_frame, text=languages[current_lang]["buttons"], font=get_font(16), text_color="white")
        buttons_label.pack(side="left", padx=5)
        add_button_button = ctk.CTkButton(polls_buttons_frame, text=languages[current_lang]["add_button"], width=100, command=self.placeholder_action, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        add_button_button.pack(side="left", padx=5)
        right_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#3a3f47")
        right_frame.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)
        right_frame.grid_rowconfigure(1, weight=1)
        attachments_label = ctk.CTkLabel(right_frame, text=languages[current_lang]["attachments"], font=get_font(20, "bold"), text_color="white")
        attachments_label.grid(row=0, column=0, padx=10, pady=10)
        add_file_button = ctk.CTkButton(right_frame, text=languages[current_lang]["add_file"], command=self.add_attachment, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        add_file_button.grid(row=0, column=1, padx=5, pady=10)
        self.attachments_listbox = ctk.CTkFrame(right_frame, fg_color="#3a3f47")
        self.attachments_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nswe")
        self.attachments_tree = tk.ttk.Treeview(self.attachments_listbox, columns=("file",), show="headings", style="Custom.Treeview", height=15)
        self.attachments_tree.heading("file", text="File")
        self.attachments_tree.column("file", width=150)
        self.attachments_tree.pack(fill="both", expand=True, padx=10, pady=10)
        bottom_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1f2833")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        custom_frame = ctk.CTkFrame(bottom_frame, corner_radius=0, fg_color="#1f2833")
        custom_frame.pack(fill="x", padx=10, pady=10)
        delay_frame = ctk.CTkFrame(custom_frame, corner_radius=10, fg_color="#3a3f47")
        delay_frame.pack(side="left", padx=10, pady=5)
        delay_label = ctk.CTkLabel(delay_frame, text=languages[current_lang]["delay_settings"], font=get_font(16, "bold"), text_color="white")
        delay_label.grid(row=0, column=0, columnspan=5, padx=5, pady=5)
        ctk.CTkLabel(delay_frame, text=languages[current_lang]["wait_label"], font=get_font(14), text_color="white").grid(row=1, column=0, padx=5, pady=5)
        delay_spin = SpinboxAlternative(delay_frame, from_=1, to=9999, width=60, textvariable=self.delay_seconds)
        delay_spin.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(delay_frame, text=languages[current_lang]["seconds_after_every"], font=get_font(14), text_color="white").grid(row=1, column=2, padx=5, pady=5)
        msgs_spin = SpinboxAlternative(delay_frame, from_=1, to=9999, width=60, textvariable=self.delay_every_msgs)
        msgs_spin.grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkLabel(delay_frame, text=languages[current_lang]["messages_label"], font=get_font(14), text_color="white").grid(row=1, column=4, padx=5, pady=5)
        send_mode_frame = ctk.CTkFrame(custom_frame, corner_radius=10, fg_color="#3a3f47")
        send_mode_frame.pack(side="left", padx=10, pady=5)
        send_mode_label = ctk.CTkLabel(send_mode_frame, text=languages[current_lang]["send_mode"], font=get_font(16, "bold"), text_color="white")
        send_mode_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        manual_radio = ctk.CTkRadioButton(send_mode_frame, text=languages[current_lang]["manual"], variable=self.send_mode_var, value="Manual", font=get_font(14), text_color="white")
        manual_radio.grid(row=1, column=0, padx=5, pady=5)
        auto_radio = ctk.CTkRadioButton(send_mode_frame, text=languages[current_lang]["auto"], variable=self.send_mode_var, value="Auto", font=get_font(14), text_color="white")
        auto_radio.grid(row=1, column=1, padx=5, pady=5)
        group_send_button = ctk.CTkButton(custom_frame, text=languages[current_lang]["group_send"], command=self.open_process_window, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        group_send_button.pack(side="left", padx=10, pady=5)
        single_send_button = ctk.CTkButton(custom_frame, text=languages[current_lang]["single_send"], command=self.open_single_message_window, fg_color="#0078AA", corner_radius=5, font=get_font(14))
        single_send_button.pack(side="left", padx=10, pady=5)
        exit_button = ctk.CTkButton(custom_frame, text=languages[current_lang]["exit_button"], command=self.on_close, fg_color="#F44336", corner_radius=5, font=get_font(14))
        exit_button.pack(side="right", padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=1, minsize=200)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_columnconfigure(2, weight=1, minsize=200)
        main_frame.grid_rowconfigure(0, weight=1)

    def open_poll_window(self):
        PollWindow(self)

    def change_language(self, lang_choice):
        global current_lang
        if lang_choice in languages:
            current_lang = lang_choice
            self.update_texts()

    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode.lower())

    def update_texts(self):
        self.title(languages[current_lang]["title"])
        self.destroy()
        new_app = WhatsAppMarketingApp()
        new_app.mainloop()

    def upload_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")], title=languages[current_lang]["upload_excel"])
        if not file_path:
            return
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            self.numbers_list.clear()
            for row in sheet.iter_rows(min_row=2, values_only=True):
                number = str(row[0]).strip() if row[0] else ""
                name = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                if number:
                    self.numbers_list.append({"number": number, "name": name})
            self.refresh_numbers_tree()
        except Exception as e:
            messagebox.showerror(languages[current_lang]["title"], f"Error reading Excel: {e}")

    def refresh_numbers_tree(self):
        for item in self.numbers_tree.get_children():
            self.numbers_tree.delete(item)
        for entry in self.numbers_list:
            self.numbers_tree.insert("", tk.END, values=(entry["number"], entry["name"]))

    def download_sample_excel(self):
        sample_path = "sample_numbers.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet["A1"] = "Number"
        sheet["B1"] = "Name"
        sheet["A2"] = "+989352490619"
        sheet["B2"] = "javad agah"
        sheet["A3"] = "+989124783207"
        sheet["B3"] = "nazi zomorodi"
        sheet["A4"] = "+989358883639"
        sheet["B4"] = "mani agah"
        sheet["A5"] = "+989428883639"
        sheet["B5"] = "test"
        sheet["A6"] = "+989353033255"
        sheet["B6"] = "melisa"
        workbook.save(sample_path)
        messagebox.showinfo(languages[current_lang]["title"], f"Sample Excel saved as {sample_path}")

    def add_attachment(self):
        file_path = filedialog.askopenfilename(title=languages[current_lang]["add_file"])
        if file_path:
            self.attachments_list.append(file_path)
            self.refresh_attachments_tree()

    def refresh_attachments_tree(self):
        for item in self.attachments_tree.get_children():
            self.attachments_tree.delete(item)
        for att in self.attachments_list:
            filename = os.path.basename(att)
            self.attachments_tree.insert("", tk.END, values=(filename,))

    def open_process_window(self):
        if not self.numbers_list:
            messagebox.showerror(languages[current_lang]["title"], languages[current_lang]["error_empty"])
            return
        messages = []
        for textbox in self.textboxes:
            content = textbox.get("1.0", "end").strip()
            if content:
                messages.append(content)
        if not messages and not self.attachments_list and not self.polls_list:
            messagebox.showerror(languages[current_lang]["title"], languages[current_lang]["error_empty"])
            return
        SendProcessWindow(self, self.numbers_list, messages, self.attachments_list, self.polls_list, self.delay_seconds.get(), self.delay_every_msgs.get(), self.send_mode_var.get())

    def open_single_message_window(self):
        SingleMessageWindow(self)

    def translate_to_arabic(self):
        if self.translate_var.get():  # اگر چک‌باکس تیک خورده باشه
            translator = GoogleTranslator(source='auto', target='ar')  # ترجمه به عربی
            for textbox in self.textboxes:
                text = textbox.get("1.0", "end").strip()
                if text:
                    translated = translator.translate(text)
                    textbox.delete("1.0", "end")
                    textbox.insert("1.0", translated)

    def translate_to_english(self):
        if self.translate_var.get():  # اگر چک‌باکس تیک خورده باشه
            translator = GoogleTranslator(source='auto', target='en')  # ترجمه به عربی
            for textbox in self.textboxes:
                text = textbox.get("1.0", "end").strip()
                if text:
                    translated = translator.translate(text)
                    textbox.delete("1.0", "end")
                    textbox.insert("1.0", translated)

    def placeholder_action(self):
        messagebox.showinfo("Info", "This feature is just a placeholder. You can implement your own logic.")

    def on_close(self):
        self.destroy()

if __name__ == "__main__":
    app = WhatsAppMarketingApp()
    app.mainloop()