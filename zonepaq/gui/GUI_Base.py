import json
from unittest.mock import mock_open, patch

import customtkinter as ctk
from backend.logger import handle_exception, log
from config.ctk_themes import CtkStyleManager, ctk_color_theme, get_colors
from config.metadata import APP_NAME, APP_VERSION
from config.settings import settings
from gui.custom_set_titlebar_icon import CTk
from gui.CustomizationManager import CustomizationManager
from gui.WindowManager import WindowManager


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

        from gui.menus import MenuRibbon

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
            border_color="red",
            border_width=1,
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
            grid_args={"row": 0, "column": 0, "columnspan": 999, "sticky": "nsew"},
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

    def open_gui(self, gui_class, toplevel=False):
        # self.customization_manager.reset()
        log.debug(f"Opening {gui_class}...")
        self.window_manager.open_window(
            parent=self, new_window=gui_class, toplevel=toplevel
        )
