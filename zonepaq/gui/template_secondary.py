import re
from pathlib import Path

import customtkinter as ctk
from backend.logger import log
from config.settings_manager import settings
from config.translations import translate
from CTkListbox import CTkListbox
from gui.template_toplevel import TemplateToplevel
from gui.window_messagebox import ModalFileDialog, WindowMessageBox
from tkinterdnd2 import DND_FILES


class TemplateSecondary(TemplateToplevel):

    def __init__(self, master, title):
        super().__init__(master, title=title)

        self.grid_columnconfigure(0, weight=1)

    @property
    def repak_cli(self):
        return settings.TOOLS_PATHS["repak_cli"]

    def on_closing(self):
        raise NotImplementedError("Subclasses must implement the 'on_closing' method.")

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
        tooltip_action_button,
        hints=None,
    ):
        self.create_header(self, title)
        self.create_hints(self, hints)

        section_frame = self.create_frame(
            self,
            padx=self.padding,
            pady=self.padding,
            column_weights=[(0, 1), (1, 0)],
            row_weights=[(0, 1)],
            sticky="nsew",
        )
        self.grid_rowconfigure(section_frame.grid_info().get("row"), weight=1)

        self._create_listbox(section_frame, listbox_name, listbox_mode)

        # ! need to expand clickable area
        listbox = getattr(self, listbox_name)
        dnd = getattr(self, f"{listbox_name}_dnd")
        dnd.bind(
            "<Button-1>",
            lambda e: self._add_manually_to_listbox(listbox, dnd, listbox_mode),
        )

        self._create_side_buttons(
            section_frame, add_command, remove_command, clear_command
        )

        action_button = self._create_action_button(
            section_frame, action_name, action_command
        )
        self.add_tooltip(action_button, tooltip_action_button)

    def _create_listbox(self, root, listbox_name, listbox_mode):
        listbox = self.create_ctk_widget(
            ctk_widget=CTkListbox,
            widget_args={
                "master": root,
                "width": 400,
                "multiple_selection": True,
            },
            widget_style="Custom.CTkListbox",
            grid_args={"row": 0, "column": 0, "sticky": "nsew"},
            row_weights=[(0, 1)],
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

        listbox.bind(
            "<Control-v>",
            lambda e: self._paste_clipboard_to_listbox(listbox, dnd, mode=listbox_mode),
        )

        # ! https://github.com/Akascape/CTkListbox/pull/68
        # listbox.bind(
        #     "<Control-a>", lambda e: self._select_all_items_in_listbox(listbox)
        # )

        listbox.bind("<Delete>", lambda e: self._remove_from_listbox(listbox, dnd))

        listbox.master.drop_target_register(DND_FILES)
        listbox.master.dnd_bind(
            "<<Drop>>",
            lambda e: self._add_dnd_to_listbox(e, listbox, dnd, listbox_mode),
        )

        dnd.drop_target_register(DND_FILES)
        dnd.dnd_bind(
            "<<Drop>>",
            lambda e: self._add_dnd_to_listbox(e, listbox, dnd, listbox_mode),
        )

        return listbox

    def _create_side_buttons(self, root, add_command, remove_command, clear_command):
        buttons_frame = self.create_frame(
            root,
            row=0,
            column=1,
            style="Transparent.CTkFrame",
            row_weights=[(0, 1), (1, 1), (2, 1)],
            padx=(self.padding, 0),
        )
        width = 90
        height = 30
        self.create_button(
            buttons_frame,
            text=translate("button_add"),
            command=add_command,
            width=width,
            height=height,
            sticky="s",
        )
        self.create_button(
            buttons_frame,
            text=translate("button_remove"),
            command=remove_command,
            width=width,
            height=height,
            pady=self.padding,
        )
        self.create_button(
            buttons_frame,
            text=translate("button_clear"),
            command=clear_command,
            width=width,
            height=height,
            sticky="n",
        )

    def _create_action_button(self, section_frame, action_name, action_command):
        return self.create_button(
            section_frame,
            text=action_name,
            command=action_command,
            style="Action.CTkButton",
            width=170,
            height=40,
            padx=0,
            pady=(self.padding, 0),
            column=0,
            columnspan=999,
        )

    # ! https://github.com/Akascape/CTkListbox/pull/68
    # def _select_all_items_in_listbox(self, listbox):
    #     try:
    #         listbox.select("all")
    #         CTkListbox.select("all")
    #     except Exception as e:
    #         log.error("Couldn't select all items in a listbox:", e)

    def _paste_clipboard_to_listbox(self, listbox, dnd, mode):
        try:
            clipboard_data = self.clipboard_get()
            paths = clipboard_data.splitlines()

            self._add_items_to_listbox(paths, listbox, dnd, mode)
        except Exception as e:
            log.error("Clipboard error:", e)

    def _add_items_to_listbox(self, items, listbox, dnd, mode):
        collector = []
        for item in items:
            path = Path(item.strip())
            if str(path) not in listbox.get("all"):
                if mode == "pak" and path.is_file() and path.suffix.lower() == ".pak":
                    collector.append(str(path))
                elif mode == "folders" and path.is_dir():
                    collector.append(str(path))
                else:
                    log.debug(f"Invalid path: {str(path)} (Mode: {mode})")

        if collector:
            dnd.grid_forget()
            listbox.focus_set()

            for item in collector:
                listbox.insert("END", item)
                log.debug(f"Added {item} to listbox")
                list(listbox.buttons.values())[-1]._text_label.configure(anchor="w")
                list(listbox.buttons.values())[-1].configure(anchor="w", height=0)

        if not listbox.get("all"):
            dnd.grid(row=0, column=0)

    def _add_dnd_to_listbox(self, event, listbox, dnd, mode):
        try:
            dropped_files_raw = event.data
            regex = r"(?:\{([^}]+)\}|\S+)"
            files = [
                match.group(1) or match.group(0)
                for match in re.finditer(regex, dropped_files_raw)
            ]
            self._add_items_to_listbox(files, listbox, dnd, mode)
        except Exception as e:
            log.error(f"DnD error: {e}")

    def _add_manually_to_listbox(self, listbox, dnd, mode):
        if mode == "pak":
            files = ModalFileDialog.askopenfilenames(
                parent=self,
                filetypes=[(translate("dialogue_pak_files"), "*.pak")],
                initialdir=self.games_manager.mods_path,
            )
            if files:
                self._add_items_to_listbox(files, listbox, dnd, mode="pak")
        elif mode == "folders":
            folder = ModalFileDialog.askdirectory(parent=self)
            if folder:
                self._add_items_to_listbox([folder], listbox, dnd, mode="folders")

    def _remove_from_listbox(self, listbox, dnd):
        try:
            selected_indices = listbox.curselection()
            if not selected_indices:
                log.debug("No items selected to remove.")
                return

            for index in reversed(selected_indices):
                log.debug(f"Removing {listbox.get(index)} from listbox")
                listbox.delete(index)
        except Exception as e:
            log.error(f"Error removing selected items: {e}")
        if not listbox.get("all"):
            dnd.grid(row=0, column=0)

    def _clear_listbox(self, listbox, dnd):
        listbox.delete("all")
        log.debug(f"Cleared listbox")

        dnd.grid(row=0, column=0)

    def show_results(
        self,
        results_ok,
        results_ko,
        title_ok=translate("generic_success"),
        title_ko=translate("generic_fail"),
    ):
        message_ok = "\n".join(results_ok) if results_ok else ""
        message_ko = "\n".join(results_ko) if results_ko else ""

        message = []
        if message_ok:
            message += [title_ok + ":", message_ok]
        if message_ko:
            message += [title_ko + ":", message_ko]

        if message:
            WindowMessageBox.showinfo(self, message=message)
