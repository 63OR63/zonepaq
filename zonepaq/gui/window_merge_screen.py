from backend.logger import log
from backend.repak import Repak
from backend.tools import Files
from config.settings import translate
from gui.window_conflicts import GUI_ConflictsReport
from gui.template_secondary import GUI_Secondary


from concurrent.futures import as_completed
from pathlib import Path
from tkinter import messagebox


class GUI_MergeScreen(GUI_Secondary):
    """GUI for analyzing and reporting file conflicts during merging."""

    def __init__(self, master):
        super().__init__(master, title=translate("merge_screen_title"))
        self._create_sections()

        self.adjust_to_content(self, adjust_width=True, adjust_height=True)

        log.info("Merge screen opened.")

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
                "hints": translate("merge_screen_hints"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def _find_conflicts(self):
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            messagebox.showerror(
                translate("generic_error"),
                f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                parent=self,
            )
            return
        files = self.merge_listbox.get("all")
        if files:
            results_ok = {}
            results_ko = {}
            futures = {}

            for file in files:
                file = Path(file)
                futures[Repak.get_list(file)] = file

            for future in as_completed(futures):
                file = futures[future]
                try:
                    success, result = future.result()
                    if success:
                        results_ok[file.as_posix()] = result
                    else:
                        results_ko[file.as_posix()] = result
                except Exception as e:
                    results_ko[file.as_posix()] = str(e)

            content_tree = Files.build_content_tree(results_ok)

            log.debug("Opening conflicts resolver screen...")
            GUI_ConflictsReport(parent=self, content_tree=content_tree)
            # self.open_gui("GUI_ConflictsReport")

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repack_screen_repack_msg_empty_list"),
            )