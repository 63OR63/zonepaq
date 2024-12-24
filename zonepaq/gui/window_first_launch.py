from tkinter import messagebox

import customtkinter as ctk
from backend.logger import log
from backend.utilities import Data, Files
from config.defaults import TOOLS
from config.metadata import APP_NAME
from config.settings import SettingsManager
from config.themes import StyleManager
from config.translations import translate
from gui.template_base import WindowTemplateBase

# Get SettingsManager class
settings = SettingsManager()


class WindowFirstLaunch(WindowTemplateBase):

    def __init__(self, master=None):
        super().__init__(title=translate("first_launch_sequence_title"))

        self.style_manager = StyleManager

        self.create()
        # settings.set("SETTINGS", "first_launch", False)
        settings.save()

        self.adjust_to_content(self)

        log.info("First launch window opened.")

    def on_closing(self):
        log.debug("First launch window closed.")
        self.destroy()

    def create(self):

        def create_labeled_text(
            group_frame, label_text, tool_key, status, text, row, column
        ):
            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": f"{label_text}:",
                    "anchor": "w",
                },
                grid_args={
                    "row": row,
                    "column": column,
                    "sticky": "w",
                    "padx": self.padding,
                },
            )

            status_label = self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": text,
                    "anchor": "w",
                },
                grid_args={
                    "row": row,
                    "column": column + 1,
                    "sticky": "w",
                    "padx": (0, self.padding),
                },
            )
            setattr(self, f"{tool_key}_status_label", status_label)

            self._apply_style(status, status_label)

            progress_bar_grid_args = {
                "row": row,
                "column": column + 2,
                "sticky": "w",
                "padx": (0, self.padding),
            }
            progress_bar = self.create_ctk_widget(
                ctk_widget=ctk.CTkProgressBar,
                widget_args={
                    "master": group_frame,
                },
                # widget_style=widget_style,
                grid_args=progress_bar_grid_args,
            )
            setattr(self, f"{tool_key}_progress_bar", progress_bar)
            setattr(self, f"{tool_key}_progress_bar_grid_args", progress_bar)

            progress_bar.grid_forget()

        report = {}

        # Add tools to the report
        for tool_key, tool_path in settings.TOOLS_PATHS.items():
            display_name = TOOLS.get(tool_key, {}).get("display_name", "Unknown")
            status = Data.is_valid_data(tool_path)
            text = "Installed" if status else "Not Installed"
            report[display_name] = {
                "tool_key": tool_key,
                "status": status,
                "text": text,
            }

        # Add AES key to the report
        status = Data.is_valid_data(settings.AES_KEY, "aes")
        text = "Detected" if status else "Not Detected"
        report[translate("settings_general_aes_key")] = {
            "tool_key": tool_key,
            "status": status,
            "text": text,
        }

        from backend.games_manager import GamesManager

        games_manager = GamesManager()

        # Add vanilla files to the report
        for index, value in enumerate(games_manager.vanilla_files):
            unpacked = value["unpacked"]
            display_name = f"{games_manager.game_display_name} Vanilla Files"
            status = not Files.is_folder_empty(unpacked)
            text = "Unpacked" if status else "Not Unpacked"
            report[display_name] = {
                "tool_key": f"vanilla_{index}",
                "status": status,
                "text": text,
            }

        # Intro Frame
        intro_frame = self.create_frame(
            self, column=0, padx=self.padding, pady=self.padding
        )
        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": intro_frame,
                "text": f'{translate("first_launch_sequence_welcome_1")} {APP_NAME} {translate("first_launch_sequence_welcome_2")}',
                "justify": "left",
            },
            grid_args={
                "column": 0,
                "sticky": "w",
            },
        )

        # Report Frame
        report_frame = self.create_frame(
            self, column=0, padx=self.padding, pady=(0, self.padding)
        )

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": report_frame,
                "text": translate("first_launch_sequence_welcome_3"),
                "justify": "left",
            },
            widget_style="SubHeader2.CTkLabel",
            grid_args={
                "column": 0,
                "sticky": "w",
            },
        )

        for key, value in report.items():
            current_row = self._get_next_row(report_frame)
            create_labeled_text(
                report_frame,
                label_text=key,
                tool_key=value["tool_key"],
                status=value["status"],
                text=value["text"],
                row=current_row,
                column=0,
            )

        self.create_separator(self, padx=self.padding)

        # Question Frame
        question_frame = self.create_frame(
            self, column=0, padx=self.padding, pady=(0, self.padding)
        )

        self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": question_frame,
                "text": f'{translate("first_launch_sequence_question")}',
                "justify": "left",
            },
            widget_style="SubHeader2.CTkLabel",
            grid_args={
                "column": 0,
                "sticky": "w",
                "padx": (0, self.padding),
                "pady": (self.padding, 0),
            },
        )

        self.create_button(
            question_frame,
            text=translate("generic_yes"),
            command=self.perform_setup_sequence,
            padx=(self.padding, 0),
            pady=(self.padding, 0),
            sticky="e",
            row="-1",
            column=1,
        )
        self.create_button(
            question_frame,
            text=translate("generic_no"),
            command=self.skip_setup_sequence,
            padx=(self.padding, 0),
            pady=(self.padding, 0),
            sticky="e",
            row="-2",
            column=2,
        )

    def installation_progress_callback(self, tool_key):
        progress_bar_widget = getattr(self, f"{tool_key}_progress_bar")
        progress_bar_widget.grid_forget()

    def perform_setup_sequence(self):
        log.info("Initiating first launch initial setup sequence...")

        from backend.tools_manager import ToolsManager

        tools_manager = ToolsManager()

        # Iterate through and call tools install methods in auto mode
        for tool_key in settings.TOOLS_PATHS.keys():
            install_method = getattr(tools_manager, f"install_{tool_key}")
            install_result = install_method(parent=self, auto_mode=True)
            if install_result:
                local_exe = TOOLS[tool_key]["local_exe"]
                if local_exe.exists():
                    # Apply success style to the status label
                    self._apply_style(True, getattr(self, f"{tool_key}_status_label"))

        tools_manager.get_aes_key(
            parent=self, auto_mode=True, skip_aes_dumpster_download=True
        )

        tools_manager.unpack_files(
            parent=self, auto_mode=True, skip_aes_extraction=True
        )

        self.on_closing()

    def skip_setup_sequence(self):
        log.debug("Skipping first launch initial setup sequence...")

        messagebox.showinfo(
            translate("generic_info"),
            f"Skip",
            parent=self,
        )

        self.on_closing()

    def _apply_style(self, is_valid, entry_widget):
        if is_valid:
            style = "Success.CTkLabel"
        else:
            style = "Error.CTkLabel"

        self.style_manager.apply_style(entry_widget, style)
