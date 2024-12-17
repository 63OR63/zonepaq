import ctypes
import io
import tempfile
from concurrent.futures import as_completed
from pathlib import Path
from time import sleep
from tkinter import PhotoImage, filedialog, messagebox

import customtkinter as ctk
from backend.logger import log
from backend.repak import Repak
from backend.tools import Files
from config.settings import settings, translate
from CTkListbox import *
from gui.custom_set_titlebar_icon import custom_set_titlebar_icon
from gui.GUI_Base import GUI_Base
from gui.gui_toplevel import GUI_ConflictsReport
from tkinterdnd2 import DND_FILES


class GUI_LaunchScreen(GUI_Base):
    """Launch screen GUI for navigating to primary application features."""

    def __init__(self):
        super().__init__(title=translate("launch_screen_title"))
        self._setup2()
        self.adjust_to_content()

        log.info("Launch screen opened.")

    # !RENAME method
    def _setup2(self):
        self._create_header(text=translate("launch_screen_header"))

        buttons = {
            "custom": [
                {
                    "text": translate("launch_screen_button_repak"),
                    "width": 300,
                    "height": 60,
                    "command": self._open_repak_gui,
                    "row": 0,
                    "column": 0,
                },
                {
                    "text": translate("launch_screen_button_merge"),
                    "width": 300,
                    "height": 60,
                    "command": self._open_merge_gui,
                    "row": 0,
                    "column": 1,
                },
            ],
            "grid": {"padx": self.padding // 2, "pady": self.padding // 2},
        }

        self._create_buttons(
            buttons,
            self,
            frame_grid_args={
                "row": 1,
                "column": 0,
                "padx": self.padding // 2,
                "pady": self.padding // 2,
            },
            row_weights=[(0, 1)],
            column_weights=[(0, 1), (1, 1)],
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _open_repak_gui(self):
        self.open_gui(GUI_RepakScreen)

    def _open_merge_gui(self):
        self.open_gui(GUI_MergeScreen)

    def on_closing(self):
        # self.customization_manager.reset()
        self.window_manager.close_window(
            self, forced=True
        )  # !FIXME need to refactor window_manager.close_window


class GUI_Secondary(GUI_Base):
    """Secondary GUI window with reusable section-building utilities."""

    def __init__(self, title):
        super().__init__(title=title)
        self.grid_columnconfigure(0, weight=1)

    @property
    def repak_cli(self):
        return settings.TOOLS_PATHS["repak_cli"]

    def create_section(
        self,
        title,
        listbox_name,
        listbox_mode,
        add_command,
        remove_command,
        clear_command,
        action_name,
        action_command,
        hints=None,
    ):
        self._create_header(title)
        self._create_hints(hints)

        section_frame = self._create_section_frame()

        listbox_frame = self._create_listbox_frame(section_frame)
        self._create_listbox(listbox_frame, listbox_name, listbox_mode)
        self._create_side_buttons(
            listbox_frame, add_command, remove_command, clear_command
        )

        self._create_action_button(section_frame, action_name, action_command)

    def _create_header(self, text):
        self._create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": self,
                "text": text,
                "anchor": "center",
                "pady": self.padding,
            },
            widget_style="Header.CTkLabel",
            grid_args={
                "row": self._get_next_row(),
                "column": 0,
                "sticky": "nsew",
                "padx": 0,
                "pady": (0, 0),
            },
            row_weights=None,
            column_weights=None,
        )

    def _create_hints(self, hints):
        if eval(settings.SHOW_HINTS) and hints:
            self._create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": self,
                    "text": hints,
                    "justify": "left",
                },
                widget_style="Hints.CTkLabel",
                grid_args={
                    "row": self._get_next_row(),
                    "column": 0,
                    "sticky": "nw",
                    "padx": (self.padding, 0),
                    "pady": (self.padding, 0),
                },
                row_weights=[(0, 0)],
                column_weights=None,
            )

    def _create_section_frame(self):
        row = self._get_next_row()
        self.grid_rowconfigure(row, weight=1)

        section_frame = self._create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args={"master": self},
            widget_style="Transparent.CTkFrame",
            grid_args={
                "row": row,
                "column": 0,
                "sticky": "nsew",
                "padx": self.padding,
                "pady": 0,
                # "pady": (0, self.padding // 2),
            },
            row_weights=[(0, 1)],
            column_weights=[(0, 1)],
        )

        return section_frame

    def _create_listbox_frame(self, root):
        listbox_frame = self._create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args={
                "master": root,
            },
            widget_style="Transparent.CTkFrame",
            grid_args={
                "row": self._get_next_row(root),
                "column": 0,
                "sticky": "nsew",
                "pady": (self.padding, 0),
            },
            row_weights=[(0, 1)],
            column_weights=[(0, 1), (1, 0)],
        )
        return listbox_frame

    def _create_listbox(self, root, listbox_name, listbox_mode):
        listbox = self._create_ctk_widget(
            ctk_widget=CTkListbox,
            widget_args={
                "master": root,
                "width": 400,
                # "justify": "left",
                "multiple_selection": True,
            },
            widget_style="Custom.CTkListbox",
            grid_args={"row": 0, "column": 0, "sticky": "nsew"},
            # row_weights=[(0, 0)],
            # column_weights=[(0, 0)],
        )
        setattr(self, listbox_name, listbox)

        dnd = self._create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": root,
                "text": f'{translate("generic_dnd")} {translate(listbox_mode)} {translate("generic_here")}',
                "justify": "center",
            },
            widget_style="Dnd.CTkLabel",
            grid_args={
                "row": 0,
                "column": 0,
            },
            row_weights=None,
            column_weights=None,
        )
        setattr(self, f"{listbox_name}_dnd", dnd)

        listbox.master.drop_target_register(DND_FILES)
        listbox.master.dnd_bind(
            "<<Drop>>",
            lambda e: self._add_dnd_files_to_listbox(e, listbox, listbox_mode, dnd),
        )
        # listbox.bind(
        #     "<Delete>",
        #     lambda e: self._remove_from_listbox(listbox, f"{listbox_name}_dnd"),
        # )

        dnd.drop_target_register(DND_FILES)
        dnd.dnd_bind(
            "<<Drop>>",
            lambda e: self._add_dnd_files_to_listbox(e, listbox, listbox_mode, dnd),
        )

        return listbox

    def _create_side_buttons(self, root, add_command, remove_command, clear_command):
        buttons = {
            "custom": [
                {
                    "text": translate("button_add"),
                    "command": add_command,
                    "width": 90,
                    "height": 30,
                    "row": 0,
                    "column": 0,
                },
                {
                    "text": translate("button_remove"),
                    "command": remove_command,
                    "width": 90,
                    "height": 30,
                    "row": 1,
                    "column": 0,
                },
                {
                    "text": translate("button_clear"),
                    "command": clear_command,
                    "width": 90,
                    "height": 30,
                    "row": 2,
                    "column": 0,
                },
            ],
            "grid": {},
        }
        self._create_buttons(
            buttons,
            parent=root,
            frame_grid_args={
                "row": 0,
                "column": 1,
                "sticky": "ns",
                "padx": (self.padding, 0),
                # "pady": (self.padding, 0),
            },
            row_weights=[(0, 1), (1, 1), (2, 1)],
            column_weights=[(0, 1)],
        )

    def _create_action_button(self, section_frame, action_name, action_command):
        buttons = {
            "custom": [
                {
                    "text": action_name,
                    "command": action_command,
                    "style": "Action.CTkButton",
                    "width": 170,
                    "height": 40,
                    "row": 1,
                    "column": 0,
                },
            ],
            "grid": {
                "padx": 0,
                "pady": self.padding,
            },
        }
        self._create_buttons(
            buttons,
            parent=section_frame,
            frame_grid_args={
                "row": 2,
                "column": 0,
                "sticky": "ns",
                "padx": 0,
                "pady": 0,
            },
        )

    def _get_next_row(self, root=None):
        root = root or self
        return len(root.grid_slaves())

    def _add_dnd_files_to_listbox(self, event, listbox, mode, dnd):
        try:
            dropped_files_raw = event.data
            files = [path for path in dropped_files_raw.split("}") if path]
            for path in files:
                path = path.replace("{", "").replace("}", "")
                path = Path(path.strip())
                if str(path) not in listbox.get("all"):
                    if (
                        mode == "pak"
                        and path.is_file()
                        and path.suffix.lower() == ".pak"
                    ):
                        listbox.insert("END", str(path))
                        # !WORKAROUND for lacking anchor option in the text Label
                        list(listbox.buttons.values())[-1]._text_label.configure(
                            anchor="w"
                        )
                        list(listbox.buttons.values())[-1].configure(
                            anchor="w", height=0
                        )
                        log.debug(f"Added {str(path)} to {listbox}")
                    elif mode == "folder" and path.is_dir():
                        listbox.insert("END", str(path))
                        # !WORKAROUND for lacking anchor option in the text Label
                        list(listbox.buttons.values())[-1]._text_label.configure(
                            anchor="w"
                        )
                        list(listbox.buttons.values())[-1].configure(
                            anchor="w", height=0
                        )
                        log.debug(f"Added {str(path)} to {listbox}")
                    else:
                        log.debug(f"Invalid path: {str(path)} (Mode: {mode})")

        except Exception as e:
            log.error(f"DnD error: {e}")
        if listbox.get("all"):
            dnd.grid_forget()

    def _add_file_to_listbox(self, listbox, dnd):
        files = filedialog.askopenfilenames(
            filetypes=[(translate("dialogue_pak_files"), "*.pak")]
        )
        for file in files:
            file = Path(file.strip())
            if str(file) not in listbox.get("all"):
                listbox.insert("END", str(file))
                # !WORKAROUND for lacking anchor option in the text Label
                list(listbox.buttons.values())[-1]._text_label.configure(anchor="w")
                list(listbox.buttons.values())[-1].configure(anchor="w", height=0)
                log.debug(f"Added {str(file)} to {listbox}")
        if listbox.get("all"):
            dnd.grid_forget()

    def _add_folder_to_listbox(self, listbox, dnd):
        folder = filedialog.askdirectory()
        if folder:
            folder = Path(folder.strip())
            if str(folder) not in listbox.get("all"):
                listbox.insert("END", str(folder))
                # !WORKAROUND for lacking anchor option in the text Label
                list(listbox.buttons.values())[-1]._text_label.configure(anchor="w")
                list(listbox.buttons.values())[-1].configure(anchor="w", height=0)
                log.debug(f"Added {str(folder)} to {listbox}")
        if listbox.get("all"):
            dnd.grid_forget()

    def _remove_from_listbox(self, listbox, dnd):
        try:
            selected_indices = listbox.curselection()
            if not selected_indices:
                log.debug("No items selected to remove.")
                return

            for index in reversed(selected_indices):
                listbox.delete(index)
            log.debug(f"Removed items at indices {selected_indices} from {listbox}")
        except Exception as e:
            log.error(f"Error removing selected items: {e}")
        if not listbox.get("all"):
            dnd.grid(
                row=0,
                column=0,
            )

    def _clear_listbox(self, listbox, dnd):
        listbox.delete("all")
        log.debug(f"Cleared {listbox}")

        dnd.grid(
            row=0,
            column=0,
        )

    def show_results(self, results_ok, results_ko):
        message_ok = "\n".join(results_ok) if results_ok else ""
        message_ko = "\n".join(results_ko) if results_ko else ""

        message = ""
        if message_ok:
            message += f"Success:\n{message_ok}\n"
        if message_ko:
            message += f"Failed:\n{message_ko}"

        if message:
            messagebox.showinfo(translate("generic_results"), message)

    def on_closing(self):
        self.window_manager.open_window(self, GUI_LaunchScreen)
        # self.open_launch_screen()

    # def open_launch_screen(self):
    #     log.debug("Opening launch screen...")
    #     self.open_gui(GUI_LaunchScreen)


