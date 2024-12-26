from concurrent.futures import as_completed
from pathlib import Path

from backend.logger import log
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
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            WindowMessageBox.showerror(
                self,
                message=f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
            )
            return
        files = self.unpack_listbox.get("all")
        if files:
            folder = ModalFileDialog.askdirectory(parent=self)
            if folder:
                folder = Path(folder)
                existing_folders = []
                for file in files:
                    file = Path(file)
                    unpacked_folder = file.with_suffix("").name
                    target_folder = folder / unpacked_folder
                    if target_folder.is_dir():
                        existing_folders.append(target_folder)

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

                results_ok = []
                results_ko = []
                futures = {}

                for file in files:
                    file = Path(file)
                    futures[Repak.unpack(file, folder)] = file

                for future in as_completed(futures):
                    file = futures[future]
                    try:
                        success, result = future.result()
                        if success:
                            results_ok.append(str(file))
                        else:
                            results_ko.append(f"{str(file)}: {result}")
                    except Exception as e:
                        results_ko.append(f"{str(file)}: {str(e)}")

                self.show_results(results_ok, results_ko)

        else:
            WindowMessageBox.showwarning(
                self,
                message=translate("repak_screen_unpack_msg_empty_list"),
            )

    def _repack_folders(self):
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            WindowMessageBox.showerror(
                self,
                message=f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
            )
            return
        folders = self.repack_listbox.get("all")
        if folders:
            target_folder = ModalFileDialog.askdirectory(parent=self)
            if target_folder:
                target_folder = Path(target_folder)
                results_ok = []
                results_ko = []

                futures = {}

                # Submit repack tasks
                for folder in folders:
                    folder = Path(folder)
                    futures[Repak.repack(folder, target_folder)] = folder

                for future in as_completed(futures):
                    folder = futures[future]
                    try:
                        success, result = future.result()
                        if success:
                            results_ok.append(str(folder))
                        else:
                            results_ko.append(f"{str(folder)}: {result}")
                    except Exception as e:
                        results_ko.append(f"{str(folder)}: {str(e)}")

                self.show_results(results_ok, results_ko)

        else:
            WindowMessageBox.showwarning(
                self,
                message=translate("repak_screen_repack_msg_empty_list"),
            )
