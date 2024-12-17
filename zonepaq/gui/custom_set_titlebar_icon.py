import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from config.metadata import APP_ICONS
from tkinterdnd2 import TkinterDnD


def custom_set_titlebar_icon(self):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(".")
    try:
        resource_path = base_path / APP_ICONS["png"]
        self.iconphoto(True, tk.PhotoImage(file=resource_path))
    except Exception:
        pass


# !WORKAROUND for CTk overwriting changes in app icon
_CTk = ctk.CTk
if hasattr(_CTk, "_windows_set_titlebar_icon"):
    _CTk._windows_set_titlebar_icon = custom_set_titlebar_icon


class CTk(_CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
