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
from gui.gui_settings_menu import GUI_SettingsMenu


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
        self._add_merging_engine_menu(preferences_menu)
        self._add_language_menu(preferences_menu)
        self._add_theme_menu(preferences_menu)
        menu_bar.add_cascade(label=translate("menu_preferences"), menu=preferences_menu)
        preferences_menu.add_checkbutton(
            label=translate("menu_preferences_hints"),
            variable=self.show_hints,
            # command=lambda: self.root.customization_manager.apply_show_hints(
            #     window=self.root, show_hints=self.show_hints.get()
            # ),
            command=None,  #!fixme
        )

    def _add_option_menu(
        self,
        parent_menu,
        menu_label,
        options,
        selected_option,
        apply_function,
        apply_param_name,
    ):
        submenu = tk.Menu(parent_menu, tearoff=0)
        for option_name in options:
            submenu.add_radiobutton(
                label=option_name,
                variable=selected_option,
                value=option_name,
                command=lambda opt=option_name: apply_function(
                    **{apply_param_name: opt, "window": self.root}
                ),
            )
        parent_menu.add_cascade(label=menu_label, menu=submenu)

    def _add_merging_engine_menu(self, parent_menu):
        self.selected_engine = tk.StringVar(
            master=self.root, value=settings.MERGING_ENGINE
        )
        self._add_option_menu(
            parent_menu=parent_menu,
            menu_label=translate("menu_preferences_merging_engine"),
            options=["WinMerge", "kdiff3"],
            selected_option=self.selected_engine,
            apply_function=lambda engine_name, window=None: settings.update_config(
                "SETTINGS", "merging_engine", engine_name
            ),
            apply_param_name="engine_name",
        )

    def _add_language_menu(self, parent_menu):
        self.selected_language = tk.StringVar(
            master=self.root, value=settings.LANG_NAME
        )
        self._add_option_menu(
            parent_menu=parent_menu,
            menu_label=translate("menu_preferences_language"),
            options=settings.ALL_LANG_NAMES,
            selected_option=self.selected_language,
            # apply_function=self.root.customization_manager.apply_translation,
            apply_function=None,  #!Fixme
            apply_param_name="lang_name",
        )

    def _add_theme_menu(self, parent_menu):
        self.selected_theme = tk.StringVar(master=self.root, value=settings.THEME_NAME)
        self._add_option_menu(
            parent_menu=parent_menu,
            menu_label=translate("menu_preferences_theme"),
            options=settings.ALL_THEME_NAMES,
            selected_option=self.selected_theme,
            apply_function=self.root.apply_color_theme,
            apply_param_name="theme_name",
        )

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
        self.root.open_gui(gui_class=GUI_SettingsMenu, toplevel=True)

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
