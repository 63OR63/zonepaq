import webbrowser
from backend.logger import log
from config.metadata import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_URL,
    APP_VERSION,
    LEGAL_NOTICE,
)
from config.settings import translate
from gui.template_toplevel import GUI_Toplevel
import customtkinter as ctk


class GUI_HelpScreen(GUI_Toplevel):
    """Popup window for configuring and saving application settings."""

    def __init__(self, master):
        super().__init__(master, title=translate("menu_help_about"))

        self._create()

        self.adjust_to_content(self)

        log.info("Info menu opened.")

    def on_closing(self):
        self.destroy()

    def _create(self):

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": self,
                "text": (f"{APP_NAME} v{APP_VERSION}\n\n{APP_DESCRIPTION}"),
                "justify": "left",
                "wraplength": 400,
            },
            grid_args={
                "padx": self.padding,
                "pady": self.padding,
            },
        )

        self.create_separator(self, padx=self.padding)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": self,
                "text": LEGAL_NOTICE,
                "justify": "left",
                "wraplength": 400,
            },
            grid_args={
                "padx": self.padding,
                "pady": (0, self.padding),
            },
        )
        self.create_button(
            self,
            text=translate("menu_help_homepage"),
            command=lambda: webbrowser.open(APP_URL),
            padx=self.padding,
            pady=(0, self.padding),
            sticky="e",
        )
