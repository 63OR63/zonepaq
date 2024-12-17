# First color in a list is for light mode, second one is for dark mode
import colorsys
from logging import log


class ThemeManager:

    color_palettes = {
        "Nord": {
            "color_text_primary": ["#3b4252", "#e5e9f0"],
            "color_text_secondary": ["#434c5e", "#d8dee9"],
            "color_text_accent": ["#2e3440", "#eceff4"],
            "color_text_muted": ["#b2bdd3", "#616e7c"],
            "color_background_primary": ["#eceff4", "#2e3440"],
            "color_background_secondary": ["#e5e9f0", "#3b4252"],
            "color_background_tertiary": ["#d8dee9", "#434c5e"],
            "color_accent_primary": "#88c0d0",
            "color_accent_secondary": "#8fbcbb",
            "color_accent_tertiary": ["#81a1c1", "#5e81ac"],
            "color_error": "#bf616a",
            "color_warning": "#d08770",
            "color_attention": "#ebcb8b",
            "color_success": "#a3be8c",
            "color_highlight": "#b48ead",
        }
    }
    color_palette = color_palettes["Nord"]

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
                "hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette, True
                ),
                "border_color": cls.get_colors(
                    "color_accent_tertiary", color_palette, True
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
                    "color_accent_tertiary", color_palette, True
                ),
            },
            "CTkSegmentedButton": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "selected_color": cls.get_colors(
                    "color_accent_tertiary", color_palette
                ),
                "selected_hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette, True
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
                    "color_accent_tertiary", color_palette, True
                ),
            },
            "CTkSwitch": {
                "fg_color": cls.get_colors("color_background_secondary", color_palette),
                "progress_color": cls.get_colors(
                    "color_background_tertiary", color_palette
                ),
                "button_color": cls.get_colors("color_accent_tertiary", color_palette),
                "button_hover_color": cls.get_colors(
                    "color_accent_tertiary", color_palette, True
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
    def _hex_to_rgb(cls, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        return r, g, b

    @classmethod
    def _rgb_to_hex(cls, r, g, b):
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
