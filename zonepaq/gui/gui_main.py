import io
import json
import tempfile
import tkinter as tk
from collections import deque
from concurrent.futures import as_completed
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from backend.logger import handle_exception, log
from backend.repak import Repak
from backend.tools import Files
from config.ctk_themes import ctk_color_theme
from config.ctk_styles import StyleManager
from config.metadata import APP_NAME, APP_VERSION
from config.settings import settings, translate
from config.styles import get_styles
from gui.gui_toplevel import GUI_ConflictsReport
from gui.menus import MenuRibbon
from gui.widgets import CustomButton, set_app_icon

import customtkinter as ctk
from CTkListbox import *
from unittest.mock import mock_open, patch


# ctk.CTk._block_update_dimensions_event = False

import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(0)


class InstanceManager:
    """Manages registration and cleanup of windows and widgets."""

    def __init__(self):
        self._reset()

    def register_window(self, window):
        if window not in self.windows:
            log.deep_debug(f"Registering window: {window}")
            self.windows.append(window)

    def unregister_window(self, window):
        if window in self.windows:
            log.deep_debug(f"Unregistering window: {window}")
            self.windows.remove(window)

        for widget in list(self.widgets.keys()):
            if self.widgets[widget] == window:
                log.deep_debug(f"Unregistering widget: {widget} @ {window}")
                self.widgets.pop(widget)

    def register_widget(self, widget, window):
        if widget not in self.widgets:
            log.deep_debug(f"Registering widget: {widget} @ {window}")
            self.widgets[widget] = window

    def _reset(self):
        log.deep_debug("'windows' and 'widgets' instance storages reset.")
        self.windows = deque()
        self.widgets = {}


