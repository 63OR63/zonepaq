import colorsys
import logging

import customtkinter as ctk
from backend.logger import log
from PIL import Image

logging.getLogger("PIL").setLevel(logging.WARNING)


class ThemeManager:
    # First color in a list is for light mode, second one is for dark mode
    color_palettes = {
        "Nord": {
            "color_text_primary": ["#3b4252", "#e5e9f0"],
            "color_text_secondary": ["#434c5e", "#d8dee9"],
            "color_text_accent": ["#2e3440", "#eceff4"],
            "color_text_muted": ["#b2bdd3", "#616e7c"],
            "color_background_primary": ["#eceff4", "#2e3440"],
            "color_background_secondary": ["#e5e9f0", "#3b4252"],
            "color_background_tertiary": ["#d8dee9", "#434c5e"],
            "color_accent_primary": ["#88c0d0", "#88c0d0"],
            "color_accent_secondary": ["#8fbcbb", "#8fbcbb"],
            "color_accent_tertiary": ["#81a1c1", "#5e81ac"],
            "color_accent_quaternary": ["#5e81ac", "#81a1c1"],
            "color_error": "#bf616a",
            "color_warning": "#d08770",
            "color_attention": "#ebcb8b",
            "color_success": "#a3be8c",
            "color_highlight": "#b48ead",
        },
        "S.T.A.L.K.E.R.": {
            "color_text_primary": ["#1b1f22", "#fff7e1"],
            "color_text_secondary": ["#272a28", "#fbe6bd"],
            "color_text_accent": ["#353533", "#f0d0b0"],
            "color_text_muted": ["#7a7d81", "#5b5b57"],
            "color_background_primary": ["#f5eaf0", "#1b1e22"],
            "color_background_secondary": ["#cfc6cb", "#191b1f"],
            "color_background_tertiary": ["#b7afaa", "#5d705e"],
            "color_accent_primary": ["#96bb98", "#7a947a"],
            "color_accent_secondary": ["#9fcda1", "#a8c8a5"],
            "color_accent_tertiary": ["#719888", "#14161a"],
            "color_accent_quaternary": ["#7cb49d", "#15181c"],
            "color_error": "#a64441",
            "color_warning": "#d77c37",
            "color_attention": "#e8b847",
            "color_success": "#609f5f",
            "color_highlight": "#8a7295",
        },
        "Half-Life": {
            "color_text_primary": ["#1c1c1c", "#f7f7f7"],
            "color_text_secondary": ["#282828", "#dcdcdc"],
            "color_text_accent": ["#303030", "#e6e6e6"],
            "color_text_muted": ["#747474", "#8c8c8c"],
            "color_background_primary": ["#c1c9b7", "#1a1a1a"],
            "color_background_secondary": ["#b4bca9", "#262626"],
            "color_background_tertiary": ["#a8b09d", "#333333"],
            "color_accent_primary": ["#fb991e", "#fb991e"],
            "color_accent_secondary": ["#ffb91e", "#ffb91e"],
            "color_accent_tertiary": ["#fb620a", "#fb620a"],
            "color_accent_quaternary": ["#fb821b", "#fb821b"],
            "color_error": "#b8160a",
            "color_warning": "#fb620a",
            "color_attention": "#ffb91e",
            "color_success": "#2ecc71",
            "color_highlight": "#9b59b6",
        },
        "Mass Effect": {
            "color_text_primary": ["#1a2633", "#d6e0ed"],
            "color_text_secondary": ["#233645", "#c1c9d6"],
            "color_text_accent": ["#2b3d4f", "#eef4fa"],
            "color_text_muted": ["#4a5866", "#6d7584"],
            "color_background_primary": ["#e9efff", "#1a2633"],
            "color_background_secondary": ["#d1ddfb", "#233645"],
            "color_background_tertiary": ["#a4b0cf", "#2b3d4f"],
            "color_accent_primary": ["#698aff", "#568fa0"],
            "color_accent_secondary": ["#6182dc", "#6ab1c6"],
            "color_accent_tertiary": ["#ff2f2f", "#a11429"],
            "color_accent_quaternary": ["#e62b2d", "#cd142d"],
            "color_error": "#e03b4e",
            "color_warning": "#f79420",
            "color_attention": "#ffd700",
            "color_success": "#59a84e",
            "color_highlight": "#9157c1",
        },
        "Cyberpunk": {
            "color_text_primary": ["#00e6ef", "#cce957"],
            "color_text_secondary": ["#4db0a4", "#55f7fe"],
            "color_text_accent": ["#00fff7", "#1cd577"],
            "color_text_muted": ["#596f72", "#5d692e"],
            "color_background_primary": ["#0f121a", "#171017"],
            "color_background_secondary": ["#1f1a22", "#151219"],
            "color_background_tertiary": ["#35181d", "#212219"],
            "color_accent_primary": ["#8c0c2c", "#135143"],
            "color_accent_secondary": ["#c70842", "#106a56"],
            "color_accent_tertiary": ["#00716f", "#19373d"],
            "color_accent_quaternary": ["#00a4a1", "#21434b"],
            "color_error": "#fa675b",
            "color_warning": "#ffaa00",
            "color_attention": ["#cef05b", "#fee909"],
            "color_success": "#17deaf",
            "color_highlight": "#902ac7",
        },
        "Space Rangers": {
            "color_text_primary": ["#124643", "#99b8b7"],
            "color_text_secondary": ["#002637", "#8c9ea9"],
            "color_text_accent": ["#024c6f", "#69b1bf"],
            "color_text_muted": ["#134643", "#95a5a6"],
            "color_background_primary": ["#9fbfbe", "#061f1f"],
            "color_background_secondary": ["#88abaf", "#002637"],
            "color_background_tertiary": ["#689193", "#024c6f"],
            "color_accent_primary": ["#00d5cc", "#003758"],
            "color_accent_secondary": ["#3bded3", "#006490"],
            "color_accent_tertiary": ["#31b8af", "#002d3d"],
            "color_accent_quaternary": ["#05cac0", "#06485b"],
            "color_error": "#f25c50",
            "color_warning": "#f39c12",
            "color_attention": "#f1c40f",
            "color_success": "#129c19",
            "color_highlight": "#2ca5bf",
        },
    }

    borders_definitions = {
        "CTkFrame": {
            "corner_radius": 6,
            "border_width": 0,
        },
        "CTkButton": {
            "corner_radius": 6,
            "border_width": 0,
        },
        "CTkLabel": {
            "corner_radius": 0,
        },
        "CTkEntry": {
            "corner_radius": 6,
            "border_width": 2,
        },
        "CTkCheckBox": {
            "corner_radius": 6,
            "border_width": 3,
        },
        "CTkSwitch": {
            "corner_radius": 1000,
            "border_width": 3,
            "button_length": 0,
        },
        "CTkRadioButton": {
            "corner_radius": 1000,
            "border_width_checked": 6,
            "border_width_unchecked": 3,
        },
        "CTkProgressBar": {
            "corner_radius": 1000,
            "border_width": 0,
        },
        "CTkSlider": {
            "corner_radius": 1000,
            "button_corner_radius": 1000,
            "border_width": 6,
            "button_length": 0,
        },
        "CTkOptionMenu": {
            "corner_radius": 6,
        },
        "CTkComboBox": {
            "corner_radius": 6,
            "border_width": 2,
        },
        "CTkScrollbar": {
            "corner_radius": 1000,
            "border_spacing": 4,
        },
        "CTkSegmentedButton": {
            "corner_radius": 6,
            "border_width": 2,
        },
        "CTkTextbox": {
            "corner_radius": 6,
            "border_width": 0,
        },
    }

    font_definitions = {
        "CTkFont": {
            "macOS": {"family": "SF Display", "size": 14, "weight": "normal"},
            "Windows": {"family": "Arial", "size": 14, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 14, "weight": "normal"},
        },
        "Header.CustomFont": {
            "macOS": {"family": "SF Display", "size": 20, "weight": "bold"},
            "Windows": {"family": "Arial", "size": 20, "weight": "bold"},
            "Linux": {"family": "Roboto", "size": 20, "weight": "bold"},
        },
        "SubHeader.CustomFont": {
            "macOS": {"family": "SF Display", "size": 15, "weight": "bold"},
            "Windows": {"family": "Arial", "size": 15, "weight": "bold"},
            "Linux": {"family": "Roboto", "size": 15, "weight": "bold"},
        },
        "Hints.CustomFont": {
            "macOS": {"family": "SF Display", "size": 13, "weight": "normal"},
            "Windows": {"family": "Arial", "size": 13, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 13, "weight": "normal"},
        },
        "Dnd.CustomFont": {
            "macOS": {"family": "SF Display", "size": 18, "weight": "normal"},
            "Windows": {"family": "Consolas", "size": 18, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 18, "weight": "normal"},
        },
        "Generic.Button.CustomFont": {
            "macOS": {"family": "SF Display", "size": 15, "weight": "normal"},
            "Windows": {"family": "Arial", "size": 15, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 15, "weight": "normal"},
        },
        "Action.Button.CustomFont": {
            "macOS": {"family": "SF Display", "size": 16, "weight": "normal"},
            "Windows": {"family": "Arial", "size": 16, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 16, "weight": "normal"},
        },
        "List.CustomFont": {
            "macOS": {"family": "SF Display", "size": 14, "weight": "normal"},
            "Windows": {"family": "Consolas", "size": 14, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 14, "weight": "normal"},
        },
        "Entry.CustomFont": {
            "macOS": {"family": "SF Display", "size": 14, "weight": "normal"},
            "Windows": {"family": "Consolas", "size": 14, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 14, "weight": "normal"},
        },
    }

    dimensions_definitions = {
        "Large.CTkButton": {
            "width": 300,
            "height": 50,
        },
    }

    @classmethod
    def get_available_theme_names(cls):
        return list(cls.color_palettes.keys())

    @classmethod
    def construct_color_theme(cls, color_palette):
        ctk_color_theme = {
            "CTk": {
                "fg_color": cls.get_colors("color_background_primary", color_palette)
            },
            "CTkToplevel": {
                "fg_color": cls.get_colors("color_background_primary", color_palette)
            },
            "CTkButton": {
                "fg_color": cls.get_colors("color_accent_tertiary", color_palette),
                "hover_color": cls.get_colors("color_accent_quaternary", color_palette),
                "border_color": cls.get_colors(
                    "color_accent_quaternary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkCheckBox": {
                "fg_color": cls.get_colors("color_accent_tertiary", color_palette),
                "border_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "hover_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "checkmark_color": cls.get_colors("color_text_accent", color_palette),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkComboBox": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "border_color": cls.get_colors(
                    "color_background_secondary", color_palette
                ),
                "button_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "button_hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkEntry": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "border_color": cls.get_colors(
                    "color_background_secondary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "placeholder_text_color": cls.get_colors(
                    "color_text_muted", color_palette
                ),
            },
            "CTkFrame": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "top_fg_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "border_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
            },
            "CTkLabel": {
                "fg_color": "transparent",
                "text_color": cls.get_colors("color_text_primary", color_palette),
            },
            "CTkOptionMenu": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "button_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "button_hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkProgressBar": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "progress_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "border_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
            },
            "CTkRadioButton": {
                "fg_color": cls.get_colors("color_accent_tertiary", color_palette),
                "border_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "hover_color": cls.get_colors("color_accent_tertiary", color_palette),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkScrollableFrame": {
                "label_fg_color": cls.get_colors(
                    "color_background_secondary", color_palette
                )
            },
            "CTkScrollbar": {
                "fg_color": "transparent",
                "button_color": cls.get_colors("color_accent_tertiary", color_palette),
                "button_hover_color": cls.get_colors(
                    "color_accent_quaternary", color_palette
                ),
            },
            "CTkSegmentedButton": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "selected_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "selected_hover_color": cls.get_colors(
                    "color_accent_quaternary", color_palette
                ),
                "unselected_color": cls.get_colors(
                    "color_background_secondary", color_palette
                ),
                "unselected_hover_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkSlider": {
                "fg_color": cls.get_colors("color_background_tertiary", color_palette),
                "progress_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "button_color": cls.get_colors("color_accent_tertiary", color_palette),
                "button_hover_color": cls.get_colors(
                    "color_accent_quaternary", color_palette
                ),
            },
            "CTkSwitch": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "progress_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "button_color": cls.get_colors("color_accent_tertiary", color_palette),
                "button_hover_color": cls.get_colors(
                    "color_accent_quaternary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "text_color_disabled": cls.get_colors(
                    "color_text_secondary", color_palette
                ),
            },
            "CTkTextbox": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "border_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "text_color": cls.get_colors("color_text_primary", color_palette),
                "scrollbar_button_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "scrollbar_button_hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
            },
            "DropdownMenu": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "hover_color": cls.get_colors("color_accent_tertiary", color_palette),
                "text_color": cls.get_colors("color_text_primary", color_palette),
            },
        }
        return ctk_color_theme

    @classmethod
    def colorize_mask(cls, input_image_path, hex_color):
        output_color = cls._hex_to_rgb(hex_color)

        img = Image.open(input_image_path).convert("RGBA")

        data = img.getdata()
        new_data = []
        for pixel in data:
            if pixel[3] > 0:
                new_data.append((*output_color, 255))
            else:
                new_data.append((0, 0, 0, 0))

        img.putdata(new_data)
        return img

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        return r, g, b

    @staticmethod
    def _rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def _adjust_color_for_mode(cls, hex_color, mode="dark", saturation_factor=1.1):
        # Convert HEX to RGB
        r, g, b = cls._hex_to_rgb(hex_color)

        # Normalize RGB values to [0, 1] range
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # Convert RGB to HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        l = max(0, 1 - l)  # Invert lightness

        # Adjust saturation based on mode
        if mode == "dark":
            s = min(1, s * saturation_factor)  # Increase saturation
        elif mode == "light":
            s = max(0, s / saturation_factor)  # Decrease saturation

        # Convert HSL back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert back to 0-255 range
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        # Return the resulting color as a HEX string
        return cls._rgb_to_hex(r, g, b)

    @classmethod
    def get_colors(cls, color, color_palette, reverse=False):
        color_dict = cls.color_palettes[color_palette]
        if isinstance(color_dict[color], list):
            color_list = color_dict[color]
        elif isinstance(color_dict[color], str):
            color_list = [color_dict[color], color_dict[color]]
        else:
            raise Exception
        if reverse:
            color_list = color_list[::-1]
        return color_list

    @classmethod
    def get_color_for_mode(cls, color_key, color_palette):
        appearance_mode = ctk.get_appearance_mode()

        is_dark_mode = appearance_mode == "Dark"

        color_list = cls.get_colors(color_key, color_palette)

        return color_list[1] if is_dark_mode else color_list[0]

    @classmethod
    def merge_dicts(cls, base, *updates):
        for update in updates:
            for key, value in update.items():
                if (
                    isinstance(value, dict)
                    and key in base
                    and isinstance(base[key], dict)
                ):
                    cls.merge_dicts(base[key], value)
                else:
                    base[key] = value
        return base


