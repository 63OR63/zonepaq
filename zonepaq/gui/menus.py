import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox

from backend.logger import log
from config.metadata import (
    APP_AUTHOR,
    APP_DESCRIPTION,
    APP_NAME,
    APP_URL,
    APP_VERSION,
    LEGAL_NOTICE,
)
from config.settings import settings, translate
from gui.window_settings_menu import GUI_SettingsMenu


class MenuRibbon:
    """Creates the application menu bar."""

    def __init__(self, parent):
        self.root = parent
        self.show_hints = tk.BooleanVar(value=settings.SHOW_HINTS)
        self.menu_bar = self._create_menu_bar()
        self.root.config(menu=self.menu_bar)

    def _create_menu_bar(self):
        menu_bar = tk.Menu(self.root, bg="gray", fg="white", background="red")
        self._add_file_menu(menu_bar)
        self._add_preferences_menu(menu_bar)
        self._add_help_menu(menu_bar)
        return menu_bar

    def _add_file_menu(self, menu_bar):
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label=translate("menu_file_exit"), command=self.exit_app)
        menu_bar.add_cascade(label=translate("menu_file"), menu=file_menu)

    def _add_preferences_menu(self, menu_bar):
        preferences_menu = tk.Menu(menu_bar, tearoff=0)
        preferences_menu.add_command(
            label=translate("menu_preferences_settings"),
            command=self.open_settings_window,
        )
        menu_bar.add_cascade(label=translate("menu_preferences"), menu=preferences_menu)

    def _add_help_menu(self, menu_bar):
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_commands = {
            "menu_help_homepage": self.visit_homepage,
            "menu_help_license": self.show_license,
            "menu_help_about": self.show_about,
        }
        for label_key, command in help_commands.items():
            help_menu.add_command(label=translate(label_key), command=command)
        menu_bar.add_cascade(label=translate("menu_help"), menu=help_menu)

    def exit_app(self):
        settings.save()
        sys.exit(0)

    def open_settings_window(self):
        log.debug("Opening settings menu...")
        GUI_SettingsMenu(self.root)
        # self.root.withdraw()

    def show_license(self):
        messagebox.showinfo(translate("menu_help_license"), LEGAL_NOTICE)

    def visit_homepage(self):
        webbrowser.open(APP_URL)

    def show_about(self):
        about_text = (
            f"{APP_NAME} v{APP_VERSION}\n"
            f'{translate("meta_developer")} {APP_AUTHOR}\n\n'
            f"{APP_DESCRIPTION}"
        )
        messagebox.showinfo(translate("menu_help_about"), about_text)
