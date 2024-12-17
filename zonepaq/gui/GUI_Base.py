import json
from unittest.mock import mock_open, patch

import customtkinter as ctk
from backend.logger import handle_exception, log
from config.ctk_themes import ThemeManager, StyleManager
from config.metadata import APP_NAME, APP_VERSION
from config.settings import settings
from gui.custom_set_titlebar_icon import CTk

# from gui.CustomizationManager import CustomizationManager
from gui.WindowManager import WindowManager


class GUI_Base(CTk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title):
        super().__init__()  # Initialize the ctk.CTk class

        self.window_manager = WindowManager(self)
        self.theme_manager = ThemeManager
        self.style_manager = StyleManager

        # self.customization_manager = CustomizationManager.get(
        #     settings.THEME_DICT
        # )  # !DELETEME
        # self.customization_manager.instances.register_window(self)

        self.color_palette = settings.THEME_NAME
        self.color_theme = self.theme_manager.merge_dicts(
            self.theme_manager.construct_color_theme(self.color_palette),
            self.theme_manager.borders_definitions,
            self.theme_manager.font_definitions,
            self.theme_manager.dimensions_definitions,
        )

        self.configure(
            fg_color=self.theme_manager.get_colors(
                "color_background_primary", self.color_palette
            )
        )

        self.report_callback_exception = handle_exception

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")
        # self.configure(bg=settings.THEME_DICT["color_background"])
        # set_app_icon(self, self.window_manager.iconpath)

        from gui.menus import MenuRibbon

        self.menu = MenuRibbon(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.padding = 20

        self.apply_color_theme()

        self.style_manager.define_style(
            "Header.CTkLabel",
            fg_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            text_color=self.theme_manager.get_colors(
                "color_text_primary", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Header.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Header.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Header.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "SubHeader.CTkLabel",
            fg_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            text_color=self.theme_manager.get_colors(
                "color_text_primary", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["SubHeader.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["SubHeader.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["SubHeader.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Hints.CTkLabel",
            fg_color="transparent",
            text_color=self.theme_manager.get_colors(
                "color_text_muted", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Hints.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Hints.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Hints.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Dnd.CTkLabel",
            fg_color="transparent",
            text_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            # text_color=self.theme_manager.get_colors("color_text_muted", self.color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Dnd.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Dnd.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Dnd.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Transparent.CTkFrame",
            fg_color="transparent",
            # border_color="red",
            # border_width=1,
        )

        self.style_manager.define_style(
            "Primary.CTkFrame",
            fg_color=self.theme_manager.get_colors(
                "color_background_primary", self.color_palette
            ),
            # border_color="red",
            # border_width=1,
        )

        self.style_manager.define_style(
            "Secondary.CTkFrame",
            fg_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            # border_color="red",
            # border_width=1,
        )

        self.style_manager.define_style(
            "Tertiary.CTkFrame",
            fg_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            # border_color="red",
            # border_width=1,
        )

        self.style_manager.define_style(
            "Generic.CTkButton",
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Action.CTkButton",
            fg_color=self.theme_manager.get_colors(
                "color_accent_primary", self.color_palette
            ),
            hover_color=self.theme_manager.get_colors(
                "color_accent_secondary", self.color_palette
            ),
            border_color=self.theme_manager.get_colors(
                "color_accent_secondary", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Action.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Action.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Action.Button.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Muted.CTkButton",
            fg_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            hover_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            border_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Alt.CTkEntry",
            fg_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            border_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            text_color=self.theme_manager.get_colors(
                "color_text_primary", self.color_palette
            ),
            placeholder_text_color=self.theme_manager.get_colors(
                "color_text_muted", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Entry.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Entry.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Entry.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "AltError.CTkEntry",
            fg_color=self.theme_manager.get_colors(
                "color_background_secondary", self.color_palette
            ),
            border_color=self.theme_manager.get_colors(
                "color_error", self.color_palette
            ),
            text_color=self.theme_manager.get_colors(
                "color_text_primary", self.color_palette
            ),
            placeholder_text_color=self.theme_manager.get_colors(
                "color_text_muted", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Entry.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Entry.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Entry.CustomFont"]["weight"],
            ),
        )

        self.style_manager.define_style(
            "Custom.CTkListbox",
            fg_color="transparent",
            border_color=self.theme_manager.get_colors(
                "color_background_tertiary", self.color_palette
            ),
            text_color=self.theme_manager.get_colors(
                "color_text_primary", self.color_palette
            ),
            button_color="transparent",
            hover_color=self.theme_manager.get_colors(
                "color_accent_tertiary", self.color_palette, True
            ),
            highlight_color=self.theme_manager.get_colors(
                "color_accent_tertiary", self.color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["List.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["List.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["List.CustomFont"]["weight"],
            ),
        )

    def apply_color_theme(self):
        theme_str = json.dumps(self.color_theme)
        mocked_file = mock_open(read_data=theme_str)
        with patch("builtins.open", mocked_file):
            ctk.set_default_color_theme("mocked_theme")

        ### Alternative ways to load theme:
        ### 1.
        # with tempfile.NamedTemporaryFile(
        #     mode="w", delete=False, suffix=".json"
        # ) as tmp_file:
        #     json.dump(self.color_theme, tmp_file)  # Write the JSON data
        #     tmp_file.close()  # Close the file to release the lock
        #     ctk.set_default_color_theme(tmp_file.name)
        ### 2.
        # ctk.set_default_color_theme(Path("zonepaq/config/themes2/Nord.json"))

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
