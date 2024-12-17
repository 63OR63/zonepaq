from backend.logger import log
from config.settings import settings, translate
from gui.GUI_Base import GUI_Base

import customtkinter as ctk

# import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk


# class GUI_SettingsMenu(GUI_Toplevel):
class GUI_SettingsMenu(GUI_Base):
    """Popup window for configuring and saving application settings."""

    def __init__(self):
        super().__init__(title=translate("menu_preferences_settings"))
        self.padding = self.padding
        self.temp_storage = {}  # Temporary storage for entries values
        self._add_settings_groups()
        # self._add_save_button()
        self.adjust_to_content(root=self, adjust_width=True)
        log.info("Settings menu opened.")

    def _add_settings_groups(self):

        # header_label = ttk.Label(
        #     self,
        #     text=translate("menu_preferences_settings"),
        #     style="Header.TLabel",
        # )
        # header_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.create_header(self, text=translate("menu_preferences_settings"))

        # self.grid_rowconfigure(0, weight=1)

        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=0)

        path_groups = {
            translate("menu_preferences_settings_path_tools"): {
                "repak_cli": {
                    "path_dict": settings.TOOLS_PATHS,
                    "title": "repak",
                    "type": ".exe",
                },
                "winmerge": {
                    "path_dict": settings.TOOLS_PATHS,
                    "title": "WinMerge",
                    "type": ".exe",
                },
                "kdiff3": {
                    "path_dict": settings.TOOLS_PATHS,
                    "title": "kdiff3",
                    "type": ".exe",
                },
            },
            translate("menu_preferences_settings_path_game"): {
                "vanilla_unpacked": {
                    "path_dict": settings.GAME_PATHS,
                    "title": translate("menu_preferences_settings_vanilla_unpacked"),
                    "type": "folder",
                },
            },
            "AES Key": {
                "aes_key": {
                    "path_dict": {"aes_key": settings.AES_KEY},
                    "title": translate("menu_preferences_settings_aes_key"),
                    "type": "aes",
                },
            },
        }

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # settings_frame = self.create_frame(
        #     self,
        #     padx=self.padding,
        #     pady=(self.padding, 0),
        #     column_weights=[(0, 0), (1, 1)],
        # )

        sidebar_frame = self.create_frame(
            self,
            style="Primary.CTkFrame",
            columnspan=1,
        )

        general_tabview_frame = self.create_frame(
            self,
            style="Secondary.CTkFrame",
            row="current",
            column="+1",
        )

        save_frame = self.create_frame(
            self, column=0, style="Tertiary.CTkFrame", column_weights=[(0, 1)]
        )

        save_button = self.create_button(
            save_frame,
            text="Save",
            style="Action.CTkButton",
            padx=self.padding / 2,
            pady=self.padding / 2,
            sticky="e",
        )

        general_button = self.create_button(
            sidebar_frame, text="General", corner_radius=0
        )

        appearance_button = self.create_button(
            sidebar_frame,
            text="Appearance",
            style="Muted.CTkButton",
            corner_radius=0,
        )

        row_index = 1
        for group_name, paths in path_groups.items():
            row_index = self._add_path_group(
                general_tabview_frame, group_name, paths, row_index
            )

    def _add_path_group(self, master, group_name, paths, starting_row):
        self._create_group_label(master, group_name, starting_row)
        for index, (settings_key, path_data) in enumerate(
            paths.items(), start=starting_row + 1
        ):
            self._create_path_input(
                master,
                path_data["path_dict"],
                settings_key,
                path_data["title"],
                path_data["type"],
                index,
            )
        return starting_row + len(paths) + 1

    def _create_group_label(self, master, group_label, row):

        self.create_subheader(master, text=group_label, row=row, column=0)

    def _create_path_input(
        self, master, path_dict, settings_key, path_title, entry_type, row
    ):

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": f"{path_title}:",
                "anchor": "w",
                "pady": self.padding / 2,
            },
            grid_args={
                "row": row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
            row_weights=None,
            column_weights=None,
        )

        entry_variable = ctk.StringVar(
            master=self, value=path_dict.get(settings_key, "")
        )
        print(path_dict.get(settings_key, ""))

        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=0)

        entry_widget = self.create_ctk_widget(
            ctk_widget=ctk.CTkEntry,
            widget_args={
                "master": master,
                "textvariable": entry_variable,
                "placeholder_text": "CTkEntry",
                "width": 400,
            },
            widget_style="Alt.CTkEntry",
            grid_args={
                "row": row,
                "column": 1,
                "sticky": "ew",
                "padx": (0, self.padding),
                "pady": self.padding / 2,
            },
            row_weights=None,
            column_weights=None,
        )

        self._store_temp_path_and_apply_style(
            settings_key, entry_variable.get(), entry_type, entry_widget
        )

        if entry_type != "aes":
            browse_button = self.create_ctk_widget(
                ctk_widget=ctk.CTkButton,
                widget_args={
                    "master": master,
                    "command": lambda: self._open_path_browse_dialog(
                        entry_variable, entry_type
                    ),
                    "text": translate("menu_preferences_settings_browse"),
                    "width": 0,
                },
                widget_style="Generic.CTkButton",
                grid_args={
                    "row": row,
                    "column": 2,
                    "sticky": "e",
                    "padx": (0, self.padding),
                    "pady": self.padding / 2,
                },
                row_weights=None,
                column_weights=None,
            )

        entry_variable.trace_add(
            "write",
            lambda *args: self._store_temp_path_and_apply_style(
                settings_key, entry_variable.get(), entry_type, entry_widget
            ),
        )

    def _store_temp_path_and_apply_style(
        self, settings_key, new_value, entry_type, entry_widget
    ):
        self.temp_storage[settings_key] = new_value
        # entry_widget.apply_style(forced_style=entry_widget.get_style(entry_type))

    def _add_save_button(self):

        save_button = self.create_ctk_widget(
            ctk_widget=ctk.CTkButton,
            widget_args={
                "master": self,
                "command": self._save_settings_and_close,
                "text": translate("menu_preferences_settings_save"),
                "width": 170,
                "height": 40,
            },
            widget_style="Generic.CTkButton",
            grid_args={
                "row": self._get_highest_row() + 1,
                "column": 0,
                "sticky": "ns",
                "padx": 0,
                "pady": self.padding,
                "columnspan": 3,
            },
            row_weights=None,
            column_weights=None,
        )

    def _get_highest_row(self):
        return max(widget.grid_info()["row"] for widget in self.grid_slaves())

    def _save_settings_and_close(self):
        for settings_key, new_value in self.temp_storage.items():
            new_value = str(new_value).strip()
            if settings_key == "aes_key":
                settings.AES_KEY = new_value
            elif settings_key in settings.GAME_PATHS:
                settings.GAME_PATHS[settings_key] = new_value
            elif settings_key in settings.TOOLS_PATHS:
                settings.TOOLS_PATHS[settings_key] = new_value
        settings.save()
        self.destroy()

    def _open_path_browse_dialog(self, entry_variable, entry_type):
        path = Path(entry_variable.get())
        if path.is_file():
            initial_dir = path.parent
        elif path.is_dir():
            initial_dir = path
        else:
            initial_dir = Path.cwd()

        if entry_type == "folder":
            selected_path = filedialog.askdirectory(parent=self, initialdir=initial_dir)
        else:
            selected_path = filedialog.askopenfilenames(
                parent=self,
                initialdir=initial_dir,
                filetypes=[(f"*{entry_type}", f"*{entry_type}")],
            )

        if selected_path:
            if isinstance(selected_path, tuple):
                selected_path = ";".join(selected_path)
            entry_variable.set(selected_path)
