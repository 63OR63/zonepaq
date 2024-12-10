import logging
import sys
import tkinter as tk
import traceback
from collections import deque
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from backend.tools import Files, Repak
from config.metadata import APP_NAME
from config.settings import settings, translate
from gui.gui_toplevel import GUI_ConflictsReport
from gui.menus import MenuRibbon
from gui.widgets import CustomButton, set_app_icon


class InstanceManager:
    """Manages registration and cleanup of windows and widgets."""

    def __init__(self):
        self._reset()

    def register_window(self, window):
        if window not in self.windows:
            logging.debug(f"Registering window: {window}")
            self.windows.append(window)

    def unregister_window(self, window):
        if window in self.windows:
            logging.debug(f"Unregistering window: {window}")
            self.windows.remove(window)

        for widget in list(self.widgets.keys()):
            if self.widgets[widget] == window:
                logging.debug(f"Unregistering widget: {widget} @ {window}")
                self.widgets.pop(widget)

    def register_widget(self, widget, window):
        if widget not in self.widgets:
            logging.debug(f"Registering widget: {widget} @ {window}")
            self.widgets[widget] = window

    def _reset(self):
        logging.debug("'windows' and 'widgets' instance storages reset.")
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
        logging.debug("'CustomizationManager' instance cleared.")
        CustomizationManager._instance = None

    def apply_theme(self, window, theme_name):
        settings.update_config("SETTINGS", "THEME_NAME", theme_name)

        self._reload_styles(settings.THEME_DICT)

        for widget in self.instances.widgets:
            widget.apply_style()

        for window in self.instances.windows:
            self._apply_specific_styles(window)

    def apply_translation(self, window, lang_name):
        settings.update_config("SETTINGS", "LANG_NAME", lang_name)

        self.reset()

        window.destroy()
        gui = GUI_LaunchScreen()
        gui.run()

    def apply_show_hints(self, window, show_hints):
        settings.SHOW_HINTS = str(show_hints)
        settings.update_config("SETTINGS", "SHOW_HINTS", show_hints)

        self.reset()

        window.destroy()
        gui = GUI_LaunchScreen()
        gui.run()

    def _reload_styles(self, theme_dict):
        styles = {
            "TFrame": {
                "background": theme_dict["color_background"],
            },
            # "TFrame": {
            #     "background": theme_dict["color_background"],
            #     "borderwidth": 1, "relief": "solid",
            # },  # Visual Debug
            "TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_normal"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
            },
            "Small.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
            },
            "Success.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_success"],
            },
            "Attention.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_attention"],
            },
            "Warning.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_warning"],
            },
            "Error.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_error"],
            },
            "Hints.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_muted"],
            },
            "Header.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_header"],
                    "bold",
                ),
                "background": theme_dict["color_highlight"],
                "foreground": theme_dict["color_contrast"],
                "anchor": "center",
                "padding": (0, 15),
            },
            "SettingsItem.TLabel": {
                "font": (
                    theme_dict["font_family_code"],
                    theme_dict["font_size_normal"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
                "anchor": "center",
            },
            "TButton": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_normal"],
                ),
                "background": theme_dict["color_background_accent"],
                "foreground": theme_dict["color_foreground"],
                "relief": "flat",
                "borderwidth": 0,
                "padding": 10,
            },
            "Subtitle.TButton": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                    "italic",
                ),
                "foreground": theme_dict["color_muted"],
                "background": theme_dict["color_background_muted"],
                "relief": "flat",
                "borderwidth": 0,
            },
            "Accent.TButton": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_normal"],
                    "bold",
                ),
                "background": theme_dict["color_accent"],
                "foreground": theme_dict["color_contrast"],
                "relief": "flat",
                "borderwidth": 0,
            },
            "SettingsGroup.TLabel": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_normal"],
                    "bold",
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_contrast"],
            },
            "PathEntry.TEntry": {
                "font": (theme_dict["font_family_code"], theme_dict["font_size_small"]),
                "background": theme_dict["color_background_highlight"],
                "foreground": theme_dict["color_foreground"],
            },
            "PathInvalid.TEntry": {
                "font": (theme_dict["font_family_code"], theme_dict["font_size_small"]),
                "background": theme_dict["color_error"],
                "foreground": theme_dict["color_contrast"],
            },
            "Treeview": {
                "font": (
                    theme_dict["font_family_code"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
                "fieldbackground": theme_dict["color_background"],
            },
            "Muted.Treeview": {
                "font": (
                    theme_dict["font_family_code"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_muted"],
                "fieldbackground": theme_dict["color_background"],
            },
            "Treeview.Heading": {
                "font": (
                    theme_dict["font_family_code"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
            },
            "Vertical.TScrollbar": {
                "background": theme_dict["color_background"],
                "troughcolor": theme_dict["color_background_muted"],
            },
            "TCheckbutton": {
                "font": (
                    theme_dict["font_family_main"],
                    theme_dict["font_size_small"],
                ),
                "background": theme_dict["color_background"],
                "foreground": theme_dict["color_foreground"],
            },
        }
        for widget, config in styles.items():
            self.style.configure(widget, **config)

        self.style.map(
            "TCheckbutton",
            background=[
                ("active", theme_dict["color_background"]),
                ("!active", theme_dict["color_background"]),
            ],
        )
        self.style.map(
            "Treeview.Heading",
            background=[
                ("active", theme_dict["color_background"]),
                ("!active", theme_dict["color_background"]),
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
                        except tk.TclError:
                            pass
                elif isinstance(current_widget, ttk.Treeview):
                    for tag, style in treeview_tags.items():
                        try:
                            current_widget.tag_configure(tag, **style)
                        except tk.TclError:
                            pass
                else:
                    for key, value in generic.items():
                        try:
                            if hasattr(current_widget, "configure"):
                                current_widget.configure({key: value})
                        except tk.TclError:
                            pass

            queue.extend(current_widget.winfo_children())


class GUI_Base(tk.Tk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title, width=800, height=350, resizable=(False, False)):
        super().__init__()  # Initialize the tk.Tk class

        self.report_callback_exception = self._custom_error_handler

        self.title(f"{APP_NAME} - {title}")
        self.configure(bg=settings.THEME_DICT["color_background"])
        set_app_icon(self)
        self.customization_manager = CustomizationManager.get(settings.THEME_DICT)
        self.customization_manager.instances.register_window(self)

        self.menu = MenuRibbon(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.padding = 30

    def __del__(self):
        self.customization_manager.instances.unregister_window(self)

    def _custom_error_handler(self, exc_type, exc_value, exc_traceback):
        self.destroy()
        error_message = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        messagebox.showerror(
            "Application Error", f"An error occurred:\n{error_message}"
        )
        sys.exit(1)

    def adjust_to_content(self, root=None, adjust_width=False, adjust_height=False):
        root = root or self
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.resizable(adjust_width, adjust_height)

    def on_closing(self):
        self.customization_manager.reset()
        self.destroy()

    def _create_header(self, text):
        header_label = ttk.Label(self, text=text, style="Header.TLabel")
        header_label.grid(row=0, column=0, sticky="nsew")

    def _create_hints(self, text):
        hints_label = ttk.Label(self, text=text, style="Hints.TLabel")
        hints_label.grid(row=1, column=0, sticky="nsew")

    def _create_buttons(self, buttons, parent, frame_grid=None, row_weights=None):
        # Create a button frame using grid
        button_frame = ttk.Frame(parent, style="TFrame")
        grid_kwargs = {
            "padx": buttons["frame"].get("padx", 0),
            "pady": buttons["frame"].get("pady", 0),
            "sticky": "nsew",
        }
        grid_kwargs.update(frame_grid or {})
        button_frame.grid(**grid_kwargs)

        if row_weights:
            for row_index, weight in row_weights:
                button_frame.grid_rowconfigure(row_index, weight=weight)

        for button_config in buttons["custom"]:
            CustomButton(
                parent=button_frame,
                customization_manager=self.customization_manager,
                text=button_config.get("text", "test"),
                subtitle_text=button_config.get("subtitle_text", ""),
                style=button_config.get("style", "TButton"),
                width=button_config.get("width", 350),
                height=button_config.get("height", 70),
                command=button_config.get("command", None),
                accent=button_config.get("accent", False),
            ).grid(
                row=button_config.get("row", 0),
                column=button_config.get("column", 0),
                columnspan=button_config.get("columnspan", 1),
                padx=buttons["grid"].get("padx", 0),
                pady=buttons["grid"].get("pady", 0),
            )

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

    def _setup(self):
        # Place the header in row 0
        self._create_header(text=translate("launch_screen_header"))
        self.grid_rowconfigure(0, weight=0)  # Header row does not expand

        buttons = {
            "custom": [
                {
                    "text": translate("launch_screen_button_repak"),
                    "command": self._open_repak_gui,
                    "row": 0,
                    "column": 0,
                },
                {
                    "text": translate("launch_screen_button_merge"),
                    "command": self._open_merge_gui,
                    "row": 0,
                    "column": 1,
                },
            ],
            "frame": {"padx": self.padding // 2, "pady": self.padding // 2},
            "grid": {"padx": self.padding // 2, "pady": self.padding // 2},
        }

        self._create_buttons(
            buttons, self, frame_grid={"row": 1, "column": 0, "sticky": "nsew"}
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _open_repak_gui(self):
        self.open_gui(GUI_RepakScreen)

    def _open_merge_gui(self):
        self.open_gui(GUI_MergeScreen)


class GUI_Secondary(GUI_Base):
    """Secondary GUI window with reusable section-building utilities."""

    def __init__(self, title, resizable):
        super().__init__(title=title, resizable=resizable)

    def create_section(
        self,
        title,
        listbox_name,
        scroll_name,
        add_command,
        clear_command,
        action_name,
        action_command,
        hints=None,
    ):
        self._create_header(title)
        section_frame = self._create_section_frame()
        hints_frame = ttk.Frame(section_frame, style="TFrame")
        hints_frame.grid(row=0, column=0, sticky="w", pady=(self.padding, 0))
        self._create_hints(hints_frame, hints)
        content_frame = self._create_content_frame(
            section_frame, listbox_name, scroll_name
        )
        self._create_side_buttons(content_frame, add_command, clear_command)
        self._create_action_button(section_frame, action_name, action_command)

    def _create_header(self, title):
        """Creates the section header."""
        header_label = ttk.Label(self, text=title, style="Header.TLabel")
        header_label.grid(
            row=self._get_next_row(), column=0, sticky="ew", padx=0, pady=(0, 0)
        )

    def _create_section_frame(self):
        """Creates the main section frame."""
        section_frame = ttk.Frame(self, style="TFrame")
        section_frame.grid(
            row=self._get_next_row(),
            column=0,
            padx=self.padding,
            pady=(0, self.padding // 2),
            sticky="nsew",
        )
        self.grid_columnconfigure(0, weight=1)
        section_frame.grid_columnconfigure(0, weight=1)
        return section_frame

    def _create_hints(self, section_frame, hints):
        """Adds hints to the section if hints are enabled."""
        if eval(settings.SHOW_HINTS) and hints:
            hints_label = ttk.Label(section_frame, text=hints, style="Hints.TLabel")
            hints_label.grid(row=0, column=0, columnspan=3, sticky="ew")

    def _create_content_frame(self, section_frame, listbox_name, scroll_name):
        """Creates the content frame containing the listbox and scrollbar."""
        content_frame = ttk.Frame(section_frame, style="TFrame")
        content_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)
        content_frame.grid_columnconfigure(2, weight=0)

        listbox = tk.Listbox(
            content_frame,
            width=70,
            height=10,
            bg=settings.THEME_DICT["color_background_highlight"],
            fg=settings.THEME_DICT["color_foreground"],
            selectbackground=settings.THEME_DICT["color_highlight"],
            font=(
                settings.THEME_DICT["font_family_code"],
                settings.THEME_DICT["font_size_small"],
                "normal",
            ),
            selectmode=tk.NONE,
        )
        listbox.grid(row=0, column=0, sticky="nsew", pady=(self.padding, 0))
        setattr(self, listbox_name, listbox)

        def _disable_selection(event):
            return "break"

        listbox.bind(
            "<<ListboxSelect>>", _disable_selection
        )  # Prevent selection events
        listbox.bind(
            "<Button-1>", _disable_selection
        )  # Disable mouse clicks for selection
        listbox.bind("<B1-Motion>", _disable_selection)  # Prevent dragging to select

        scrollbar = ttk.Scrollbar(
            content_frame, orient=tk.VERTICAL, command=listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns", pady=(self.padding, 0))
        listbox.config(yscrollcommand=scrollbar.set)
        setattr(self, scroll_name, scrollbar)

        return content_frame

    def _create_side_buttons(self, content_frame, add_command, clear_command):
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
                    "text": translate("button_clear"),
                    "command": clear_command,
                    "width": 130,
                    "height": 50,
                    "row": 2,
                    "column": 0,
                },
            ],
            "frame": {
                "padx": (self.padding, 0),
                "pady": (self.padding, 0),
            },  # Padding for the button frame
            "grid": {
                "padx": 0,
                "pady": self.padding / 2,
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
            if file not in listbox.get(0, tk.END):
                listbox.insert(tk.END, file)

    @staticmethod
    def _clear_files_from_listbox(listbox):
        listbox.delete(0, tk.END)

    @staticmethod
    def _add_folder_to_listbox(listbox):
        folder = filedialog.askdirectory()
        if folder:
            listbox.insert(tk.END, folder)

    @staticmethod
    def _clear_folders_from_listbox(listbox):
        listbox.delete(0, tk.END)

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
        self.open_gui(GUI_LaunchScreen)


class GUI_RepakScreen(GUI_Secondary):
    """GUI for unpacking and repacking files."""

    def __init__(self):
        super().__init__(title=translate("repak_screen_title"), resizable=(True, False))
        self._create_sections()
        self.adjust_to_content(adjust_width=True)

    def _create_sections(self):
        sections = [
            {
                "title": translate("repak_screen_unpack_header"),
                "listbox_name": "unpack_listbox",
                "scroll_name": "unpack_scroll",
                "add_command": lambda: self._add_file_to_listbox(self.unpack_listbox),
                "clear_command": lambda: self._clear_files_from_listbox(
                    self.unpack_listbox
                ),
                "action_name": translate("repak_screen_unpack_button"),
                "action_command": self._unpack_files,
                "hints": translate("repak_screen_unpack_hints"),
            },
            {
                "title": translate("repak_screen_repack_header"),
                "listbox_name": "repack_listbox",
                "scroll_name": "repack_scroll",
                "add_command": lambda: self._add_folder_to_listbox(self.repack_listbox),
                "clear_command": lambda: self._clear_pa_clear_folders_from_listboxk_files(
                    self.repack_listbox
                ),
                "action_name": translate("repak_screen_repack_button"),
                "action_command": self._repack_folders,
                "hints": translate("repak_screen_repack_hints"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def _unpack_files(self):
        files = self.unpack_listbox.get(0, tk.END)
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
                for file in files:
                    file = Path(file)
                    success, result = Repak.unpack(file, folder)
                    if success:
                        results_ok.append(f"Unpacked {file} to: {result}")
                    else:
                        results_ko.append(f"Error unpacking {file}: {result}")
                self.show_results(results_ok, results_ko)

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repak_screen_unpack_msg_empty_list"),
            )

    def _repack_folders(self):
        folders = self.repack_listbox.get(0, tk.END)
        if folders:
            target_folder = filedialog.askdirectory()
            if target_folder:
                target_folder = Path(target_folder)
                results_ok = []
                results_ko = []

                for folder in folders:
                    folder = Path(folder)
                    success, result = Repak.repack(folder, target_folder)
                    if success:
                        results_ok.append(f"Repacked {folder} into: {result}")
                    else:
                        results_ko.append(f"Error repacking {folder}: {result}")

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

    def _create_sections(self):
        sections = [
            {
                "title": translate("merge_screen_header"),
                "listbox_name": "merge_listbox",
                "scroll_name": "merge_scroll",
                "add_command": lambda: self._add_file_to_listbox(self.merge_listbox),
                "clear_command": lambda: self._clear_files_from_listbox(
                    self.merge_listbox
                ),
                "action_name": translate("merge_screen_analyze_button"),
                "action_command": self._find_conflicts,
                "hints": translate("merge_screen_hints"),
            },
        ]
        for section in sections:
            self.create_section(**section)

    def _find_conflicts(self):
        files = self.merge_listbox.get(0, tk.END)
        if files:
            results_ok = {}
            results_ko = {}
            for file in files:
                file = Path(file)
                success, result = Repak.get_list(file)
                if success:
                    results_ok[file.as_posix()] = result
                else:
                    results_ko[str(file)] = result

            content_tree = Files.build_content_tree(results_ok)

            GUI_ConflictsReport(parent=self, content_tree=content_tree)

        else:
            messagebox.showwarning(
                translate("generic_warning"),
                translate("repack_screen_repack_msg_empty_list"),
            )
