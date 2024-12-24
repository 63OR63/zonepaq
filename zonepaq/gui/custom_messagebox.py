import customtkinter as ctk
import tkinter as tk

from gui.template_toplevel import WindowTemplateToplevel


class CustomMessageBox(WindowTemplateToplevel):
    def __init__(self, master=None):
        self.master = master
        self.message_box = None

    def _create_message_box(self, master, title, message, buttons):
        self.message_box = ctk.CTkToplevel(master)
        self.message_box.title(title)
        self.message_box.geometry("300x150")

        label = ctk.CTkLabel(self.message_box, text=message)
        label.pack(pady=20)

        button_frame = ctk.CTkFrame(self.message_box)
        button_frame.pack(pady=10)

        for btn_text, btn_command in buttons.items():
            button = ctk.CTkButton(button_frame, text=btn_text, command=btn_command)
            button.pack(side=tk.LEFT, padx=5)

    def showinfo(self, title, message):
        def close():
            self.message_box.destroy()

        buttons = {"OK": close}
        self._create_message_box(title, message, buttons)

    def showwarning(self, title, message):
        def close():
            self.message_box.destroy()

        buttons = {"OK": close}
        self._create_message_box(title, message, buttons)

    def showerror(self, title, message):
        def close():
            self.message_box.destroy()

        buttons = {"OK": close}
        self._create_message_box(title, message, buttons)

    def askyesno(self, title, message):
        def yes():
            self.result = True
            self.message_box.destroy()

        def no():
            self.result = False
            self.message_box.destroy()

        buttons = {"Yes": yes, "No": no}
        self._create_message_box(title, message, buttons)

        self.message_box.wait_window(self.message_box)
        return getattr(self, "result", None)
