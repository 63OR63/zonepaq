import sys
from backend.logger import log
from backend.tools import Data, Files
from config.settings import settings, translate
from gui.template_toplevel import GUI_Toplevel
import customtkinter as ctk

# import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


class GUI_SettingsMenu(GUI_Toplevel):
    """Popup window for configuring and saving application settings."""

    def __init__(self, master):
        super().__init__(master, title=translate("menu_preferences_settings"))
        self.temp_storage = {}  # Temporary storage for entries values
        self._create_tabview_layout()
        self._add_general_tabview(self.general_tabview_frame)
        self._add_appearance_tabview(self.appearance_tabview_frame)
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
                settings.GAME_PATHS[settings_key] = new_value
            elif settings_key in settings.TOOLS_PATHS:
                settings.TOOLS_PATHS[settings_key] = new_value
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
            row_weights=None,
            column_weights=None,
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
                    "title": "repak",
                    "type": ".exe",
                    "buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "params": (
                                "entry_variable",
                                "entry_type",
                                "entry_widget",
                                "settings_key",
                            ),
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_repak,
                            "params": ("entry_variable",),
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
                "kdiff3": {
                    "path_dict": settings.TOOLS_PATHS,
                    "title": "kdiff3",
                    "type": ".exe",
                    "buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "params": (
                                "entry_variable",
                                "entry_type",
                                "entry_widget",
                                "settings_key",
                            ),
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_kdiff3,
                            "params": ("entry_variable",),
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
                "winmerge": {
                    "path_dict": settings.TOOLS_PATHS,
                    "title": "WinMergeU",
                    "type": ".exe",
                    "buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "params": (
                                "entry_variable",
                                "entry_type",
                                "entry_widget",
                                "settings_key",
                            ),
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._install_winmerge,
                            "params": ("entry_variable",),
                            "text": translate("settings_general_install"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
            },
            translate("settings_general_path_game"): {
                "vanilla_unpacked": {
                    "path_dict": settings.GAME_PATHS,
                    "title": translate("settings_general_vanilla_unpacked"),
                    "type": "folder",
                    "buttons": [
                        {
                            "command": self._open_path_browse_dialog,
                            "params": (
                                "entry_variable",
                                "entry_type",
                                "entry_widget",
                                "settings_key",
                            ),
                            "text": translate("settings_general_browse"),
                            "style": "Generic.CTkButton",
                        },
                        {
                            "command": self._unpack_files,
                            "params": ("entry_variable"),
                            "text": translate("settings_general_unpack"),
                            "style": "Alt.CTkButton",
                        },
                    ],
                },
            },
            translate("settings_general_keys"): {
                "aes_key": {
                    "path_dict": {"aes_key": settings.AES_KEY},
                    "title": translate("settings_general_aes_key"),
                    "type": "aes",
                    "buttons": [
                        {
                            "command": self._get_aes_key,
                            "params": ("entry_variable"),
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
            row_weights=None,
            column_weights=None,
        )

        self.engine_name = ctk.StringVar(master=self, value=settings.MERGING_ENGINE)
        self.create_ctk_widget(
            ctk_widget=ctk.CTkOptionMenu,
            widget_args={
                "master": group_frame,
                "variable": self.engine_name,
                "values": list(settings.ALL_LANG_NAMES),
                "command": lambda: (
                    settings.update_config(
                        "SETTINGS", "merging_engine", self.engine_name
                    ),
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
            row_weights=None,
            column_weights=None,
        )

        self.create_spacer(group_frame)

    def _create_entry_group(self, master, group_name, entries):

        self.create_subheader(master, text=group_name, column=0)

        self.create_spacer(master)
        for settings_key, entry_data in entries.items():
            self._create_entry_line(
                master,
                entry_data["path_dict"],
                settings_key,
                entry_data["title"],
                entry_data["type"],
                entry_data["buttons"],
            )
        self.create_spacer(master)

    def _create_entry_line(
        self, master, path_dict, settings_key, path_title, entry_type, entry_buttons
    ):
        current_row = self._get_next_row(master)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": f"{path_title}:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
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
            row_weights=None,
            column_weights=None,
        )

        self._store_temp_path_and_apply_style(
            settings_key, entry_variable.get(), entry_type, entry_widget
        )

        for index, button in enumerate(entry_buttons):
            column_index = 2 + index

            command = button["command"]
            params = button.get("params", ())

            if not isinstance(params, (list, tuple)):
                params = (params,)

            resolved_params = []
            for param in params:
                if param == "entry_variable":
                    resolved_params.append(entry_variable)
                elif param == "entry_type":
                    resolved_params.append(entry_type)
                elif param == "entry_widget":
                    resolved_params.append(entry_widget)
                elif param == "settings_key":
                    resolved_params.append(settings_key)
                else:
                    resolved_params.append(param)

            self.create_ctk_widget(
                ctk_widget=ctk.CTkButton,
                widget_args={
                    "master": master,
                    "command": lambda cmd=command, p=resolved_params: cmd(*p),
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

        group_frame = self.create_frame(
            master,
            column_weights=[(4, 1)],
        )

        self.create_subheader(
            group_frame, text=translate("settings_appearance_customization")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": group_frame,
                "text": f"{translate('settings_appearance_color_theme')} *:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
            row_weights=None,
            column_weights=None,
        )

        self.selected_theme = ctk.StringVar(master=self, value=settings.THEME_NAME)
        self.create_ctk_widget(
            ctk_widget=ctk.CTkOptionMenu,
            widget_args={
                "master": group_frame,
                "variable": self.selected_theme,
                "values": settings.ALL_THEME_NAMES,
                "command": lambda selected_theme=self.selected_theme: (
                    settings.update_config("SETTINGS", "theme_name", selected_theme),
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
            row_weights=None,
            column_weights=None,
        )

        self.dark_mode_widget = self.create_ctk_widget(
            ctk_widget=ctk.CTkSwitch,
            widget_args={
                "master": group_frame,
                "text": translate("settings_appearance_dark_mode"),
                "onvalue": True,
                "offvalue": False,
                "command": self._switch_dark_mode,
            },
            grid_args={
                "row": current_row,
                "column": 2,
                "sticky": "w",
                "padx": (0, self.padding),
                "pady": self.padding / 5,
            },
            row_weights=None,
            column_weights=None,
        )

        self.create_spacer(group_frame)
        self.create_subheader(
            group_frame, text=translate("settings_appearance_localization")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": group_frame,
                "text": f"{translate('settings_appearance_language')}:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
            row_weights=None,
            column_weights=None,
        )

        self.selected_lang = ctk.StringVar(master=self, value=settings.LANG_NAME)
        self.create_ctk_widget(
            ctk_widget=ctk.CTkOptionMenu,
            widget_args={
                "master": group_frame,
                "variable": self.selected_lang,
                "values": list(settings.ALL_LANG_NAMES),
                "command": lambda selected_lang=self.selected_lang: (
                    settings.update_config("SETTINGS", "lang_name", selected_lang),
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
            row_weights=None,
            column_weights=None,
        )

        self.create_spacer(group_frame)
        self.create_subheader(
            group_frame, text=translate("settings_appearance_onboarding")
        )
        self.create_spacer(group_frame)

        current_row = self._get_next_row(group_frame)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": group_frame,
                "text": f"{translate('settings_appearance_hints')}:",
                "anchor": "w",
                "pady": self.padding / 5,
            },
            grid_args={
                "row": current_row,
                "column": 0,
                "sticky": "w",
                "padx": self.padding,
            },
            row_weights=None,
            column_weights=None,
        )

        self.show_hints = ctk.BooleanVar(value=settings.SHOW_HINTS)
        self.show_hints_widget = self.create_ctk_widget(
            ctk_widget=ctk.CTkSwitch,
            widget_args={
                "master": group_frame,
                "text": translate("settings_appearance_show_hints"),
                "variable": self.show_hints,
                "onvalue": True,
                "offvalue": False,
                "command": self._switch_hints,
            },
            grid_args={
                "row": current_row,
                "column": 1,
                "sticky": "w",
                "padx": (0, self.padding),
                "pady": self.padding / 5,
            },
            row_weights=None,
            column_weights=None,
        )

    def _switch_dark_mode(self):
        if self.dark_mode_widget.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def _switch_hints(self):
        settings.update_config("SETTINGS", "show_hints", self.show_hints_widget.get())

    def _show_frame(self, frame):
        frame.tkraise()

    def _store_temp_path_and_apply_style(
        self, settings_key, new_value, entry_type, entry_widget
    ):
        self.temp_storage[settings_key] = new_value

        path = Path(entry_widget.get())

        if Data.is_valid_data(path, entry_type):
            style = "Alt.CTkEntry"
        else:
            style = "AltError.CTkEntry"

        self.style_manager.apply_style(entry_widget, style)

    def _get_highest_row(self, root):
        root = root or self
        return max(widget.grid_info()["row"] for widget in root.grid_slaves())

    def _open_path_browse_dialog(
        self, entry_variable, entry_type, entry_widget, settings_key
    ):
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

            self._store_temp_path_and_apply_style(
                settings_key, entry_variable.get(), entry_type, entry_widget
            )

    def prompt_redownload(self, text):
        result = messagebox.askquestion(
            translate("generic_question"), text, parent=self
        )
        if result == "yes":
            return True
        return False

    def _install_tool(
        self,
        tool_name,
        download_method,
        download_args,
        installer_path,
        output_dir,
        extract_method,
        extract_parameter,
        local_path,
        entry_variable,
        auto_mode=False,
        check_platform=True,
    ):
        if check_platform and sys.platform != "win32":
            if not auto_mode:
                messagebox.showerror(
                    translate("generic_error"),
                    translate("dialogue_only_windows"),
                    parent=self,
                )
            return False

        if download_url := download_method(**download_args):
            install_result, skipped = self.tools_manager.download_and_extract_tool(
                url=download_url,
                installer_path=installer_path,
                output_dir=output_dir,
                tool_name=tool_name,
                prompt_callback=self.prompt_redownload,
                extract_method=extract_method,
                extract_parameter=extract_parameter,
            )
            if skipped:
                return False
            if install_result:
                if not auto_mode:
                    if Files.is_existing_file(local_path):
                        entry_variable.set(str(Path(local_path).resolve()))
                        self._save_settings_and_close(close=False)
                        messagebox.showinfo(
                            translate("generic_info"),
                            f'{tool_name} {translate("dialogue_install_success")} {output_dir}',
                            parent=self,
                        )
                    else:
                        log.error(f"{tool_name} can't be located at {local_path}")
                        messagebox.showerror(
                            translate("generic_error"),
                            f'{translate("dialogue_install_error")} {tool_name}\n{translate("dialogue_check_logs")}',
                            parent=self,
                        )
                        return False
                return True

        if not auto_mode:
            messagebox.showerror(
                translate("generic_error"),
                f'{translate("dialogue_install_error")} {tool_name}\n{translate("dialogue_check_logs")}',
                parent=self,
            )
        return False

    def _install_repak(self, entry_variable):
        return self._install_tool(
            tool_name="repak_cli",
            download_method=self.tools_manager.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["repak_cli"]["github_repo"],
                "asset_regex": self.tools_manager.repak_asset_regex,
            },
            installer_path=self.tools_manager.repak_installer,
            output_dir=self.tools_manager.repak_output_dir,
            extract_method=self.tools_manager.repak_extract_method,
            extract_parameter=self.tools_manager.repak_extract_parameter,
            local_path=self.tools_manager.repak_local_path,
            entry_variable=entry_variable,
        )

    def _install_kdiff3(self, entry_variable):
        return self._install_tool(
            tool_name="KDiff3",
            download_method=self.tools_manager.get_latest_kdiff3,
            download_args={"base_url": settings.TOOLS["kdiff3"]["base_url"]},
            installer_path=self.tools_manager.kdiff3_installer,
            output_dir=self.tools_manager.kdiff3_output_dir,
            extract_method=self.tools_manager.kdiff3_extract_method,
            extract_parameter=self.tools_manager.kdiff3_extract_parameter,
            local_path=self.tools_manager.kdiff3_local_path,
            entry_variable=entry_variable,
        )

    def _install_winmerge(self, entry_variable):
        return self._install_tool(
            tool_name="WinMerge",
            download_method=self.tools_manager.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["winmerge"]["github_repo"],
                "asset_regex": self.tools_manager.winmerge_asset_regex,
            },
            installer_path=self.tools_manager.winmerge_installer,
            output_dir=self.tools_manager.winmerge_output_dir,
            extract_method=self.tools_manager.winmerge_extract_method,
            extract_parameter=self.tools_manager.winmerge_extract_parameter,
            local_path=self.tools_manager.winmerge_local_path,
            entry_variable=entry_variable,
        )

    def _unpack_files(self, entry_variable):
        print(entry_variable.get())
        pass

    def _get_aes_key(self, entry_variable):
        print(entry_variable.get())
        pass
