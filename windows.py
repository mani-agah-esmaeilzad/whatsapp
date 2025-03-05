import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import webbrowser
import pywhatkit
import pyautogui
import time
import threading
import json 
import datetime
import socket
import os
import base64
from config import languages, current_lang, get_font
from utils import copy_image_to_clipboard

def send_log_to_api(phone, status, text, image_file_path=None):
    # اگر وضعیت لاگ "sending..." باشد، ارسال نشود
    if status.lower().strip() == "sending...":
        return

    url = "http://localhost:5000/api/logs"  # آدرس API دات‌نت؛ در صورت نیاز تغییر دهید.
    log_data = {
        "Timestamp": datetime.datetime.now().isoformat(),
        "Phone": phone,
        "Status": status,
        "Platform": "application",  # همیشه "application"
        "Text": text,
        "SystemIp": socket.gethostbyname(socket.gethostname()),
        "ImageBase64": ""
    }
    if image_file_path and os.path.exists(image_file_path):
        with open(image_file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            log_data["ImageBase64"] = encoded_string

    try:
        response = requests.post(url, json=log_data)
        if response.status_code == 200:
            print("Log sent successfully to API.")
        else:
            print("Error sending log to API:", response.text)
    except Exception as e:
        print("Exception sending log to API:", e)


class PollWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Add Poll" if current_lang == "English" else "افزودن نظرسنجی")
        self.geometry("400x400")
        question_label = ctk.CTkLabel(
            self, 
            text=("Poll Question:" if current_lang == "English" else "سوال نظرسنجی:"), 
            font=get_font(14, "bold")
        )
        question_label.pack(padx=10, pady=10)
        self.question_entry = ctk.CTkEntry(self, font=get_font(14))
        self.question_entry.pack(padx=10, pady=10, fill="x")
        options_label = ctk.CTkLabel(
            self, 
            text=("Poll Options (one per line):" if current_lang == "English" else "گزینه‌های نظرسنجی (هر گزینه در یک خط):"), 
            font=get_font(14, "bold")
        )
        options_label.pack(padx=10, pady=10)
        self.options_textbox = ctk.CTkTextbox(self, font=get_font(14), height=150, wrap="word")
        self.options_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        add_button = ctk.CTkButton(
            self, 
            text=("Add Poll" if current_lang == "English" else "افزودن نظرسنجی"), 
            command=self.add_poll, 
            fg_color="#0078AA", 
            corner_radius=5, 
            font=get_font(14, "bold")
        )
        add_button.pack(padx=10, pady=10)

    def add_poll(self):
        question = self.question_entry.get().strip()
        options_text = self.options_textbox.get("1.0", "end").strip()
        if not question or not options_text:
            messagebox.showerror(
                "Error" if current_lang == "English" else "خطا", 
                "Please enter both question and options." if current_lang == "English" else "لطفاً سوال و گزینه‌ها را وارد کنید."
            )
            return
        options = [opt.strip() for opt in options_text.splitlines() if opt.strip()]
        if len(options) < 2:
            messagebox.showerror(
                "Error" if current_lang == "English" else "خطا", 
                "Please enter at least two options." if current_lang == "English" else "لطفاً حداقل دو گزینه وارد کنید."
            )
            return
        poll_data = {"question": question, "options": options}
        self.master.polls_list.append(poll_data)
        messagebox.showinfo(
            "Info" if current_lang == "English" else "اطلاع", 
            "Poll added successfully." if current_lang == "English" else "نظرسنجی با موفقیت افزوده شد."
        )
        self.destroy()


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

        self.log_data = []

        top_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        top_frame.pack(fill="x", pady=10, padx=10)
        initiate_label = ctk.CTkLabel(
            top_frame, 
            text="Initiate WhatsApp & Scan QR Code from your mobile", 
            font=get_font(14, "bold"), 
            text_color="white"
        )
        initiate_label.pack(side="left", padx=10, pady=10)
        self.status_label = ctk.CTkLabel(top_frame, text="Status: Indicated", font=get_font(14), text_color="white")
        self.status_label.pack(side="right", padx=10)
        self.initiate_button = ctk.CTkButton(
            top_frame, 
            text="CLICK TO INITIATE", 
            fg_color="#0078AA", 
            command=self.initiate_connection, 
            corner_radius=5
        )
        self.initiate_button.pack(side="left", padx=10)

        middle_frame = ctk.CTkFrame(self, fg_color="#20232a", corner_radius=10)
        middle_frame.pack(fill="x", pady=10, padx=10)
        self.start_button = ctk.CTkButton(
            middle_frame, 
            text="START", 
            fg_color="#4CAF50", 
            command=self.start_sending, 
            corner_radius=5, 
            font=get_font(14, "bold")
        )
        self.start_button.pack(side="left", padx=5)
        self.pause_button = ctk.CTkButton(
            middle_frame, 
            text="PAUSE", 
            fg_color="#FF9800", 
            command=self.pause_sending, 
            corner_radius=5, 
            font=get_font(14, "bold")
        )
        self.pause_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(
            middle_frame, 
            text="STOP", 
            fg_color="#F44336", 
            command=self.stop_sending, 
            corner_radius=5, 
            font=get_font(14, "bold")
        )
        self.stop_button.pack(side="left", padx=5)
        self.progress_label = ctk.CTkLabel(
            middle_frame, 
            text="0% Completed [0/{}]".format(len(self.numbers_list)), 
            font=get_font(14), 
            text_color="white"
        )
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
        notes_label = ctk.CTkLabel(
            notes_frame, 
            text=("Important Notes:\n1) Make sure your WhatsApp Web is logged in.\n2) Keep your phone connected to the internet.\n3) Do not close the browser tab during sending.\n"), 
            font=get_font(12), 
            justify="left", 
            text_color="white"
        )
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
            # ثبت لاگ اولیه قبل از ارسال
            self.update_log(phone, "Sending...", "")
            sent_text = ""
            try:
                if self.attachments:
                    caption_text = ""
                    if self.messages:
                        caption_text = "\n".join([msg.replace("{NAME}", contact.get("name", "")).replace("{NUMBER}", contact.get("number", "")) for msg in self.messages])
                    for file in self.attachments:
                        pywhatkit.sendwhats_image(phone, file, caption=caption_text, wait_time=20, tab_close=True, close_time=3)
                        time.sleep(2)
                        copy_image_to_clipboard(file)
                        time.sleep(1)
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(1)
                        pyautogui.press("enter")
                        time.sleep(5)
                    sent_text += f"Attachment(s) sent with caption: {caption_text}\n"
                elif self.messages:
                    for msg in self.messages:
                        personalized_msg = msg.replace("{NAME}", contact.get("name", "")).replace("{NUMBER}", contact.get("number", ""))
                        pywhatkit.sendwhatmsg_instantly(phone, personalized_msg, wait_time=12, tab_close=True, close_time=3)
                        time.sleep(8)
                        pyautogui.press("enter")
                        sent_text += f"Message sent: {personalized_msg}\n"
                if self.polls:
                    for poll in self.polls:
                        poll_text = "Poll: " + poll["question"] + "\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(poll["options"])])
                        pywhatkit.sendwhatmsg_instantly(phone, poll_text, wait_time=12, tab_close=True, close_time=3)
                        time.sleep(8)
                        pyautogui.press("enter")
                        sent_text += f"Poll sent: {poll_text}\n"
                self.update_log(phone, "Success", sent_text)
            except Exception as e:
                self.update_log(phone, f"Failed: {e}", sent_text)
            percent = int((idx / total) * 100)
            self.progress_label.configure(text=f"{percent}% Completed [{idx}/{total}]")
            if (idx % self.delay_every_msgs == 0) and (idx < total):
                time.sleep(self.delay_seconds)
        self.start_button.configure(state="normal")
        messagebox.showinfo("Info", "Sending process finished!")

    def update_log(self, chat_name, status, message_text="", image_file_path=None):
        self.log_tree.insert("", tk.END, values=(chat_name, status))
        self.log_tree.update_idletasks()
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "phone": chat_name,
            "status": status,
            "text": message_text,
            "platform": "application",
            "system_ip": socket.gethostbyname(socket.gethostname())
        }
        self.log_data.append(log_entry)
        with open("logs.json", "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=4)
        # ارسال لاگ به API دات‌نت تنها در صورت عدم وجود وضعیت "sending..."
        send_log_to_api(chat_name, status, message_text, image_file_path)


class SingleMessageWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.attributes("-fullscreen", False)
        self.transient(parent)
        self.lift()
        self.grab_set()
        self.title("Send Single Message" if current_lang == "English" else "ارسال پیام تکی")
        self.geometry("500x400")
        phone_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        phone_frame.pack(fill="x", padx=10, pady=10)
        phone_label = ctk.CTkLabel(
            phone_frame, 
            text=languages[current_lang]["phone_label"], 
            font=get_font(14, "bold"), 
            text_color="white"
        )
        phone_label.pack(side="left", padx=10, pady=10)
        self.phone_entry = ctk.CTkEntry(phone_frame, font=get_font(14))
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        message_frame = ctk.CTkFrame(self, fg_color="#1f2833", corner_radius=10)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)
        message_label = ctk.CTkLabel(
            message_frame, 
            text=languages[current_lang]["single_message_label"], 
            font=get_font(14, "bold"), 
            text_color="white"
        )
        message_label.pack(anchor="nw", padx=10, pady=10)
        self.message_textbox = ctk.CTkTextbox(message_frame, font=get_font(14), wrap="word")
        self.message_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        send_button = ctk.CTkButton(
            self, 
            text=languages[current_lang]["send_button"], 
            command=self.send_single_message, 
            fg_color="#0078AA", 
            corner_radius=5, 
            font=get_font(14, "bold")
        )
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
            send_log_to_api(phone, "Success", message)
            messagebox.showinfo("Info", languages[current_lang]["success_sent"])
            self.destroy()
        except Exception as e:
            send_log_to_api(phone, f"Failed: {e}", message)
            messagebox.showerror("Error", f"{languages[current_lang]['error_sending']} {e}")
