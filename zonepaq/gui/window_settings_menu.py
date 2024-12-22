import sys
from backend.logger import log
from backend.tools import Data, Files
from config.settings import settings, translate
from gui.template_toplevel import GUI_Toplevel
import customtkinter as ctk

# import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from gui.window_help import GUI_HelpScreen


class GUI_SettingsMenu(GUI_Toplevel):
    """Popup window for configuring and saving application settings."""

    def __init__(self, master):
        super().__init__(master, title=translate("menu_preferences_settings"))
        self.temp_storage = {}  # Temporary storage for entries values
        self._create_tabview_layout()
        self._add_general_tabview(self.general_tabview_frame)
        self._add_appearance_tabview(self.appearance_tabview_frame)

        self.create_header_button(
            self,
            command=lambda: GUI_HelpScreen(self),
            image=self.help_image,
            image_hover=self.help_image_hover,
            sticky="e",
        )

        self._show_frame(self.general_tabview_frame)

        self.adjust_to_content(self, adjust_width=True)

        log.info("Settings menu opened.")

    def on_closing(self):
        self.destroy()

    def _save_settings_and_close(self, close=True):
        for settings_key, new_value in self.temp_storage.items():
            new_value = str(new_value).strip()
            if settings_key == "aes_key":
                settings.AES_KEY = new_value
            elif settings_key in settings.GAME_PATHS:
                settings.GAME_PATHS[settings_key] = Files.get_relative_path(new_value)
            elif settings_key in settings.TOOLS_PATHS:
                settings.TOOLS_PATHS[settings_key] = Files.get_relative_path(new_value)
        settings.save()
        if close:
            self.destroy()

    def _create_tabview_layout(self):
        self.create_header(
            self, text=translate("menu_preferences_settings"), row=0, column=0
        )

        sidebar_frame = self.create_frame(
            self,
            style="Secondary.CTkFrame",
            row=1,
            column=0,
            columnspan=1,
        )
        self.grid_columnconfigure(sidebar_frame.grid_info().get("column"), weight=0)

        self.general_tabview_frame = self.create_frame(
            self,
            style="Primary.CTkFrame",
            row=1,
            column=1,
            column_weights=[(0, 1)],
        )
        self.grid_columnconfigure(
            self.general_tabview_frame.grid_info().get("column"), weight=1
        )

        self.appearance_tabview_frame = self.create_frame(
            self,
            style="Primary.CTkFrame",
            row=1,
            column=1,
            column_weights=[(0, 1)],
        )
        # self.grid_columnconfigure(
        #     self.appearance_tabview_frame.grid_info().get("column"), weight=1
        # )

        save_frame = self.create_frame(
            self, column=0, style="Tertiary.CTkFrame", column_weights=[(0, 1)]
        )

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": save_frame,
                "text": translate("settings_require_restart"),
                "anchor": "e",
                "pady": self.padding / 2,
            },
            widget_style="Hints2.CTkLabel",
            grid_args={
                "row": self._get_next_row(save_frame),
                "column": 0,
                "sticky": "e",
            },
        )

        self.create_button(
            save_frame,
            text=translate("settings_save"),
            command=self._save_settings_and_close,
            style="Action.CTkButton",
            width=120,
            padx=self.padding,
            pady=self.padding / 2,
            sticky="e",
            row="-1",
            column=1,
        )

        self.general_button = self.create_button(
            sidebar_frame,
            text=translate("settings_general"),
            command=lambda: self._button_command(
                self.general_button, self.general_tabview_frame
            ),
            corner_radius=0,
            width=120,
        )

        self.appearance_button = self.create_button(
            sidebar_frame,
            text=translate("settings_appearance"),
            style="Muted.CTkButton",
            command=lambda: self._button_command(
                self.appearance_button, self.appearance_tabview_frame
            ),
            corner_radius=0,
            width=120,
        )

    def _button_command(self, button_widget, frame):
        self.style_manager.apply_style(button_widget, "Generic.CTkButton")
        buttons = [self.general_button, self.appearance_button]
        for btn in buttons:
            if btn != button_widget:
                self.style_manager.apply_style(btn, "Muted.CTkButton")
        self._show_frame(frame)

    def _add_general_tabview(self, master):
        general_group = {
            translate("settings_general_path_tools"): {
                "repak_cli": {
                    "path_dict": settings.TOOLS_PATHS,
                    "entry_title": f'{settings.TOOLS["repak_cli"]["display_name"]}',
                    "entry_type": settings.TOOLS["repak_cli"]["exe_name"],
                    "entry_buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_repak,
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
                "kdiff3": {
                    "path_dict": settings.TOOLS_PATHS,
                    "entry_title": f'{settings.TOOLS["kdiff3"]["display_name"]}',
                    "entry_type": settings.TOOLS["kdiff3"]["exe_name"],
                    "entry_buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_kdiff3,
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
                "winmerge": {
                    "path_dict": settings.TOOLS_PATHS,
                    "entry_title": f'{settings.TOOLS["winmerge"]["display_name"]}',
                    "entry_type": settings.TOOLS["winmerge"]["exe_name"],
                    "entry_buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_winmerge,
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
            },
            translate("settings_general_path_game"): {
                self.games_manager.game_name: {
                    "path_dict": settings.GAME_PATHS,
                    "entry_title": self.games_manager.game_name,
                    "entry_type": "folder",
                    "entry_buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._unpack_files,
                            "text": translate("settings_general_unpack"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
            },
            translate("settings_general_keys"): {
                "aes_key": {
                    "path_dict": {"aes_key": settings.AES_KEY},
                    "entry_title": translate("settings_general_aes_key"),
                    "entry_type": "aes",
                    "entry_buttons": [
                        {
                            "command": self._get_aes_key,
                            "text": translate("settings_general_get"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
            },
        }

        group_frame = self.create_frame(
            master,
            column_weights=[(0, 0), (1, 1), (2, 0)],
        )
        for group_name, entries in general_group.items():
            self._create_entry_group(group_frame, group_name, entries)

        self.create_subheader(
            group_frame, text=translate("settings_general_merging_engine")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": group_frame,
                "text": f"{translate('settings_general_used_tool')}:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
        )

        self.engine_name = ctk.StringVar(master=self, value=settings.MERGING_ENGINE)
        self.create_ctk_widget(
            ctk_widget=ctk.CTkOptionMenu,
            widget_args={
                "master": group_frame,
                "variable": self.engine_name,
                "values": list(settings.SUPPORTED_MERGING_ENGINES),
                "command": lambda engine_name=self.engine_name: (
                    settings.update_config("SETTINGS", "merging_engine", engine_name),
                ),
                "anchor": "w",
            },
            grid_args={
                "row": current_row,
                "column": 1,
                "sticky": "w",
                "padx": (0, self.padding),
                "pady": self.padding / 5,
            },
        )

        self.create_spacer(group_frame)

    def _create_entry_group(self, master, group_name, entries):

        self.create_subheader(master, text=group_name, column=0)

        self.create_spacer(master)
        for settings_key, entry_data in entries.items():
            self._create_entry_line(
                master,
                path_dict=entry_data["path_dict"],
                settings_key=settings_key,
                entry_title=entry_data["entry_title"],
                entry_type=entry_data["entry_type"],
                entry_buttons=entry_data["entry_buttons"],
            )
        self.create_spacer(master)

    def _create_entry_line(
        self, master, path_dict, settings_key, entry_title, entry_type, entry_buttons
    ):
        current_row = self._get_next_row(master)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": f"{entry_title}:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
        )

        entry_variable = ctk.StringVar(
            master=self, value=path_dict.get(settings_key, "")
        )

        entry_widget = self.create_ctk_widget(
            ctk_widget=ctk.CTkEntry,
            widget_args={
                "master": master,
                "textvariable": entry_variable,
                "placeholder_text": "CTkEntry",
                "width": 300,
            },
            widget_style="Alt.CTkEntry",
            grid_args={
                "row": current_row,
                "column": 1,
                "sticky": "ew",
                "padx": (0, self.padding),
                "pady": self.padding / 5,
            },
        )

        self._store_temp_path_and_apply_style(
            settings_key, entry_variable.get(), entry_type, entry_widget
        )

        for index, button in enumerate(entry_buttons):
            column_index = 2 + index

            command = button["command"]

            params = {
                "settings_key": settings_key,
                # "entry_title": entry_title,
                "entry_type": entry_type,
                "entry_variable": entry_variable,
                "entry_widget": entry_widget,
            }

            self.create_ctk_widget(
                ctk_widget=ctk.CTkButton,
                widget_args={
                    "master": master,
                    "command": lambda cmd=command, p=params: cmd(install_metadata=p),
                    "text": button["text"],
                    "width": 0,
                },
                widget_style=button["style"],
                grid_args={
                    "row": current_row,
                    "column": column_index,
                    "sticky": "ew",
                    "padx": (0, self.padding),
                    "pady": self.padding / 5,
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

    def _add_appearance_tabview(self, master):

        def create_labeled_option_menu(
            group_frame, label_text, variable, values, command, row, column
        ):
            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": label_text,
                    "anchor": "w",
                    "pady": self.padding / 5,
                },
                grid_args={
                    "row": row,
                    "column": column,
                    "sticky": "w",
                    "padx": self.padding,
                },
            )

            return self.create_ctk_widget(
                ctk_widget=ctk.CTkOptionMenu,
                widget_args={
                    "master": group_frame,
                    "variable": variable,
                    "values": values,
                    "command": command,
                    "anchor": "w",
                },
                grid_args={
                    "row": row,
                    "column": column + 1,
                    "sticky": "w",
                    "padx": (0, self.padding),
                    "pady": self.padding / 5,
                },
            )

        def create_labeled_switch(
            group_frame, label_label, switch_text, variable, command, row, column
        ):
            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": label_label,
                    "anchor": "w",
                    "pady": self.padding / 5,
                },
                grid_args={
                    "row": row,
                    "column": column,
                    "sticky": "w",
                    "padx": self.padding,
                },
            )

            return self.create_ctk_widget(
                ctk_widget=ctk.CTkSwitch,
                widget_args={
                    "master": group_frame,
                    "text": switch_text,
                    "variable": variable,
                    "onvalue": True,
                    "offvalue": False,
                    "command": command,
                },
                grid_args={
                    "row": row,
                    "column": column + 1,
                    "sticky": "w",
                    "padx": (0, self.padding),
                    "pady": self.padding / 5,
                },
            )

        group_frame = self.create_frame(
            master,
            column_weights=[(4, 1)],
        )

        # Section: Customization
        self.create_subheader(
            group_frame, text=translate("settings_appearance_customization")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)
        self.selected_theme = ctk.StringVar(master=self, value=settings.THEME_NAME)
        create_labeled_option_menu(
            group_frame,
            label_text=f"{translate('settings_appearance_color_theme')} *:",
            variable=self.selected_theme,
            values=settings.ALL_THEME_NAMES,
            command=lambda selected_theme: settings.update_config(
                "SETTINGS", "theme_name", selected_theme
            ),
            row=current_row,
            column=0,
        )

        self.dark_mode = ctk.BooleanVar(value=settings.DARK_MODE)
        self.dark_mode_widget = create_labeled_switch(
            group_frame,
            label_label="",
            switch_text=translate("settings_appearance_dark_mode"),
            variable=self.dark_mode,
            command=self._switch_dark_mode,
            row=current_row,
            column=2,
        )

        # Section: Localization
        self.create_spacer(group_frame)
        self.create_subheader(
            group_frame, text=translate("settings_appearance_localization")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)
        self.selected_lang = ctk.StringVar(master=self, value=settings.LANG_NAME)
        create_labeled_option_menu(
            group_frame,
            label_text=f"{translate('settings_appearance_language')}:",
            variable=self.selected_lang,
            values=list(settings.ALL_LANG_NAMES),
            command=lambda selected_lang: settings.update_config(
                "SETTINGS", "lang_name", selected_lang
            ),
            row=current_row,
            column=0,
        )

        # Section: Onboarding
        self.create_spacer(group_frame)
        self.create_subheader(
            group_frame, text=translate("settings_appearance_onboarding")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)
        self.show_hints = ctk.BooleanVar(value=settings.SHOW_HINTS)
        self.show_hints_widget = create_labeled_switch(
            group_frame,
            label_label=f"{translate('settings_appearance_hints')}:",
            switch_text=translate("settings_appearance_show_hints"),
            variable=self.show_hints,
            command=self._switch_hints,
            row=current_row,
            column=0,
        )

    def _switch_dark_mode(self):
        if self.dark_mode_widget.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        settings.update_config("SETTINGS", "dark_mode", self.dark_mode_widget.get())

    def _switch_hints(self):
        settings.update_config("SETTINGS", "show_hints", self.show_hints_widget.get())

    def _show_frame(self, frame):
        frame.tkraise()

    def _store_temp_path_and_apply_style(
        self, settings_key, new_value, entry_type, entry_widget
    ):
        self.temp_storage[settings_key] = new_value

        path = Path(entry_widget.get())

        self._apply_style(Data.is_valid_data(path, entry_type), entry_widget)

    def _apply_style(self, is_valid, entry_widget):
        if is_valid:
            style = "Alt.CTkEntry"
        else:
            style = "AltError.CTkEntry"

        self.style_manager.apply_style(entry_widget, style)

    def _open_path_browse_dialog(self, install_metadata):
        path = Path(install_metadata["entry_variable"].get())
        if path.is_file():
            initial_dir = path.parent
        elif path.is_dir():
            initial_dir = path
        else:
            initial_dir = Path.cwd()

        if install_metadata["entry_type"] == "folder":
            selected_path = filedialog.askdirectory(parent=self, initialdir=initial_dir)
        else:
            filetypes = [(f'{install_metadata["entry_type"]}', "*")]
            if sys.platform == "win32":
                filetypes[0] = (filetypes[0][0], filetypes[0][1] + ".exe")

            selected_path = filedialog.askopenfilenames(
                parent=self,
                initialdir=initial_dir,
                filetypes=filetypes,
            )

        if selected_path:
            if isinstance(selected_path, tuple):
                selected_path = ";".join(selected_path)
            install_metadata["entry_variable"].set(
                Files.get_relative_path(selected_path)
            )

            self._store_temp_path_and_apply_style(
                install_metadata["settings_key"],
                install_metadata["entry_variable"].get(),
                install_metadata["entry_type"],
                install_metadata["entry_widget"],
            )

    def prompt_redownload(self, text, auto_mode):
        if auto_mode:
            return True
        result = messagebox.askquestion(
            translate("generic_question"), text, parent=self
        )
        if result == "yes":
            return True
        return False

    def _install_repak(self, install_metadata={}, auto_mode=False):
        install_metadata.update(settings.TOOLS["repak_cli"])
        return self.tools_manager._install_tool(
            self,
            download_method=self.tools_manager.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["repak_cli"]["github_repo"],
                "asset_regex": settings.TOOLS["repak_cli"]["asset_regex"],
            },
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    def _install_kdiff3(self, install_metadata={}, auto_mode=False):
        install_metadata.update(settings.TOOLS["kdiff3"])
        return self.tools_manager._install_tool(
            self,
            download_method=self.tools_manager.get_latest_kdiff3,
            download_args={"base_url": settings.TOOLS["kdiff3"]["base_url"]},
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    def _install_winmerge(self, install_metadata={}, auto_mode=False):
        install_metadata.update(settings.TOOLS["winmerge"])
        return self.tools_manager._install_tool(
            self,
            download_method=self.tools_manager.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["winmerge"]["github_repo"],
                "asset_regex": settings.TOOLS["winmerge"]["asset_regex"],
            },
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    def _unpack_files(self, install_metadata):
        print("raise NotImplementedError")

    def _get_aes_key(self, install_metadata):
        if not Files.is_existing_file(settings.TOOLS_PATHS["aes_dumpster"]):
            self._install_aes_dumpster()

    def _install_aes_dumpster(self, install_metadata={}, auto_mode=False):
        install_metadata.update(settings.TOOLS["aes_dumpster"])
        return self.tools_manager._install_tool(
            self,
            download_method=self.tools_manager.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["aes_dumpster"]["github_repo"],
                "asset_regex": settings.TOOLS["aes_dumpster"]["asset_regex"],
            },
            install_metadata=install_metadata,
            skip_extract=True,
            auto_mode=True,
        )
