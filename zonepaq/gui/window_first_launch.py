import logging
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from backend.logger import log
from backend.parallel_orchestrator import ThreadExecutor, ThreadManager
from backend.utilities import Data, Files
from config.defaults import TOOLS
from config.metadata import APP_NAME
from config.settings_manager import settings
from config.themes import StyleManager
from config.translations import translate
from gui.template_base import TemplateBase
from gui.window_messagebox import WindowMessageBox


class TextBoxHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            if self.text_widget.winfo_exists():  # Check if the widget still exists
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
        except Exception:
            self.handleError(record)

    def close(self):
        # Perform cleanup when the handler is removed
        self.text_widget = None
        super().close()


class WindowFirstLaunch(TemplateBase):

    def __init__(self, master=None):
        super().__init__(title=translate("first_launch_sequence_title"))

        self.style_manager = StyleManager
        self.executor = ThreadExecutor()

        self.text_installed = [
            translate("generic_installed"),
            translate("generic_not_installed"),
        ]

        self.text_detected = [
            translate("generic_detected"),
            translate("generic_not_detected"),
        ]

        self.text_unpacked = [
            translate("generic_unpacked"),
            translate("generic_not_unpacked"),
        ]

        self.create()

        settings.update_config("SETTINGS", "first_launch", False)

        self.adjust_to_content(self)

        log.info("First launch window opened.")

    def on_closing(self):
        logging.getLogger().removeHandler(self.text_handler)
        self.text_handler.close()  # Clean up the handler
        log.info("First launch window closed.")
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
                    # "text": text,
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

            self._apply_style(status, status_label, text)

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
            setattr(self, f"{tool_key}_progress_bar_grid_args", progress_bar_grid_args)

            progress_bar.grid_forget()

        self.report = {}

        # Add tools to the report
        for tool_key, tool_path in settings.TOOLS_PATHS.items():
            display_name = TOOLS.get(tool_key, {}).get("display_name", "Unknown")
            status = Data.is_valid_data(tool_path)
            self.report[tool_key] = {
                "label_text": display_name,
                "tool_key": tool_key,
                "status": status,
                "text": self.text_installed,
            }

        # Add AES key to the report
        status = Data.is_valid_data(settings.AES_KEY, "aes")
        self.report["aes_key"] = {
            "label_text": translate("settings_game_aes_key"),
            "tool_key": "aes_key",
            "status": status,
            "text": self.text_detected,
        }

        # Add vanilla files to the report
        for index, value in enumerate(self.games_manager.vanilla_files):
            unpacked = value["unpacked"]
            display_name = str(Path(unpacked).name)
            status = not Files.is_folder_empty(unpacked)
            self.report[f"vanilla_{index}"] = {
                "label_text": display_name,
                "tool_key": f"vanilla_{index}",
                "status": status,
                "text": self.text_unpacked,
            }

        # Create an Intro Frame
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

        # Create a Report Frame
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

        for key, value in self.report.items():
            current_row = self._get_next_row(report_frame)
            create_labeled_text(
                report_frame,
                label_text=value["label_text"],
                tool_key=value["tool_key"],
                status=value["status"],
                text=value["text"],
                row=current_row,
                column=0,
            )

        self.create_separator(self, padx=self.padding)

        # Create a Question Frame
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

        # Create a frame to hold the log display
        log_frame = self.create_frame(
            self,
            column=0,
            padx=self.padding,
            pady=(0, self.padding),
            sticky="nsew",
            column_weights=[(0, 1)],
        )

        # Create the log display as a CTkTextbox
        log_textbox = self.create_ctk_widget(
            ctk_widget=ctk.CTkTextbox,
            widget_args={
                "master": log_frame,
                "wrap": "word",
            },
            # widget_style="SubHeader2.CTkLabel",
            grid_args={
                "column": 0,
                "sticky": "nsew",
                # "padx": (0, self.padding),
                # "pady": (self.padding, 0),
            },
        )

        # Add the TextBoxHandler to the logger
        self.text_handler = TextBoxHandler(log_textbox)
        self.text_handler.setLevel(logging.INFO)

        # Define a custom format for logs displayed in the TextBox
        custom_format = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(custom_format, datefmt="%Y-%m-%d %H:%M:%S")
        self.text_handler.setFormatter(formatter)

        # Add the handler to the root logger
        logging.getLogger().addHandler(self.text_handler)

    def perform_setup_sequence(self):
        results = []

        def execute_tool_installation():

            for tool_key in settings.TOOLS_PATHS.keys():
                if self.report[tool_key]["status"]:
                    results.append(True)
                    continue
                self.installation_progress_callback(tool_key)
                self.update_ui()
                install_method = getattr(self.tools_manager, f"install_{tool_key}")
                install_result = install_method(parent=self, auto_mode=True)
                results.append(install_result)
                if install_result:
                    log.info(f'{settings.TOOLS[tool_key]["display_name"]} installed.')
                    self.installation_progress_callback(tool_key, 1)
                    self._apply_style(
                        True,
                        getattr(self, f"{tool_key}_status_label"),
                        text=self.text_installed,
                    )
                else:
                    self.installation_progress_callback(tool_key, 0)
                self.update_ui()

        def execute_aes_key_detection():
            if self.report["aes_key"]["status"]:
                results.append(True)
                return
            self.installation_progress_callback("aes_key")
            detect_result = self.tools_manager.get_aes_key(
                parent=self, auto_mode=True, skip_aes_dumpster_download=True
            )
            results.append(detect_result)
            if detect_result:
                log.info("AES Key extracted.")
                self.installation_progress_callback("aes_key", 1)
                self._apply_style(
                    True, getattr(self, "aes_key_status_label"), text=self.text_detected
                )
            else:
                self.installation_progress_callback("aes_key", 0)
            self.update_ui()

        def execute_vanilla_unpack():
            for index in range(len(self.games_manager.vanilla_files)):
                if self.report[f"vanilla_{index}"]["status"]:
                    results.append(True)
                    continue
                self.installation_progress_callback(f"vanilla_{index}")
                self.update_ui()
                unpack_result = self.tools_manager.unpack_vanilla_files(
                    parent=self,
                    install_metadata={
                        "index": index,
                        "aes_key": settings.get("SETTINGS", "aes_key"),
                    },
                    auto_mode=True,
                )
                results.append(unpack_result)
                if unpack_result:
                    log.info("Vanilla files unpacked.")
                    self.installation_progress_callback(f"vanilla_{index}", 1)
                    self._apply_style(
                        True,
                        getattr(self, f"vanilla_{index}_status_label"),
                        text=self.text_unpacked,
                    )
                else:
                    self.installation_progress_callback(f"vanilla_{index}", 0)
                self.update_ui()

        def finalize_report():
            if results and all(results):
                self.show_report("info", translate("dialogue_setup_sequence_success"))
            else:
                self.show_report(
                    "warning", translate("dialogue_setup_sequence_warning")
                )

        # Schedule tasks sequentially in a background thread
        def task_sequence():
            execute_tool_installation()
            execute_aes_key_detection()
            execute_vanilla_unpack()
            finalize_report()

        ThreadManager.run_in_background(task_sequence)

    def installation_progress_callback(self, tool_key, value=None):
        progress_bar_widget = getattr(self, f"{tool_key}_progress_bar")
        progress_bar_grid_args = getattr(self, f"{tool_key}_progress_bar_grid_args")
        progress_bar_widget.grid(**progress_bar_grid_args)
        if value != None:
            progress_bar_widget.stop()
            progress_bar_widget.set(value)
        else:
            progress_bar_widget.start()

    def update_ui(self):
        self.executor.run(self.update_idletasks)

    def show_report(self, msg_type, message):
        def show_messagebox():
            if msg_type == "info":
                WindowMessageBox.showinfo(self, message=message)
            elif msg_type == "warning":
                WindowMessageBox.showwarning(self, message=message)

            self.after(0, self.on_closing)

        self.executor.run(show_messagebox)

    def _apply_style(self, is_valid, entry_widget, text):
        if is_valid:
            text = text[0]
            style = "Success.CTkLabel"
        else:
            text = text[1]
            style = "Error.CTkLabel"

        self.style_manager.apply_style(entry_widget, style)
        entry_widget.configure(text=text)

    def skip_setup_sequence(self):
        log.debug("Skipping first launch initial setup sequence...")

        WindowMessageBox.showinfo(
            self,
            message=translate("dialogue_skip_setup_sequence"),
        )

        self.on_closing()