# !WORKAROUND for lacking styling option as in Ttk
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
            log.error(f"Style '{style_name}' not defined!")

    @classmethod
    def define_custom_styles(cls, color_palette):

        cls.define_style(
            "Header.CTkLabel",
            fg_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Header.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Header.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Header.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "SubHeader.CTkLabel",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["SubHeader.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["SubHeader.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["SubHeader.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "SubHeader2.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["SubHeader.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["SubHeader.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["SubHeader.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Hints.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_text_muted", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Hints.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Hints.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Hints.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Hints2.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_text_secondary", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Hints.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Hints.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Hints.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Error.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_error", color_palette),
        )

        cls.define_style(
            "Warning.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_warning", color_palette),
        )

        cls.define_style(
            "Attention.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_attention", color_palette),
        )

        cls.define_style(
            "Success.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_success", color_palette),
        )

        cls.define_style(
            "Highlight.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors("color_highlight", color_palette),
        )

        cls.define_style(
            "Dnd.CTkLabel",
            fg_color="transparent",
            text_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            # text_color=ThemeManager.get_colors("color_text_muted", color_palette),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Dnd.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Dnd.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Dnd.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Transparent.CTkFrame",
            fg_color="transparent",
            # border_color="red",
            # border_width=1,
        )

        cls.define_style(
            "SubHeader.CTkFrame",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
        )

        cls.define_style(
            "Separator.CTkFrame",
            fg_color=ThemeManager.get_colors("color_text_muted", color_palette),
            # border_color="red",
            # border_width=1,
        )

        cls.define_style(
            "Primary.CTkFrame",
            fg_color=ThemeManager.get_colors("color_background_primary", color_palette),
            # border_color="red",
            # border_width=1,
        )

        cls.define_style(
            "Secondary.CTkFrame",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            # border_color="red",
            # border_width=1,
        )

        cls.define_style(
            "Tertiary.CTkFrame",
            fg_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            # border_color="red",
            # border_width=1,
        )

        cls.define_style(
            "HeaderImage.CTkButton",
            fg_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            hover_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
        )

        cls.define_style(
            "Generic.CTkButton",
            fg_color=ThemeManager.get_colors("color_accent_tertiary", color_palette),
            hover_color=ThemeManager.get_colors(
                "color_accent_quaternary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_accent_quaternary", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Alt.CTkButton",
            fg_color=ThemeManager.get_colors("color_accent_primary", color_palette),
            hover_color=ThemeManager.get_colors(
                "color_accent_secondary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_accent_secondary", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Action.CTkButton",
            fg_color=ThemeManager.get_colors("color_accent_primary", color_palette),
            hover_color=ThemeManager.get_colors(
                "color_accent_secondary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_accent_secondary", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Action.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Action.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Action.Button.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Muted.CTkButton",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            hover_color=ThemeManager.get_colors(
                "color_accent_quaternary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_accent_quaternary", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Generic.Button.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Alt.CTkEntry",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            border_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            placeholder_text_color=ThemeManager.get_colors(
                "color_text_muted", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Entry.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Entry.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Entry.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "AltError.CTkEntry",
            fg_color=ThemeManager.get_colors(
                "color_background_secondary", color_palette
            ),
            border_color=ThemeManager.get_colors("color_error", color_palette),
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            placeholder_text_color=ThemeManager.get_colors(
                "color_text_muted", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["Entry.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["Entry.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["Entry.CustomFont"]["weight"],
            ),
        )

        cls.define_style(
            "Custom.CTkListbox",
            fg_color="transparent",
            border_color=ThemeManager.get_colors(
                "color_background_tertiary", color_palette
            ),
            text_color=ThemeManager.get_colors("color_text_primary", color_palette),
            button_color="transparent",
            hover_color=ThemeManager.get_colors(
                "color_accent_quaternary", color_palette
            ),
            highlight_color=ThemeManager.get_colors(
                "color_accent_tertiary", color_palette
            ),
            font=ctk.CTkFont(
                family=ctk.ThemeManager.theme["List.CustomFont"]["family"],
                size=ctk.ThemeManager.theme["List.CustomFont"]["size"],
                weight=ctk.ThemeManager.theme["List.CustomFont"]["weight"],
            ),
        )
