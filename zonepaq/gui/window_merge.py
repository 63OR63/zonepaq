from pathlib import Path

from backend.logger import log
from backend.parallel_orchestrator import (
    TaskRetryManager,
    ThreadExecutor,
    ThreadManager,
)
from backend.repak import Repak
from backend.utilities import Data, Files
from config.translations import translate
from gui.template_secondary import TemplateSecondary
from gui.window_conflicts import WindowConflicts
from gui.window_messagebox import WindowMessageBox


class WindowMerge(TemplateSecondary):
    """GUI for analyzing and reporting file conflicts during merging."""

    def __init__(self, master):
        super().__init__(master, title=translate("merge_screen_title"))
        self._create_sections()
        self.create_settings_button(self)

        self.adjust_to_content(self, adjust_width=True, adjust_height=True)

        log.info("Merge window opened.")

    def on_closing(self):
        log.info("Merge window closed.")
        self.destroy()
        self.master.deiconify()

    def _create_sections(self):
        sections = [
            {
                "title": translate("merge_screen_header"),
                "listbox_name": "merge_listbox",
                "listbox_mode": "pak",
                "add_command": lambda: self._add_file_to_listbox(
                    self.merge_listbox, self.merge_listbox_dnd
                ),
                "remove_command": lambda: self._remove_from_listbox(
                    self.merge_listbox, self.merge_listbox_dnd
                ),
                "clear_command": lambda: self._clear_listbox(
                    self.merge_listbox, self.merge_listbox_dnd
                ),
                "action_name": translate("merge_screen_analyze_button"),
                "action_command": self._find_conflicts,
                # "hints": translate("merge_screen_hints"),
                "tooltip_action_button": translate("tooltip_button_merge"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def _find_conflicts(self):
        def task_runner(files):
            task_retry_manager = TaskRetryManager(ThreadExecutor())

            # Execute the tasks
            results_ok, results_ko = task_retry_manager.execute_tasks_with_retries(
                files, Repak.get_list
            )

            # Handle errors and results on the main thread
            if results_ko:
                self.after(
                    0,
                    lambda: WindowMessageBox.showerror(
                        self,
                        message="\n".join(
                            [
                                translate("merge_screen_analyze_msg_error_header"),
                                *[
                                    f"{str(Path(key))} ({value})"
                                    for key, value in results_ko.items()
                                ],
                            ]
                        ),
                    ),
                )

            if results_ok:
                content_tree = Data.build_content_tree(results_ok)
                log.debug("Opening conflicts resolver screen...")
                self.after(
                    0, lambda: WindowConflicts(master=self, content_tree=content_tree)
                )

        # Validate repak_cli path on the main thread
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            self.after(
                0,
                lambda: WindowMessageBox.showerror(
                    self,
                    message=f'repak_cli {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                ),
            )
            return

        # Get file list on the main thread
        files = self.merge_listbox.get("all")
        if not files:
            self.after(
                0,
                lambda: WindowMessageBox.showwarning(
                    self, message=translate("merge_screen_analyze_msg_empty_list")
                ),
            )
            return

        # Run the background task
        ThreadManager.run_in_background(lambda: task_runner(files))