class GUI_RepakScreen(GUI_Secondary):
    """GUI for unpacking and repacking files."""

    def __init__(self):
        super().__init__(title=translate("repak_screen_title"))
        self._create_sections()
        self.adjust_to_content(adjust_width=True, adjust_height=True)

        log.info("Repak screen opened.")

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
                "action_command": self._unpack_files,
                "hints": translate("repak_screen_unpack_hints"),
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
                "hints": translate("repak_screen_repack_hints"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def _unpack_files(self):
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            messagebox.showerror(
                translate("generic_error"),
                f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                parent=self,
            )
            return
        files = self.unpack_listbox.get("all")
        if files:
            folder = filedialog.askdirectory()
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
                    overwrite = messagebox.askyesno(
                        translate("generic_warning"),
                        f'{translate("repak_screen_unpack_msg_overwrite_1")}\n\n'
                        + "\n".join(map(str, existing_folders))
                        + f'\n\n{translate("repak_screen_unpack_msg_overwrite_2")}',
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
                            results_ok.append(f"Unpacked {file} to: {result}")
                        else:
                            results_ko.append(f"Error unpacking {file}: {result}")
                    except Exception as e:
                        results_ko.append(f"Error unpacking {file}: {str(e)}")

                self.show_results(results_ok, results_ko)

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repak_screen_unpack_msg_empty_list"),
            )

    def _repack_folders(self):
        if not Files.is_existing_file_type(self.repak_cli, ".exe"):
            log.error(f"repak_cli executable isn't found at {str(self.repak_cli)}")
            messagebox.showerror(
                translate("generic_error"),
                f'repak_cli executable {translate("error_executable_not_found_1")} {str(self.repak_cli)}\n{translate("error_executable_not_found_2")}',
                parent=self,
            )
            return
        folders = self.repack_listbox.get("all")
        if folders:
            target_folder = filedialog.askdirectory()
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
                            results_ok.append(f"Repacked {folder} into: {result}")
                        else:
                            results_ko.append(f"Error repacking {folder}: {result}")
                    except Exception as e:
                        results_ko.append(f"Error repacking {folder}: {str(e)}")

                self.show_results(results_ok, results_ko)

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repack_screen_repack_msg_empty_list"),
            )


class GUI_MergeScreen(GUI_Secondary):
    """GUI for analyzing and reporting file conflicts during merging."""

    def __init__(self):
        super().__init__(title=translate("merge_screen_title"))
        self._create_sections()

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

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repack_screen_repack_msg_empty_list"),
            )
