from pathlib import Path

from backend.logger import log
from backend.parallel_orchestrator import (
    TaskRetryManager,
    ThreadExecutor,
    ThreadManager,
)
from backend.repak import Repak
from backend.utilities import Files
from config.translations import translate
from CTkListbox import *
from gui.template_secondary import TemplateSecondary
from gui.window_messagebox import ModalFileDialog, WindowMessageBox


class WindowRepak(TemplateSecondary):
    """GUI for unpacking and repacking files."""

    def __init__(self, master):
        super().__init__(master, title=translate("repak_screen_title"))
        self._create_sections()
        self.create_settings_button(self)

        self.adjust_to_content(self, adjust_width=True, adjust_height=True)

        log.info("Repak window opened.")

    def on_closing(self):
        log.info("Repak window closed.")
        self.destroy()
        self.master.deiconify()

    def _create_sections(self):
        sections = [
            {
                "title": translate("repak_screen_unpack_header"),
                "listbox_name": "unpack_listbox",
                "listbox_mode": "pak",
                "add_command": lambda: self._add_file_to_listbox(
                    self.unpack_listbox, self.unpack_listbox_dnd
                ),
                "remove_command": lambda: self._remove_from_listbox(
                    self.unpack_listbox, self.unpack_listbox_dnd
                ),
                "clear_command": lambda: self._clear_listbox(
                    self.unpack_listbox, self.unpack_listbox_dnd
                ),
                "action_name": translate("repak_screen_unpack_button"),
                "action_command": self.unpack_files,
                # "hints": translate("repak_screen_unpack_hints"),
                "tooltip_action_button": translate("tooltip_button_unpack"),
            },
            {
                "title": translate("repak_screen_repack_header"),
                "listbox_name": "repack_listbox",
                "listbox_mode": "folders",
                "add_command": lambda: self._add_folder_to_listbox(
                    self.repack_listbox, self.repack_listbox_dnd
                ),
                "remove_command": lambda: self._remove_from_listbox(
                    self.repack_listbox, self.repack_listbox_dnd
                ),
                "clear_command": lambda: self._clear_listbox(
                    self.repack_listbox, self.repack_listbox_dnd
                ),
                "action_name": translate("repak_screen_repack_button"),
                "action_command": self._repack_folders,
                # "hints": translate("repak_screen_repack_hints"),
                "tooltip_action_button": translate("tooltip_button_repack"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def unpack_files(self):
        def task_runner(files, folder, overwrite):
            task_retry_manager = TaskRetryManager(ThreadExecutor())
            results_ok, results_ko = task_retry_manager.execute_tasks_with_retries(
                files, lambda f: Repak.unpack(f, folder)
            )

            # Show results on the main thread
            self.after(
                0,
                lambda: self.show_results(
                    results_ok=[str(file) for file in results_ok],
                    results_ko=[
                        f"{str(file)}: {result}" for file, result in results_ko.items()
                    ],
                    title_ok=translate("generic_files_were_unpacked"),
                    title_ko=translate("generic_files_were_not_unpacked"),
                ),
            )

        # Validate repak_cli path on the main thread
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            self.after(
                0,
                lambda: WindowMessageBox.showerror(
                    self,
                    message=f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                ),
            )
            return

        # Get file list on the main thread
        files = self.unpack_listbox.get("all")
        if not files:
            self.after(
                0,
                lambda: WindowMessageBox.showwarning(
                    self, message=translate("repak_screen_unpack_msg_empty_list")
                ),
            )
            return

        # Ask for the target folder on the main thread
        folder = ModalFileDialog.askdirectory(
            parent=self, initialdir=self.games_manager.mods_path
        )
        if not folder:
            return

        folder = Path(folder)
        existing_folders = []
        for file in files:
            file = Path(file)
            unpacked_folder = file.with_suffix("").name
            target_folder = folder / unpacked_folder
            if target_folder.is_dir():
                existing_folders.append(target_folder)

        # Handle overwrite confirmation on the main thread
        overwrite = True
        if existing_folders:
            overwrite = WindowMessageBox.askyesno(
                self,
                message=[
                    translate("repak_screen_unpack_msg_overwrite_1"),
                    "\n".join(map(str, existing_folders)),
                    translate("repak_screen_unpack_msg_overwrite_2"),
                ],
            )
            if not overwrite:
                return

        # Run the background task
        ThreadManager.run_in_background(lambda: task_runner(files, folder, overwrite))

    def _repack_folders(self):
        def task_runner(folders, target_folder):
            task_retry_manager = TaskRetryManager(ThreadExecutor())
            results_ok, results_ko = task_retry_manager.execute_tasks_with_retries(
                folders, lambda f: Repak.repack(Path(f), target_folder)
            )

            # Show results on the main thread
            self.after(
                0,
                lambda: self.show_results(
                    results_ok=[str(folder) for folder in results_ok],
                    results_ko=[
                        f"{str(folder)}: {result}"
                        for folder, result in results_ko.items()
                    ],
                    title_ok=translate("generic_folders_were_repacked"),
                    title_ko=translate("generic_folders_were_not_repacked"),
                ),
            )

        # Validate repak_cli path on the main thread
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            self.after(
                0,
                lambda: WindowMessageBox.showerror(
                    self,
                    message=f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                ),
            )
            return

        # Get folders list on the main thread
        folders = self.repack_listbox.get("all")
        if not folders:
            self.after(
                0,
                lambda: WindowMessageBox.showwarning(
                    self, message=translate("repak_screen_repack_msg_empty_list")
                ),
            )
            return

        # Ask for the target folder on the main thread
        target_folder = ModalFileDialog.askdirectory(
            parent=self, initialdir=self.games_manager.mods_path
        )
        if not target_folder:
            return

        # Run the background task
        ThreadManager.run_in_background(
            lambda: task_runner(folders, Path(target_folder))
        )
