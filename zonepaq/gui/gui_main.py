import ctypes
import io
import json
import sys
import tempfile
import tkinter as tk
from collections import deque
from concurrent.futures import as_completed
from pathlib import Path
from time import sleep
from tkinter import PhotoImage, filedialog, messagebox, ttk
from unittest.mock import mock_open, patch

import customtkinter as ctk
from backend.logger import handle_exception, log
from backend.repak import Repak
from backend.tools import Files
from config.ctk_themes import CtkStyleManager, ctk_color_theme, get_colors
from config.metadata import APP_ICONS, APP_NAME, APP_VERSION
from config.settings import settings, translate
from config.styles import get_styles
from CTkListbox import *
from gui.gui_toplevel import GUI_ConflictsReport
from gui.menus import MenuRibbon

from tkinterdnd2 import DND_FILES, TkinterDnD


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


class WindowManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent):
        if not hasattr(self, "initialized"):
            self.open_windows = {type(parent): parent}
            # set_app_icon(parent)
            # self.iconpath = tk.PhotoImage(file=resource_path(APP_ICONS["png"]))

            self.initialized = True

    def open_window(self, parent, new_window):
        print(self.open_windows)
        if new_window in self.open_windows:
            window = self.open_windows[new_window]
            parent.withdraw()
            window.deiconify()
        else:
            parent.withdraw()
            window = new_window()
            self.open_windows[new_window] = window
            window.run()

    def close_window(self, parent):
        """Close the current window."""
        if isinstance(parent, GUI_LaunchScreen):
            parent.destroy()
            sys.exit(0)
            # parent.quit()
        else:
            parent.withdraw()
            self.open_windows[type(parent)] = parent


def custom_set_titlebar_icon(self):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(".")
    try:
        resource_path = base_path / APP_ICONS["png"]
        self.iconphoto(True, tk.PhotoImage(file=resource_path))
    except Exception:
        pass


_CTk = ctk.CTk
if hasattr(_CTk, "_windows_set_titlebar_icon"):
    _CTk._windows_set_titlebar_icon = custom_set_titlebar_icon


