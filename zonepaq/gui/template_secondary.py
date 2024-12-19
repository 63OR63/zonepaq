from pathlib import Path
from tkinter import filedialog, messagebox

from CTkListbox import CTkListbox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from backend.logger import log
from config.settings import settings, translate

from gui.template_toplevel import GUI_Toplevel


class GUI_Secondary(GUI_Toplevel):

    def __init__(self, master, title):
        super().__init__(master, title=title)

        self.grid_columnconfigure(0, weight=1)

    @property
    def repak_cli(self):
        return settings.TOOLS_PATHS["repak_cli"]

    def on_closing(self):
        self.destroy()
        self.master.deiconify()

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
        self.create_header(self, title)
        self.create_hints(self, hints)

        section_frame = self.create_frame(
            self,
            padx=self.padding,
            pady=self.padding,
            column_weights=[(0, 1)],
        )

        listbox_frame = self.create_frame(
            section_frame,
            column_weights=[(0, 1), (1, 0)],
        )
        self._create_listbox(listbox_frame, listbox_name, listbox_mode)
        self._create_side_buttons(
            listbox_frame, add_command, remove_command, clear_command
        )

        self._create_action_button(section_frame, action_name, action_command)

    def _create_listbox(self, root, listbox_name, listbox_mode):
        listbox = self.create_ctk_widget(
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

        dnd = self.create_ctk_widget(
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
        self.create_buttons(
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
                "pady": (self.padding, 0),
            },
        }
        self.create_buttons(
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
