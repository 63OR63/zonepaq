from backend.logger import handle_exception, log
from backend.games_manager import GamesManager
from backend.utilities import Files
from backend.tools_manager import ToolsManager
from config import metadata
from config.settings import SettingsManager
from config.metadata import APP_NAME, APP_VERSION
from config.themes import StyleManager, ThemeManager
from gui.ctk_wraps import CTk
import customtkinter as ctk


import json
from unittest.mock import mock_open, patch

from gui.window_settings import WindowSettings

# Get SettingsManager class
settings = SettingsManager()


class TemplateBase(CTk):
    """Base class for all GUI windows with common functionalities."""

    def __init__(self, title):
        super().__init__()  # Initialize the ctk.CTk class wrapper

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")

        self.games_manager = GamesManager()
        self.tools_manager = ToolsManager()
        self.theme_manager = ThemeManager
        self.style_manager = StyleManager

        self.padding = 20

        self._restyle()

        self.report_callback_exception = handle_exception

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        raise NotImplementedError("Subclasses must implement the 'on_closing' method.")

    def _restyle(self, color_palette=settings.THEME_NAME):
        log.debug(f"Applying {color_palette} color theme...")

        self.color_theme = self.theme_manager.merge_dicts(
            self.theme_manager.construct_color_theme(color_palette),
            self.theme_manager.borders_definitions,
            self.theme_manager.font_definitions,
            self.theme_manager.dimensions_definitions,
        )

        self.apply_color_theme(self.color_theme)

        if eval(settings.DARK_MODE):
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

        self.style_manager.define_custom_styles(color_palette)

        self.cog_image = self.create_image_for_button(
            metadata.APP_ICONS["mdi-cog"], color_palette, hover=False
        )
        self.cog_image_hover = self.create_image_for_button(
            metadata.APP_ICONS["mdi-cog"], color_palette, hover=True
        )
        self.help_image = self.create_image_for_button(
            metadata.APP_ICONS["mdi-help"], color_palette, hover=False
        )
        self.help_image_hover = self.create_image_for_button(
            metadata.APP_ICONS["mdi-help"], color_palette, hover=True
        )

        self.configure(
            fg_color=self.theme_manager.get_colors(
                "color_background_primary", color_palette
            )
        )

        log.debug(f"Color theme {color_palette} applied")

    def create_image_for_button(self, img, color_palette, hover=False):
        color_type = "color_accent_quaternary" if hover else "color_accent_tertiary"
        colors = self.theme_manager.get_colors(color_type, color_palette)
        light_color, dark_color = colors[0], colors[1]

        def themed_image(img, color):
            base_path = Files.get_base_path() / img
            return self.theme_manager.colorize_mask(base_path, color)

        return ctk.CTkImage(
            light_image=themed_image(img, light_color),
            dark_image=themed_image(img, dark_color),
            size=(self.padding * 1.5, self.padding * 1.5),
        )

    def create_header_button(self, master, command, image, image_hover, sticky):
        button = self.create_ctk_widget(
            ctk_widget=ctk.CTkButton,
            widget_args={
                "master": self.get_first_widget(master),
                "text": "",
                "image": image,
                "width": int(self.padding * 1.5),
                "height": int(self.padding * 1.5),
                "command": command,
            },
            widget_style="HeaderImage.CTkButton",
            grid_args={
                "row": 0,
                "columnspan": 999,
                "padx": int(self.padding * 1.5),
                "sticky": sticky,
            },
            row_weights=None,
            column_weights=None,
        )

        def on_enter(event):
            button.configure(image=image_hover)

        def on_leave(event):
            button.configure(image=image)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

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

    # def adjust_to_content(self, root, adjust_width=False, adjust_height=False):
    #     root = root or self

    #     root.minsize(
    #         root.winfo_reqwidth(),
    #         root.winfo_reqheight(),
    #     )

    #     root.resizable(adjust_width, adjust_height)

    # * Alternative to wrapping CTk.resizable(), causes flickering
    def adjust_to_content(
        self,
        root,
        max_width=None,
        max_height=None,
        adjust_width=False,
        adjust_height=False,
    ):
        root = root or self

        root.update_idletasks()
        current_width = max_width or root.winfo_reqwidth()
        current_height = max_height or root.winfo_reqheight()

        def set_minsize(previous_width, previous_height):
            root.minsize(
                min(previous_width, root._current_width),
                min(previous_height, root._current_height),
            )

        root.after(1009, lambda: set_minsize(current_width, current_height))

        root.resizable(adjust_width, adjust_height)

    def find_max_req_dimensions(self, frames):
        max_width = 0
        max_height = 0

        for frame in frames:
            width = frame.winfo_reqwidth()
            height = frame.winfo_reqheight()

            max_width = max(max_width, width)
            max_height = max(max_height, height)

        return max_width, max_height

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
            self.style_manager.apply_style(widget, widget_style)
        widget.grid(**grid_args)
        if row_weights:
            for row_index, weight in row_weights:
                widget.grid_rowconfigure(row_index, weight=weight)
        if column_weights:
            for column_index, weight in column_weights:
                widget.grid_columnconfigure(column_index, weight=weight)
        return widget

    def create_header(self, master, text="", row="current", column=0):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        header_label = self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": master,
                "text": text,
                "anchor": "center",
                "pady": self.padding,
            },
            widget_style="Header.CTkLabel",
            grid_args={
                "column": 0,
                "columnspan": 999,
                "sticky": "nsew",
            },
            row_weights=None,
            column_weights=None,
        )

        return header_label

    def create_subheader(self, master, text="", row="current", column=0):
        if row == "current":
            row = self._get_next_row(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            row = max(eval(f"{self._get_next_row(master)} {row}"), 0)

        if column == "current":
            column = self._get_next_column(master)
        elif isinstance(row, str) and row.startswith(("+", "-")):
            column = max(eval(f"{self._get_next_column(master)} {column}"), 0)

        frame = self.create_frame(
            master,
            style="SubHeader.CTkFrame",
            row=row,
            column=column,
            column_weights=[(0, 0), (1, 1)],
        )

        label = self.create_ctk_widget(
            ctk_widget=ctk.CTkLabel,
            widget_args={
                "master": frame,
                "text": text,
                "anchor": "w",
                "padx": self.padding,
                "pady": self.padding / 2,
            },
            widget_style="SubHeader.CTkLabel",
            grid_args={
                "sticky": "nsew",
                "row": 0,
                "column": 0,
            },
            row_weights=None,
            column_weights=None,
        )

        self.create_separator(frame, padx=self.padding, row=0, column=1)

        return

    def create_frame(
        self,
        master,
        scrollable=False,
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

        if scrollable:
            ctk_widget = ctk.CTkScrollableFrame
        else:
            ctk_widget = ctk.CTkFrame

        return self.create_ctk_widget(
            ctk_widget=ctk_widget,
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

    def create_separator(
        self,
        master,
        style="Separator.CTkFrame",
        row="current",
        column=0,
        rowspan=1,
        columnspan=999,
        sticky="ew",
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

        widget_args = {"master": master, "height": 2}

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

            return self.create_ctk_widget(
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

    def get_first_widget(self, parent):
        for widget in parent.winfo_children():
            if str(widget.winfo_manager()) == "grid":
                grid_info = widget.grid_info()
                if grid_info["row"] == 0 and grid_info["column"] == 0:
                    return widget
        return None

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
            widget_args["width"] = width
        if height:
            widget_args["height"] = height

        widget_args.update(kwargs)

        return self.create_ctk_widget(
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

    def create_settings_button(self, master):
        return self.create_header_button(
            master,
            command=lambda: WindowSettings(master),
            image=self.cog_image,
            image_hover=self.cog_image_hover,
            sticky="e",
        )