class CTk(_CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App(CTk):
    def __init__(self):
        super().__init__()
        gui = GUI_LaunchScreen()
        gui.run()


class GUI_Base(CTk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title):
        super().__init__()  # Initialize the ctk.CTk class
        self.window_manager = WindowManager(self)

        self.configure(fg_color=get_colors("color_background_primary"))

        self.report_callback_exception = handle_exception

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")
        self.configure(bg=settings.THEME_DICT["color_background"])
        # set_app_icon(self, self.window_manager.iconpath)

        self.customization_manager = CustomizationManager.get(settings.THEME_DICT)
        # self.customization_manager.instances.register_window(self)

        self.menu = MenuRibbon(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.padding = 20

        theme_str = json.dumps(ctk_color_theme)
        mocked_file = mock_open(read_data=theme_str)
        with patch("builtins.open", mocked_file):
            ctk.set_default_color_theme("mocked_theme")

        ### Alternative ways to load theme:
        ### 1.
        # with tempfile.NamedTemporaryFile(
        #     mode="w", delete=False, suffix=".json"
        # ) as tmp_file:
        #     json.dump(ctk_color_theme, tmp_file)  # Write the JSON data
        #     tmp_file.close()  # Close the file to release the lock
        #     ctk.set_default_color_theme(tmp_file.name)
        ### 2.
        # ctk.set_default_color_theme(Path("zonepaq/config/themes2/Nord.json"))

        CtkStyleManager.define_style(
            "Header.CTkLabel",
            fg_color=get_colors("color_background_tertiary"),
            text_color=get_colors("color_text_accent"),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Header.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Header.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Header.CustomFont"]["weight"],
            ),
        )

        CtkStyleManager.define_style(
            "Hints.CTkLabel",
            fg_color="transparent",
            text_color=get_colors("color_text_muted"),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Hints.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Hints.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Hints.CustomFont"]["weight"],
            ),
        )

        CtkStyleManager.define_style(
            "Dnd.CTkLabel",
            fg_color="transparent",
            text_color=get_colors("color_background_tertiary"),
            # text_color=get_colors("color_text_muted"),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Dnd.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Dnd.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Dnd.CustomFont"]["weight"],
            ),
        )

        CtkStyleManager.define_style(
            "Transparent.CTkFrame",
            fg_color="transparent",
            # border_color="red",
            # border_width=1,
        )

        CtkStyleManager.define_style(
            "Generic.CTkButton",
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        CtkStyleManager.define_style(
            "Action.CTkButton",
            fg_color=get_colors("color_accent_primary"),
            hover_color=get_colors("color_accent_secondary"),
            border_color=get_colors("color_accent_secondary"),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Action.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Action.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Action.Button.CustomFont"]["weight"],
            ),
        )

        CtkStyleManager.define_style(
            "Custom.CTkListbox",
            fg_color="transparent",
            border_color=get_colors("color_background_tertiary"),
            text_color=get_colors("color_text_primary"),
            button_color="transparent",
            hover_color=get_colors("color_accent_tertiary", True),
            highlight_color=get_colors("color_accent_tertiary"),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["List.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["List.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["List.CustomFont"]["weight"],
            ),
        )

    def adjust_to_content(self, root=None, adjust_width=False, adjust_height=False):
        root = root or self

        root.update_idletasks()
        current_width = root.winfo_reqwidth()
        current_height = root.winfo_reqheight()

        def set_minsize(previous_width, previous_height):
            root.minsize(
                min(previous_width, root._current_width),
                min(previous_height, root._current_height),
            )

        root.after(1009, lambda: set_minsize(current_width, current_height))

        root.resizable(adjust_width, adjust_height)

    def on_closing(self):
        # self.customization_manager.reset()
        self.window_manager.close_window(self)

    @staticmethod
    def _create_ctk_widget(
        ctk_widget,
        widget_args,
        widget_style=None,
        grid_args=None,
        row_weights=None,
        column_weights=None,
    ):
        widget = ctk_widget(**widget_args)
        if widget_style:
            CtkStyleManager.apply_style(widget, widget_style)
        widget.grid(**grid_args)
        if row_weights:
            for row_index, weight in row_weights:
                widget.grid_rowconfigure(row_index, weight=weight)
        if column_weights:
            for column_index, weight in column_weights:
                widget.grid_columnconfigure(column_index, weight=weight)
        return widget

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
            grid_args={"row": 0, "column": 0, "sticky": "nsew"},
            row_weights=None,
            column_weights=None,
        )

    def _create_buttons(
        self,
        buttons,
        parent,
        frame_grid_args=None,
        row_weights=None,
        column_weights=None,
    ):
        button_frame = self._create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args={"master": parent},
            widget_style="Transparent.CTkFrame",
            grid_args={**frame_grid_args},
            row_weights=row_weights,
            column_weights=column_weights,
        )

        for button_config in buttons["custom"]:
            self._create_ctk_widget(
                ctk_widget=ctk.CTkButton,
                widget_args={
                    "master": button_frame,
                    "text": button_config.get("text", "test"),
                    "width": button_config.get("width", 0),
                    "height": button_config.get("height", 0),
                    "command": button_config.get("command", None),
                },
                widget_style=button_config.get("style", "Generic.CTkButton"),
                grid_args={
                    "row": button_config.get("row", 0),
                    "column": button_config.get("column", 0),
                    "columnspan": button_config.get("columnspan", 1),
                    "rowspan": button_config.get("rowspan", 1),
                    "sticky": buttons["grid"].get("sticky", ""),
                    "padx": buttons["grid"].get("padx", 0),
                    "pady": buttons["grid"].get("pady", 0),
                },
                row_weights=None,
                column_weights=None,
            )

    def open_gui(self, gui_class):
        # self.customization_manager.reset()
        log.debug(f"Opening {gui_class}...")
        self.window_manager.open_window(self, gui_class)

    def run(self):
        self.mainloop()


class GUI_LaunchScreen(GUI_Base):
    """Launch screen GUI for navigating to primary application features."""

    def __init__(self):
        super().__init__(title=translate("launch_screen_title"))
        self._setup2()
        self.adjust_to_content()

        log.info("Launch screen opened.")

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
            grid_args={
                "row": 0,
                "column": 0,
                "sticky": "nsew",
            },
            column_weights=None,
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
                    "accent": True,
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
                        log.debug(f"Added {str(path)} to {listbox}")
                    elif mode == "folder" and path.is_dir():
                        listbox.insert("END", str(path))
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
                log.debug(f"Added {str(file)} to {listbox}")
        if listbox.get("all"):
            dnd.grid_forget()

    def _add_folder_to_listbox(self, listbox, dnd):
        folder = filedialog.askdirectory()
        if folder:
            folder = Path(folder.strip())
            if str(folder) not in listbox.get("all"):
                listbox.insert("END", str(folder))
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

        self.adjust_to_content(adjust_width=True)
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
