import math
import sys
import tkinter as tk
from pathlib import Path

from backend.logger import log
from backend.tools import Data
from config.metadata import *
from config.settings import settings


# get the resource path for the application icon and other resources
def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(".")

    return base_path / relative_path


def set_app_icon(root):
    root.iconphoto(True, tk.PhotoImage(file=resource_path(APP_ICONS["png"])))


class CustomWidget:
    def __init__(self, parent, customization_manager, style, **kwargs):
        self.root = parent
        self.customization_manager = customization_manager
        self.style = style
        self.window = kwargs.pop("window", None)

        self.reload_style()

        customization_manager.instances.register_widget(self, self.window or self.root)

    def reload_style(self, forced_style=None):
        style = forced_style or self.style
        self.bg_color = self.customization_manager.style.lookup(style, "background")
        self.fg_color = self.customization_manager.style.lookup(style, "foreground")
        self.font = self.customization_manager.style.lookup(style, "font")

    def apply_style(self, forced_style=None):
        raise NotImplementedError("Subclasses must implement apply_style")


class CustomButton(CustomWidget):
    def __init__(
        self,
        parent,
        customization_manager,
        text,
        subtitle_text=None,
        accent=None,
        command=None,
        style="TButton",
        width=300,
        height=70,
        radius_divisor=3.5,
        **kwargs,
    ):
        super().__init__(parent, customization_manager, style, **kwargs)
        self.command = command
        self.width = width
        self.height = height
        self.radius_divisor = radius_divisor
        self.text = text
        self.subtitle_text = subtitle_text
        self.accent = accent

        self.bg_color = self.customization_manager.style.lookup(style, "background")
        self.fg_color = self.customization_manager.style.lookup(style, "foreground")
        self.font = self.customization_manager.style.lookup(style, "font")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=self._get_parent_bg(),
            highlightthickness=0,
        )

        self.round_rect = self._create_rounded_rectangle(
            self.canvas,
            2,
            2,
            width - 2,
            height - 2,
            height / 2 / radius_divisor,
            fill=self.bg_color,
        )

        if style == "Subtitle.TButton":
            self.text_element = self.canvas.create_text(
                width // 2,
                height // 3,
                text=text,
                fill=self.fg_color,
                font=self.font,
                tags=("subtitle",),
            )
            self.subtitle_text_element = self.canvas.create_text(
                width // 2,
                (2 * height) // 3,
                text=subtitle_text,
                fill=self.fg_color,
                font=self.font,
                tags=("subtitle",),
            )
        else:
            self.text_element = self.canvas.create_text(
                width // 2, height // 2, text=text, fill=self.fg_color, font=self.font
            )

        self._bind_events()

    def _get_parent_bg(self):
        try:
            style_name = self.root.cget("style")
            return (
                self.customization_manager.style.lookup(style_name, "background")
                or settings.THEME_DICT["color_background"]
            )
        except tk.TclError:
            return settings.THEME_DICT["color_background"]

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = []
        # Cap the radius to half the rectangle's width or height
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)

        # Define the angles for quarter-circles at corners
        corner_angles = [
            (180, 270),  # Top-left corner
            (270, 360),  # Top-right corner
            (0, 90),  # Bottom-right corner
            (90, 180),  # Bottom-left corner
        ]

        # Center points for the corner circles
        corner_centers = [
            (x1 + radius, y1 + radius),  # Top-left
            (x2 - radius, y1 + radius),  # Top-right
            (x2 - radius, y2 - radius),  # Bottom-right
            (x1 + radius, y2 - radius),  # Bottom-left
        ]

        # Generate points for the rounded rectangle
        for (start_angle, end_angle), (cx, cy) in zip(corner_angles, corner_centers):
            for angle in range(start_angle, end_angle + 1, 1):  # Step through angles
                rad = math.radians(angle)
                x = cx + radius * math.cos(rad)
                y = cy + radius * math.sin(rad)
                points.append((x, y))

        # Connect the points to form a smooth polygon
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def apply_style(self, forced_style=None):
        style = forced_style or self.style
        self.reload_style(forced_style=style)

        self.canvas.itemconfig(self.round_rect, fill=self.bg_color)
        self.canvas.itemconfig(self.text_element, fill=self.fg_color, font=self.font)
        if hasattr(self, "subtitle_text_element"):
            self.canvas.itemconfig(
                self.subtitle_text_element, fill=self.fg_color, font=self.font
            )

    def grid(self, row, column, padx=0, pady=0, columnspan=1, **kwargs):
        self.canvas.grid(
            row=row,
            column=column,
            padx=padx,
            pady=pady,
            columnspan=columnspan,
            **kwargs,
        )

    def _bind_events(self):
        # Bind events to the rounded rectangle
        self.canvas.tag_bind(self.round_rect, "<ButtonPress-1>", self._on_press)
        self.canvas.tag_bind(self.round_rect, "<ButtonRelease-1>", self._on_release)

        # Bind events to the main text
        self.canvas.tag_bind(self.text_element, "<ButtonPress-1>", self._on_press)
        self.canvas.tag_bind(self.text_element, "<ButtonRelease-1>", self._on_release)

        # Bind events to the subtitle text if it exists
        if hasattr(self, "subtitle_text_element"):
            self.canvas.tag_bind(
                self.subtitle_text_element, "<ButtonPress-1>", self._on_press
            )
            self.canvas.tag_bind(
                self.subtitle_text_element, "<ButtonRelease-1>", self._on_release
            )

    def _on_press(self, event=None):
        self._change_button_color(darken=True)

    def _on_release(self, event=None):
        self._change_button_color(darken=False)
        if callable(self.command):
            self.command()

    def _change_button_color(self, darken):
        color = self._darken_color(self.bg_color) if darken else self.bg_color
        self.canvas.itemconfig(self.round_rect, fill=color)

    def _darken_color(self, color, factor=0.9):
        color = color.lstrip("#")
        r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"


class CustomEntry(CustomWidget):
    def __init__(
        self,
        parent,
        customization_manager,
        textvariable=None,
        width=0,
        style="PathEntry",
        **kwargs,
    ):
        super().__init__(parent, customization_manager, style, **kwargs)
        self.textvariable = textvariable or tk.StringVar()
        self.entry = tk.Entry(
            self.root,
            width=0,
            textvariable=self.textvariable,
            bg=self.customization_manager.style.lookup(style, "background"),
            fg=self.customization_manager.style.lookup(style, "foreground"),
            font=self.customization_manager.style.lookup(style, "font"),
        )

    def apply_style(self, forced_style=None):
        style = forced_style or self.style
        self.entry.configure(
            bg=self.customization_manager.style.lookup(style, "background"),
            fg=self.customization_manager.style.lookup(style, "foreground"),
            font=self.customization_manager.style.lookup(style, "font"),
        )

    def get_style(self, entry_type):
        path = Path(self.get())
        if Data.is_valid_data(path, entry_type):
            return "PathEntry.TEntry"
        return "PathInvalid.TEntry"

    def grid(self, row, column, padx=0, pady=0, columnspan=1, **kwargs):
        self.entry.grid(
            row=row,
            column=column,
            padx=padx,
            pady=pady,
            columnspan=columnspan,
            **kwargs,
        )

    def get(self):
        return self.textvariable.get().strip()

    def set(self, value):
        self.textvariable.set(value)
