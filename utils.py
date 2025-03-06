import customtkinter as ctk
from PIL import Image
from io import BytesIO
import tkinter as tk
import win32clipboard
from deep_translator import GoogleTranslator

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
        print(f"Error copying image to clipboard: {e}")

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

def translate_to_arabic(textboxes, translate_var):
    if translate_var.get():
        translator = GoogleTranslator(source='auto', target='ar')
        for textbox in textboxes:
            text = textbox.get("1.0", "end").strip()
            if text:
                translated = translator.translate(text)
                textbox.delete("1.0", "end")
                textbox.insert("1.0", translated)

def translate_to_english(textboxes, translate_var):
    if translate_var.get():
        translator = GoogleTranslator(source='auto', target='en')
        for textbox in textboxes:
            text = textbox.get("1.0", "end").strip()
            if text:
                translated = translator.translate(text)
                textbox.delete("1.0", "end")
                textbox.insert("1.0", translated)
