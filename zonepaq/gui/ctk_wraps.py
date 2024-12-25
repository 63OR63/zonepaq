import tkinter as tk

import customtkinter as ctk
from backend.utilities import Files
from config.metadata import APP_ICONS
from tkinterdnd2 import TkinterDnD


def custom_set_titlebar_icon(self):
    base_path = Files.get_base_path()
    try:
        resource_path = base_path / APP_ICONS["png"]
        self.iconphoto(True, tk.PhotoImage(file=resource_path))
    except Exception:
        pass


_CTk = ctk.CTk
# !WORKAROUND for CTk overwriting changes in app icon
if hasattr(_CTk, "_windows_set_titlebar_icon"):
    _CTk._windows_set_titlebar_icon = custom_set_titlebar_icon
# !WORKAROUND for CTk applying dpi scaling to winfo_reqwidth() and winfo_reqheight()
# if hasattr(_CTk, "minsize"):
#     _CTk.minsize = tk.Tk.minsize
# !WORKAROUND for CTk resizable() causing flickering
if hasattr(_CTk, "resizable"):
    _CTk.resizable = tk.Tk.resizable


class CTk(_CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


_CTkToplevel = ctk.CTkToplevel
# !WORKAROUND for CTk overwriting changes in app icon
if hasattr(_CTkToplevel, "_windows_set_titlebar_icon"):
    _CTkToplevel._windows_set_titlebar_icon = custom_set_titlebar_icon
# !WORKAROUND for CTk applying dpi scaling to winfo_reqwidth() and winfo_reqheight()
# if hasattr(_CTkToplevel, "minsize"):
#     _CTkToplevel.minsize = tk.Tk.minsize
# !WORKAROUND for CTk resizable() causing flickering
if hasattr(_CTkToplevel, "resizable"):
    _CTkToplevel.resizable = tk.Tk.resizable


class CTkToplevel(_CTkToplevel, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
