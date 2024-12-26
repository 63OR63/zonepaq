import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
from backend.logger import log
from config.translations import translate
from gui.template_toplevel import TemplateToplevel


class WindowMessageBox(TemplateToplevel):
    def __init__(self, master, title="", message="", buttons={}):
        super().__init__(master, title=title)

        self.result = None
        self._create_message_box(message, buttons)

        self.adjust_to_content(self)

        log.info("Message Box window opened.")

    def on_closing(self):
        log.info("Message Box window closed.")
        self.destroy()

    def _create_message_box(self, message, buttons):
        box_frame = self.create_frame(
            self,
            padx=self.padding,
            pady=self.padding,
            sticky="nsew",
            column_weights=[(0, 1)],
        )

        if isinstance(message, str):
            message = [message]
        elif not isinstance(message, list):
            message = [""]

        for index, msg in enumerate(message):
            if msg:
                if index % 2 == 0:
                    self.create_ctk_widget(
                        ctk_widget=ctk.CTkLabel,
                        widget_args={
                            "master": box_frame,
                            "text": msg,
                            "wraplength": 500,
                            "justify": "left",
                        },
                        grid_args={
                            "sticky": "nw",
                        },
                    )
                else:
                    textbox = self.create_ctk_widget(
                        ctk_widget=ctk.CTkTextbox,
                        widget_args={
                            "master": box_frame,
                            "width": 500,
                            "wrap": "none",
                            # "state": "disabled",
                        },
                        grid_args={"sticky": "nsew", "pady": self.padding / 2},
                    )
                    textbox.insert(tk.END, msg)

        button_frame = self.create_frame(
            box_frame, pady=(self.padding, 0), column_weights=[(0, 1), (1, 0)]
        )

        for index, (btn_text, btn_command) in enumerate(buttons.items()):
            self.create_button(
                button_frame,
                text=btn_text,
                command=btn_command,
                width=90,
                sticky="e",
                row=0,
                column=index,
                padx=(self.padding / 2 if index > 0 else 0, 0),
            )

    @classmethod
    def showinfo(cls, master, title=translate("generic_info"), message=""):
        def close():
            dialog.on_closing()

        buttons = {translate("generic_ok"): close}
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return None

    @classmethod
    def showwarning(cls, master, title=translate("generic_warning"), message=""):
        def close():
            dialog.on_closing()

        buttons = {translate("generic_ok"): close}
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return None

    @classmethod
    def showerror(cls, master, title=translate("generic_error"), message=""):
        def close():
            dialog.on_closing()

        buttons = {translate("generic_ok"): close}
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return None

    @classmethod
    def askyesno(cls, master, title=translate("generic_question"), message=""):
        def yes():
            dialog.result = True
            dialog.on_closing()

        def no():
            dialog.result = False
            dialog.on_closing()

        buttons = {translate("generic_yes"): yes, translate("generic_no"): no}
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return dialog.result

    @classmethod
    def askyesnocancel(cls, master, title=translate("generic_question"), message=""):
        def yes():
            dialog.result = True
            dialog.on_closing()

        def no():
            dialog.result = False
            dialog.on_closing()

        def cancel():
            dialog.result = None
            dialog.on_closing()

        buttons = {
            translate("generic_yes"): yes,
            translate("generic_no"): no,
            translate("generic_cancel"): cancel,
        }
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return dialog.result

    @classmethod
    def askokcancel(cls, master, title=translate("generic_question"), message=""):
        def ok():
            dialog.result = True
            dialog.on_closing()

        def cancel():
            dialog.result = False
            dialog.on_closing()

        buttons = {
            translate("generic_ok"): ok,
            translate("generic_cancel"): cancel,
        }
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return dialog.result

    @classmethod
    def askretrycancel(cls, master, title=translate("generic_question"), message=""):
        def retry():
            dialog.result = True
            dialog.on_closing()

        def cancel():
            dialog.result = False
            dialog.on_closing()

        buttons = {
            translate("generic_retry"): retry,
            translate("generic_cancel"): cancel,
        }
        dialog = cls(master=master, title=title, message=message, buttons=buttons)
        dialog.wait_window(dialog)
        return dialog.result


class ModalFileDialog:
    @staticmethod
    def askdirectory(
        parent, initialdir=None, title=translate("filedialogue_askdirectory")
    ):
        return ModalFileDialog._show_modal_dialog(
            parent,
            lambda: filedialog.askdirectory(
                parent=parent, initialdir=initialdir, title=title
            ),
        )

    @staticmethod
    def askopenfilenames(
        parent,
        initialdir=None,
        title=translate("filedialogue_askopenfilenames"),
        filetypes=(("All Files", "*.*"),),
    ):
        return ModalFileDialog._show_modal_dialog(
            parent,
            lambda: filedialog.askopenfilenames(
                parent=parent, initialdir=initialdir, title=title, filetypes=filetypes
            ),
        )

    @staticmethod
    def _show_modal_dialog(parent, dialog_function):
        parent.grab_set()
        try:
            result = dialog_function()
        finally:
            parent.grab_release()
        return result
