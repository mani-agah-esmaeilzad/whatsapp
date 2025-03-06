import tkinter.ttk as ttk
from config import get_ttk_font, get_ttk_heading_font

def apply_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview", background="#0b0c10", foreground="white", fieldbackground="#0b0c10", font=get_ttk_font())
    style.configure("Custom.Treeview.Heading", background="#1f2833", foreground="white", font=get_ttk_heading_font())
    style.map("Custom.Treeview", background=[("selected", "#3a3f47")])
