import customtkinter

from config.settings import settings
from config.ctk_themes import ctk_color_theme

import customtkinter as ctk


# Custom Style Manager
class StyleManager:
    _styles = {}  # Dictionary to store custom styles

    @classmethod
    def define_style(cls, style_name, **options):
        cls._styles[style_name] = options

    @classmethod
    def apply_style(cls, widget, style_name):
        if style_name in cls._styles:
            style = cls._styles[style_name]
            for key, value in style.items():
                if hasattr(
                    widget, "configure"
                ):  # Check if widget has method to configure
                    widget.configure(**{key: value})
                else:
                    # If it's a direct attribute, set it directly
                    if hasattr(widget, f"_{key}"):
                        setattr(widget, f"_{key}", value)
        else:
            print(f"Style '{style_name}' not defined!")


theme_dict = settings.THEME_DICT


# StyleManager.define_style(
#     "Accent.CTkButton",
#     fg_color=["#ffA8E8", "#ff77B6"],  # Light/Dark mode colors
#     hover_color=["#ff86C6", "#ff5F89"],
#     border_color=["#FFFFFF", "#FFFFFF"],
#     text_color=["#ffA8E8", "#ff77B6"],
#     text_color_disabled=["#ffA8E8", "#ff77B6"],
# )
