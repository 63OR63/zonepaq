import json
from unittest.mock import mock_open, patch

import customtkinter as ctk
from backend.logger import handle_exception, log
from config.themes import StyleManager, ThemeManager
from config.metadata import APP_NAME, APP_VERSION
from config.settings import settings
from gui.custom_set_titlebar_icon import CTk
from gui.window_manager import WindowManager


class GUI_Base(CTk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title):
        super().__init__()  # Initialize the ctk.CTk class wrapper

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")

        self.window_manager = WindowManager(self)
        self.theme_manager = ThemeManager
        self.style_manager = StyleManager

        self.restyle()

        self.report_callback_exception = handle_exception

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        from gui.menus import MenuRibbon

        self.menu = MenuRibbon(self)

        self.padding = 20

    def restyle(self, color_palette=settings.THEME_NAME):
        log.debug(f"Applying {color_palette} color theme...")

        self.color_theme = self.theme_manager.merge_dicts(
            self.theme_manager.construct_color_theme(color_palette),
            self.theme_manager.borders_definitions,
            self.theme_manager.font_definitions,
            self.theme_manager.dimensions_definitions,
        )

        self.configure(
            fg_color=self.theme_manager.get_colors(
                "color_background_primary", color_palette
            )
        )

        self.apply_color_theme(self.color_theme)

        self.style_manager.define_custom_styles(color_palette)

        log.debug(f"Color theme {color_palette} applied")

    def apply_color_theme(self, color_theme):
        ### Using mocked file
        theme_str = json.dumps(color_theme)
        mocked_file = mock_open(read_data=theme_str)
        with patch("builtins.open", mocked_file):
            ctk.set_default_color_theme("mocked_theme")

        ### Using temp file
        # with tempfile.NamedTemporaryFile(
        #     mode="w", delete=False, suffix=".json"
        # ) as tmp_file:
        #     json.dump(self.color_theme, tmp_file)  # Write the JSON data
        #     tmp_file.close()  # Close the file to release the lock
        #     ctk.set_default_color_theme(tmp_file.name)

        ### Using predefined .json file
        # ctk.set_default_color_theme(Path(f"zonepaq/config/themes/{color_theme}.json"))

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

    def create_ctk_widget(
        self,
        ctk_widget,
        widget_args,
        widget_style=None,
        grid_args=None,
        row_weights=None,
        column_weights=None,
    ):
        widget = ctk_widget(**widget_args)
        if widget_style:
            StyleManager.apply_style(widget, widget_style)
        widget.grid(**grid_args)
        if row_weights:
            for row_index, weight in row_weights:
                widget.grid_rowconfigure(row_index, weight=weight)
        if column_weights:
            for column_index, weight in column_weights:
                widget.grid_columnconfigure(column_index, weight=weight)
        return widget

    def create_header(self, master, text="", row="current", column="current"):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        return self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": text,
                "anchor": "center",
                "pady": self.padding,
            },
            widget_style="Header.CTkLabel",
            grid_args={
                "row": self._get_next_row(master),
                "column": 0,
                "columnspan": 999,
                "sticky": "nsew",
            },
            row_weights=None,
            column_weights=None,
        )

    def create_subheader(self, master, text="", row="current", column="current"):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        return self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": text,
                "anchor": "w",
                "padx": self.padding,
                "pady": self.padding / 2,
            },
            widget_style="SubHeader.CTkLabel",
            grid_args={
                "row": row,
                "column": column,
                "columnspan": 999,
                "sticky": "nsew",
            },
            row_weights=None,
            column_weights=None,
        )

    def create_frame(
        self,
        master,
        style="Transparent.CTkFrame",
        row="current",
        column="current",
        rowspan=1,
        columnspan=999,
        sticky="nsew",
        padx=0,
        pady=0,
        row_weights=None,
        column_weights=None,
        **kwargs,
    ):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        widget_args = {"master": master}

        widget_args.update(kwargs)

        return self.create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args=widget_args,
            widget_style=style,
            grid_args={
                "row": row,
                "column": column,
                "rowspan": rowspan,
                "columnspan": columnspan,
                "sticky": sticky,
                "padx": padx,
                "pady": pady,
            },
            row_weights=row_weights,
            column_weights=column_weights,
        )

    def create_spacer(
        self,
        master,
        style="Transparent.CTkFrame",
        row="current",
        column=0,
        rowspan=1,
        columnspan=999,
        sticky="nsew",
        padx=0,
        pady=0,
        row_weights=None,
        column_weights=None,
        **kwargs,
    ):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        widget_args = {"master": master, "height": self.padding / 2}

        widget_args.update(kwargs)

        return self.create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args=widget_args,
            widget_style=style,
            grid_args={
                "row": row,
                "column": column,
                "rowspan": rowspan,
                "columnspan": columnspan,
                "sticky": sticky,
                "padx": padx,
                "pady": pady,
            },
            row_weights=row_weights,
            column_weights=column_weights,
        )

    def create_hints(self, master, hints, row="current", column=0):
        if eval(settings.SHOW_HINTS) and hints:
            if row == "current":
                row = self._get_next_row(master)
            elif isinstance(row, str) and row.startswith(("+", "-")):
                row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

            if column == "current":
                column = self._get_next_column(master)
            elif isinstance(row, str) and row.startswith(("+", "-")):
                column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

            self.create_ctk_widget(
                ctk_widget=ctk.CTkLabel,
                widget_args={
                    "master": master,
                    "text": hints,
                    "justify": "left",
                },
                widget_style="Hints.CTkLabel",
                grid_args={
                    "row": row,
                    "column": column,
                    "sticky": "nw",
                    "padx": self.padding,
                    "pady": (self.padding, 0),
                },
                row_weights=[(0, 0)],
                column_weights=None,
            )

    def _get_next_row(self, root=None):
        root = root or self
        return len(root.grid_slaves())

    def _get_next_column(self, root=None):
        root = root or self
        columns = set()
        for widget in root.grid_slaves():
            col = widget.grid_info().get("column")
            if col is not None:
                columns.add(int(col))
        return max(columns, default=0)

    def create_button(
        self,
        master,
        text="",
        width=None,
        height=None,
        command=None,
        style="Generic.CTkButton",
        row="current",
        column="current",
        rowspan=1,
        columnspan=1,
        sticky="",
        padx=0,
        pady=0,
        row_weights=None,
        column_weights=None,
        **kwargs,
    ):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        widget_args = {
            "master": master,
            "text": text,
            "command": command,
        }

        if width:
            widget_args[width] = width
        if height:
            widget_args[height] = height

        widget_args.update(kwargs)

        self.create_ctk_widget(
            ctk_widget=ctk.CTkButton,
            widget_args=widget_args,
            widget_style=style,
            grid_args={
                "row": row,
                "column": column,
                "rowspan": rowspan,
                "columnspan": columnspan,
                "sticky": sticky,
                "padx": padx,
                "pady": pady,
            },
            row_weights=row_weights,
            column_weights=column_weights,
        )

    def create_buttons(
        self,
        buttons,
        parent,
        frame_grid_args=None,
        row_weights=None,
        column_weights=None,
    ):
        button_frame = self.create_ctk_widget(
            ctk_widget=ctk.CTkFrame,
            widget_args={"master": parent},
            widget_style="Transparent.CTkFrame",
            grid_args={**frame_grid_args},
            row_weights=row_weights,
            column_weights=column_weights,
        )

        for button_config in buttons["custom"]:
            self.create_ctk_widget(
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

    def open_gui(self, gui_class, toplevel=False):
        # self.customization_manager.reset()
        log.debug(f"Opening {gui_class}...")
        self.window_manager.open_window(
            parent=self, new_window=gui_class, toplevel=toplevel
        )
