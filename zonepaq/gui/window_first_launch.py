from tkinter import messagebox
from backend.logger import log
from backend.utilities import Data
from config.defaults import DEFAULT_TOOLS_PATHS, TOOLS
from config.metadata import (
    APP_NAME,
)
from config.settings import settings, translate
from gui.template_base import WindowTemplateBase

import customtkinter as ctk


class WindowFirstLaunch(WindowTemplateBase):

    def __init__(self, master=None):
        super().__init__(title=translate("first_launch_sequence_title"))

        self.action = self.first_launch_sequence()
        settings.set("SETTINGS", "first_launch", False)
        settings.save()

        self.adjust_to_content(self)

        log.info("First launch window opened.")

    def on_closing(self):
        self.destroy()

    def first_launch_sequence(self):

        def create_labeled_text(group_frame, label_text, status, text, row, column):
            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": f"{label_text}:",
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

            if status:
                widget_style = "Success.CTkLabel"
            else:
                widget_style = "Error.CTkLabel"

            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": group_frame,
                    "text": text,
                    "anchor": "w",
                    "pady": self.padding / 5,
                },
                widget_style=widget_style,
                grid_args={
                    "row": row,
                    "column": column + 1,
                    "sticky": "w",
                    "padx": (0, self.padding),
                    "pady": self.padding / 5,
                },
            )

        report = {}

        for tool_key, tool_path in settings.TOOLS_PATHS.items():
            display_name = TOOLS.get(tool_key, {}).get("display_name", "Unknown")
            status = Data.is_valid_data(tool_path)
            text = "Installed" if status else "Not Installed"
            report[display_name] = [status, text]

        status = Data.is_valid_data(settings.AES_KEY, "aes")
        text = "Detected" if status else "Not Detected"
        report[translate("settings_general_aes_key")] = [status, text]

        for tool_key, tool_path in settings.GAME_PATHS.items():
            display_name = "Vanilla Files"
            status = Data.is_valid_data(tool_path, "folder")
            text = "Unpacked" if status else "Not Unpacked"
            report[display_name] = [status, text]

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
            create_labeled_text(report_frame, key, value[0], value[1], current_row, 0)

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
            command=None,
            padx=(self.padding, 0),
            pady=(self.padding, 0),
            sticky="e",
            row="-1",
            column=1,
        )
        self.create_button(
            question_frame,
            text=translate("generic_no"),
            command=None,
            padx=(self.padding, 0),
            pady=(self.padding, 0),
            sticky="e",
            row="-2",
            column=2,
        )