class CustomizationManager:
    """Singleton class to apply and manage UI themes and customizations."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, style, theme_dict):
        self.style = style
        self.theme_dict = theme_dict
        self.instances = InstanceManager()  # Central instance tracking
        self._reload_styles(self.theme_dict)

    @classmethod
    def get(cls, theme_dict):
        if cls._instance is None:
            style = ttk.Style()
            style.theme_use("clam")
            # style.theme_use("alt")
            # style.theme_use("default")
            # style.theme_use("classic")
            # style.theme_use("vista")
            # style.theme_use("xpnative")
            cls._instance = cls(style, theme_dict)
        return cls._instance

    def reset(self):
        self.instances._reset()
        log.deep_debug("'CustomizationManager' instance cleared.")
        CustomizationManager._instance = None

    def apply_theme(self, window, theme_name):
        settings.update_config("SETTINGS", "theme_name", theme_name)

        self._reload_styles(settings.THEME_DICT)

        for widget in self.instances.widgets:
            widget.apply_style()

        for window in self.instances.windows:
            self._apply_specific_styles(window)

    def apply_translation(self, window, lang_name):
        settings.update_config("SETTINGS", "lang_name", lang_name)

        self.reset()

        window.destroy()
        gui = GUI_LaunchScreen()
        gui.run()

    def apply_show_hints(self, window, show_hints):
        settings.SHOW_HINTS = str(show_hints)
        settings.update_config("SETTINGS", "show_hints", show_hints)

        self.reset()

        window.destroy()
        gui = GUI_LaunchScreen()
        gui.run()

    def _reload_styles(self, theme_dict):
        styles = get_styles(theme_dict)
        for widget, config in styles.items():
            self.style.configure(widget, **config)

        self._map_style("TCheckbutton", theme_dict["color_background"])
        self._map_style("Treeview.Heading", theme_dict["color_background"])

    def _map_style(self, widget, color):
        self.style.map(
            widget,
            background=[
                ("active", color),
                ("!active", color),
            ],
        )

    def _apply_specific_styles(self, widget, generic={}, listboxes={}):
        excluded_widgets = (
            tk.Menu,
            tk.Entry,
        )

        default_generic = {
            "bg": settings.THEME_DICT["color_background"],
            "fg": settings.THEME_DICT["color_foreground"],
        }
        default_listboxes = {
            "bg": settings.THEME_DICT["color_background_highlight"],
            "fg": settings.THEME_DICT["color_foreground"],
            "selectbackground": settings.THEME_DICT["color_highlight"],
            "font": (
                settings.THEME_DICT["font_family_code"],
                settings.THEME_DICT["font_size_small"],
                "normal",
            ),
        }
        treeview_tags = {
            "no_conflicts": {"foreground": settings.THEME_DICT["color_success"]},
            "dual_match": {"foreground": settings.THEME_DICT["color_foreground"]},
            "dual_no_match": {"foreground": settings.THEME_DICT["color_attention"]},
            "tri": {"foreground": settings.THEME_DICT["color_warning"]},
            "complex": {"foreground": settings.THEME_DICT["color_error"]},
        }

        generic = {**default_generic, **generic}
        listboxes = {**default_listboxes, **listboxes}

        queue = deque([widget])

        while queue:
            current_widget = queue.popleft()
            if not isinstance(current_widget, excluded_widgets):
                if isinstance(current_widget, tk.Listbox):
                    for key, value in listboxes.items():
                        try:
                            if hasattr(current_widget, "configure"):
                                current_widget.configure({key: value})
                        except:
                            pass
                elif isinstance(current_widget, ttk.Treeview):
                    for tag, style in treeview_tags.items():
                        try:
                            current_widget.tag_configure(tag, **style)
                        except:
                            pass
                else:
                    for key, value in generic.items():
                        try:
                            if hasattr(current_widget, "configure"):
                                current_widget.configure({key: value})
                        except:
                            pass

            queue.extend(current_widget.winfo_children())


# class GUI_Base(tk.Tk):
class GUI_Base(ctk.CTk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title, width=800, height=350, resizable=(False, False)):
        super().__init__()  # Initialize the tk.Tk class
        log.debug(self._block_update_dimensions_event)
        self.report_callback_exception = handle_exception

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")
        self.configure(bg=settings.THEME_DICT["color_background"])
        set_app_icon(self)
        self.customization_manager = CustomizationManager.get(settings.THEME_DICT)
        self.customization_manager.instances.register_window(self)

        self.menu = MenuRibbon(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.padding = 30

        theme_str = json.dumps(ctk_color_theme)
        mocked_file = mock_open(read_data=theme_str)
        with patch("builtins.open", mocked_file):
            ctk.set_default_color_theme("mocked_theme")

        StyleManager.define_style(
            "Header.CTkLabel",
            fg_color=ctk_color_theme["CTkOptionMenu"]["fg_color"],
            text_color=ctk_color_theme["CTkOptionMenu"]["text_color"],
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Header.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Header.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Header.CustomFont"]["weight"],
            ),
        )
        StyleManager.define_style(
            "Transparent.CTkFrame",
            fg_color="transparent",
            border_color="red",
            border_width=1,
        )
        StyleManager.define_style(
            "Large.CTkButton",
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Button.CustomFont"]["weight"],
            ),
        )

        # with tempfile.NamedTemporaryFile(
        #     mode="w", delete=False, suffix=".json"
        # ) as tmp_file:
        #     json.dump(ctk_color_theme, tmp_file)  # Write the JSON data
        #     tmp_file.close()  # Close the file to release the lock
        #     ctk.set_default_color_theme(tmp_file.name)

        # ctk.set_default_color_theme(Path("zonepaq/config/themes2/Nord.json"))

    def adjust_to_content(self, root=None, adjust_width=False, adjust_height=False):
        root = root or self
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()

        # log.debug(width)
        # log.debug(height)
        # # log.debug(root._current_width)
        # # log.debug(root._current_height)
        # # log.debug(root._min_width)
        # # log.debug(root._min_height)
        # # log.debug(root._max_width)
        # # log.debug(root._max_height)
        # root.after(500, lambda: print(f".height() -> {root._min_width}"))
        # root.after(500, lambda: print(f".height() -> {root._min_height}"))
        # root.after(500, lambda: print(f".height() -> {root._current_width}"))
        # root.after(500, lambda: print(f".height() -> {root._current_height}"))

        # log.debug(root.winfo_width())
        # log.debug(root.winfo_height())
        # root.after(
        #     500,
        #     lambda: (
        #         root.update_idletasks(),
        #         print(f".height() -> {root.winfo_width()}"),
        #     ),
        # )
        # root.after(
        #     500,
        #     lambda: (
        #         root.update_idletasks(),
        #         print(f".height() -> {root.winfo_height()}"),
        #     ),
        # )

        # root.after(1500, lambda: (root.update_idletasks(), root.minsize(root.winfo_width(), root.winfo_height())))

        root.after(
            1009, lambda: root.minsize(root._current_width, root._current_height)
        )

        # root.minsize(0, 0)
        # log.debug(height)
        # root.after(500, lambda: print(f".height() -> {root.winfo_reqheight()}"))
        # root.minsize(width, height)
        root.resizable(adjust_width, adjust_height)

    def on_closing(self):
        self.customization_manager.reset()
        self.destroy()

    def _create_header(self, text):
        # header_label = ctk.Label(self, text=text, style="Header.TLabel")
        header_label = ctk.CTkLabel(
            self,
            text=text,
            anchor="center",
            pady=self.padding / 1.5,
        )
        header_label.grid(row=0, column=0, sticky="nsew")
        StyleManager.apply_style(header_label, "Header.CTkLabel")

    def _create_hints(self, text):
        # hints_label = ttk.Label(self, text=text, style="Hints.TLabel")
        hints_label = ctk.CTkLabel(self, text=text)
        hints_label.grid(row=1, column=0, sticky="nsew")

    def _create_buttons(
        self, buttons, parent, frame_grid=None, row_weights=None, column_weights=None
    ):
        # Create a button frame using grid
        button_frame = ctk.CTkFrame(parent)
        grid_kwargs = {
            "padx": buttons["frame"].get("padx", 0),
            "pady": buttons["frame"].get("pady", 0),
            "sticky": "nsew",
        }
        grid_kwargs.update(frame_grid or {})
        button_frame.grid(**grid_kwargs)
        StyleManager.apply_style(button_frame, "Transparent.CTkFrame")

        if row_weights:
            for row_index, weight in row_weights:
                button_frame.grid_rowconfigure(row_index, weight=weight)
        if column_weights:
            for column_index, weight in column_weights:
                button_frame.grid_columnconfigure(column_index, weight=weight)

        for button_config in buttons["custom"]:
            button = ctk.CTkButton(
                button_frame,
                text=button_config.get("text", "test"),
                width=button_config.get("width", 200),
                height=button_config.get("height", 40),
                command=button_config.get("command", None),
            )
            button.grid(
                row=button_config.get("row", 0),
                column=button_config.get("column", 0),
                columnspan=button_config.get("columnspan", 1),
                padx=buttons["grid"].get("padx", 0),
                pady=buttons["grid"].get("pady", 0),
            )

            StyleManager.apply_style(button, button_config.get("style", ""))

            # CustomButton(
            #     parent=button_frame,
            #     customization_manager=self.customization_manager,
            #     text=button_config.get("text", "test"),
            #     subtitle_text=button_config.get("subtitle_text", ""),
            #     style=button_config.get("style", "TButton"),
            #     width=button_config.get("width", 350),
            #     height=button_config.get("height", 70),
            #     command=button_config.get("command", None),
            #     accent=button_config.get("accent", False),
            # ).grid(
            #     row=button_config.get("row", 0),
            #     column=button_config.get("column", 0),
            #     columnspan=button_config.get("columnspan", 1),
            #     padx=buttons["grid"].get("padx", 0),
            #     pady=buttons["grid"].get("pady", 0),
            # )

    ctk.set_default_color_theme

    def open_gui(self, gui_class):
        self.customization_manager.reset()
        self.destroy()
        gui = gui_class()
        gui.run()

    def run(self):
        self.mainloop()


class GUI_LaunchScreen(GUI_Base):
    """Launch screen GUI for navigating to primary application features."""

    def __init__(self):
        super().__init__(title=translate("launch_screen_title"))
        self._setup()
        self.adjust_to_content()

        log.info("Launch screen opened.")

    def _setup(self):
        # Place the header in row 0
        self._create_header(text=translate("launch_screen_header"))
        # self.grid_rowconfigure(0, weight=0)  # Header row does not expand

        buttons = {
            "custom": [
                {
                    "text": translate("launch_screen_button_repak"),
                    "style": "Large.CTkButton",
                    "width": 320,
                    "height": 60,
                    "command": self._open_repak_gui,
                    "row": 0,
                    "column": 0,
                },
                {
                    "text": translate("launch_screen_button_merge"),
                    "style": "Large.CTkButton",
                    "width": 320,
                    "height": 60,
                    "command": self._open_merge_gui,
                    "row": 0,
                    "column": 1,
                },
            ],
            "frame": {"padx": 0, "pady": 0},
            "grid": {"padx": 0, "pady": 0},
            # "frame": {"padx": self.padding // 2, "pady": self.padding // 2},
            # "grid": {"padx": self.padding // 2, "pady": self.padding // 2},
        }

        self._create_buttons(
            buttons,
            self,
            frame_grid={"row": 1, "column": 0, "sticky": "nsew"},
            row_weights=[(0, 1)],
            column_weights=[(0, 1), (1, 1)],
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _open_repak_gui(self):
        log.debug("Opening repak screen...")
        self.open_gui(GUI_RepakScreen)

    def _open_merge_gui(self):
        log.debug("Opening merge screen...")
        self.open_gui(GUI_MergeScreen)


class GUI_Secondary(GUI_Base):
    """Secondary GUI window with reusable section-building utilities."""

    def __init__(self, title, resizable):
        super().__init__(title=title, resizable=resizable)

    @property
    def repak_cli(self):
        return settings.TOOLS_PATHS["repak_cli"]

    def create_section(
        self,
        title,
        listbox_name,
        listbox_mode,
        scroll_name,
        add_command,
        remove_command,
        clear_command,
        action_name,
        action_command,
        hints=None,
    ):
        self._create_header(title)
        section_frame = self._create_section_frame()
        # hints_frame = ttk.Frame(section_frame, style="TFrame")
        hints_frame = ctk.CTkFrame(section_frame)
        hints_frame.grid(row=0, column=0, sticky="w", pady=(self.padding, 0))
        StyleManager.apply_style(hints_frame, "Transparent.CTkFrame")
        self._create_hints(hints_frame, hints)
        content_frame = self._create_content_frame(
            section_frame, listbox_name, scroll_name, listbox_mode
        )
        self._create_side_buttons(
            content_frame, add_command, remove_command, clear_command
        )
        self._create_action_button(section_frame, action_name, action_command)

    # def _create_header(self, title):
    #     """Creates the section header."""
    #     header_label = ttk.Label(self, text=title, style="Header.TLabel")
    #     header_label.grid(
    #         row=self._get_next_row(), column=0, sticky="ew", padx=0, pady=(0, 0)
    #     )

    def _create_section_frame(self):
        """Creates the main section frame."""
        # section_frame = ttk.Frame(self, style="TFrame")
        section_frame = ctk.CTkFrame(
            self,
        )
        section_frame.grid(
            row=self._get_next_row(),
            column=0,
            padx=self.padding,
            pady=(0, self.padding // 2),
            sticky="nsew",
        )
        self.grid_columnconfigure(0, weight=1)
        section_frame.grid_columnconfigure(0, weight=1)
        StyleManager.apply_style(section_frame, "Transparent.CTkFrame")
        return section_frame

    def _create_hints(self, section_frame, hints):
        """Adds hints to the section if hints are enabled."""
        if eval(settings.SHOW_HINTS) and hints:
            # hints_label = ttk.Label(section_frame, text=hints, style="Hints.TLabel")
            hints_label = ctk.CTkLabel(section_frame, text=hints)
            hints_label.grid(row=0, column=0, columnspan=3, sticky="ew")

    def _create_content_frame(
        self, section_frame, listbox_name, scroll_name, listbox_mode
    ):
        """Creates the content frame containing the listbox and scrollbar."""
        # content_frame = ttk.Frame(section_frame, style="TFrame")
        content_frame = ctk.CTkFrame(section_frame)
        content_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)
        content_frame.grid_columnconfigure(2, weight=0)
        StyleManager.apply_style(content_frame, "Transparent.CTkFrame")

        # listbox = tk.Listbox(
        listbox = CTkListbox(
            content_frame,
            width=70,
            height=10,
            # bg=settings.THEME_DICT["color_background_highlight"],
            # fg=settings.THEME_DICT["color_foreground"],
            # selectbackground=settings.THEME_DICT["color_highlight"],
            # font=(
            #     settings.THEME_DICT["font_family_code"],
            #     settings.THEME_DICT["font_size_small"],
            #     "normal",
            # ),
            # selectmode=tk.EXTENDED,
            multiple_selection=True,
        )
        listbox.grid(row=0, column=0, sticky="nsew", pady=(self.padding, 0))
        setattr(self, listbox_name, listbox)

        listbox.bind(
            "<Control-v>",
            lambda event: self._paste_clipboard(listbox=listbox, mode=listbox_mode),
        )
        listbox.bind(
            "<Delete>", lambda event: self._remove_from_listbox(listbox=listbox)
        )

        return content_frame

    def _paste_clipboard(self, listbox, mode):
        try:
            clipboard_data = self.clipboard_get()
            paths = clipboard_data.splitlines()

            for item in paths:
                path = Path(item.strip())

                if mode == "pak" and path.is_file() and path.suffix.lower() == ".pak":
                    listbox.insert(path)
                elif mode == "folder" and path.is_dir():
                    listbox.insert(path)
                else:
                    log.debug(f"Invalid path: {path} (Mode: {mode})")
        except Exception as e:
            log.error("Clipboard error:", e)

    def _create_side_buttons(
        self, content_frame, add_command, remove_command, clear_command
    ):
        buttons = {
            "custom": [
                {
                    "text": translate("button_add"),
                    "command": add_command,
                    "width": 130,
                    "height": 50,
                    "row": 1,
                    "column": 0,
                },
                {
                    "text": translate("button_remove"),
                    "command": remove_command,
                    "width": 130,
                    "height": 50,
                    "row": 2,
                    "column": 0,
                },
                {
                    "text": translate("button_clear"),
                    "command": clear_command,
                    "width": 130,
                    "height": 50,
                    "row": 3,
                    "column": 0,
                },
            ],
            "frame": {
                "padx": (self.padding, 0),
                "pady": (self.padding, 0),
            },  # Padding for the button frame
            "grid": {
                "padx": 0,
                "pady": self.padding / 4,
            },  # Padding for individual buttons
        }
        self._create_buttons(
            buttons,
            parent=content_frame,
            frame_grid={"row": 0, "column": 2, "sticky": "ns"},
            row_weights=[(0, 1), (1, 0), (2, 0), (3, 1)],
        )

    def _create_action_button(self, section_frame, action_name, action_command):
        buttons = {
            "custom": [
                {
                    "text": action_name,
                    "command": action_command,
                    "style": "Accent.TButton",
                    "width": 160,
                    "height": 55,
                    "accent": True,
                    "row": 1,
                    "column": 0,
                },
            ],
            "frame": {
                "padx": 0,
                "pady": 0,
            },  # Padding for the button frame
            "grid": {
                "padx": 0,
                "pady": self.padding,
            },  # Padding for individual buttons
        }
        self._create_buttons(
            buttons,
            parent=section_frame,
            frame_grid={"row": 2, "column": 0, "sticky": "n"},
        )

    def _get_next_row(self):
        return len(self.grid_slaves())

    @staticmethod
    def _add_file_to_listbox(listbox):
        files = filedialog.askopenfilenames(
            filetypes=[(translate("dialogue_pak_files"), "*.pak")]
        )
        for file in files:
            # if file not in listbox.get(0, "END"):
            listbox.insert("END", file)
            log.debug(f"Added {file} to {listbox}")

    @staticmethod
    def _add_folder_to_listbox(listbox):
        folder = filedialog.askdirectory()
        if folder:
            listbox.insert(folder)
            log.debug(f"Added {folder} to {listbox}")

    @staticmethod
    def _remove_from_listbox(listbox):
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

    @staticmethod
    def _clear_listbox(listbox):
        listbox.delete("all")
        log.debug(f"Cleared {listbox}")

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
        self.open_launch_screen()

    def open_launch_screen(self):
        log.debug("Opening launch screen...")
        self.open_gui(GUI_LaunchScreen)


class GUI_RepakScreen(GUI_Secondary):
    """GUI for unpacking and repacking files."""

    def __init__(self):
        super().__init__(title=translate("repak_screen_title"), resizable=(True, False))
        self._create_sections()
        self.adjust_to_content(adjust_width=True)

        log.info("Repak screen opened.")

    def _create_sections(self):
        sections = [
            {
                "title": translate("repak_screen_unpack_header"),
                "listbox_name": "unpack_listbox",
                "listbox_mode": "pak",
                "scroll_name": "unpack_scroll",
                "add_command": lambda: self._add_file_to_listbox(self.unpack_listbox),
                "remove_command": lambda: self._remove_from_listbox(
                    self.unpack_listbox
                ),
                "clear_command": lambda: self._clear_listbox(self.unpack_listbox),
                "action_name": translate("repak_screen_unpack_button"),
                "action_command": self._unpack_files,
                "hints": translate("repak_screen_unpack_hints"),
            },
            {
                "title": translate("repak_screen_repack_header"),
                "listbox_name": "repack_listbox",
                "listbox_mode": "folder",
                "scroll_name": "repack_scroll",
                "add_command": lambda: self._add_folder_to_listbox(self.repack_listbox),
                "remove_command": lambda: self._remove_from_listbox(
                    self.repack_listbox
                ),
                "clear_command": lambda: self._clear_listbox(self.repack_listbox),
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
        files = self.unpack_listbox.get()
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
        folders = self.repack_listbox.get()
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
        super().__init__(title=translate("merge_screen_title"), resizable=(True, False))
        self._create_sections()

        self.adjust_to_content(adjust_width=True)
        log.info("Merge screen opened.")

    def _create_sections(self):
        sections = [
            {
                "title": translate("merge_screen_header"),
                "listbox_name": "merge_listbox",
                "listbox_mode": "pak",
                "scroll_name": "merge_scroll",
                "add_command": lambda: self._add_file_to_listbox(self.merge_listbox),
                "remove_command": lambda: self._remove_from_listbox(self.merge_listbox),
                "clear_command": lambda: self._clear_listbox(self.merge_listbox),
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
        files = self.merge_listbox.get()
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
