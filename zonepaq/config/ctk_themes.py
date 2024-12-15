# First color in a list is for light mode, second one is for dark mode
import colorsys


color_palettes = {
    "Nord": {
        "color_text_primary": ["#434c5e", "#d8dee9"],
        "color_text_secondary": ["#3b4252", "#e5e9f0"],
        "color_text_accent": ["#2e3440", "#eceff4"],
        "color_background_primary": ["#eceff4", "#2e3440"],
        "color_background_secondary": ["#e5e9f0", "#3b4252"],
        "color_background_tertiary": ["#d8dee9", "#434c5e"],
        "color_muted": "#4c566a",
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


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return r, g, b


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def adjust_color_for_mode(hex_color, mode="dark", saturation_factor=1.1):
    # Convert HEX to RGB
    r, g, b = hex_to_rgb(hex_color)

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
    return rgb_to_hex(r, g, b)


# def get_colors(color, palette=color_palette):
#     color_list = []
#     if "light" in palette:
#         color_list.append(palette["light"][color])
#     else:
#         color_list.append(
#             adjust_color_for_mode(hex_color=palette["dark"][color], mode="light")
#         )
#     if "dark" in palette:
#         color_list.append(palette["dark"][color])
#     else:
#         color_list.append(
#             adjust_color_for_mode(hex_color=palette["light"][color], mode="dark")
#         )
#     return color_list


def get_colors(color, reverse=False, palette=color_palette):
    if isinstance(palette[color], list):
        color_list = palette[color]
    elif isinstance(palette[color], str):
        color_list = [palette[color], palette[color]]
    else:
        raise Exception
    if reverse:
        color_list = color_list[::-1]
    return color_list


color_palettes = {
    "Nord": {
        "color_text_primary": ["#434c5e", "#d8dee9"],
        "color_text_secondary": ["#3b4252", "#e5e9f0"],
        "color_text_accent": ["#2e3440", "#eceff4"],
        "color_background_primary": ["#eceff4", "#2e3440"],
        "color_background_secondary": ["#e5e9f0", "#3b4252"],
        "color_background_tertiary": ["#d8dee9", "#434c5e"],
        "color_muted": "#4c566a",
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

ctk_color_theme = {
    "CTk": {"fg_color": get_colors("color_background_primary")},
    "CTkToplevel": {"fg_color": get_colors("color_background_primary")},
    "CTkButton": {
        "fg_color": get_colors("color_accent_tertiary"),
        "hover_color": get_colors("color_accent_tertiary", True),
        "border_color": get_colors("color_accent_tertiary", True),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkCheckBox": {
        "fg_color": get_colors("color_accent_tertiary"),
        "border_color": get_colors("color_muted"),
        "hover_color": get_colors("color_muted"),
        "checkmark_color": get_colors("color_text_accent"),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkComboBox": {
        "fg_color": get_colors("color_background_secondary"),
        "border_color": get_colors("color_background_secondary"),
        "button_color": get_colors("color_muted"),
        "button_hover_color": get_colors("color_accent_tertiary"),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkEntry": {
        "fg_color": get_colors("color_background_secondary"),
        "border_color": get_colors("color_background_secondary"),
        "text_color": get_colors("color_text_primary"),
        "placeholder_text_color": get_colors("color_muted"),
    },
    "CTkFrame": {
        "fg_color": get_colors("color_background_secondary"),
        "top_fg_color": get_colors("color_background_tertiary"),
        "border_color": get_colors("color_muted"),
    },
    "CTkLabel": {
        "fg_color": "transparent",
        "text_color": get_colors("color_text_primary"),
    },
    "CTkOptionMenu": {
        "fg_color": get_colors("color_background_secondary"),
        "button_color": get_colors("color_muted"),
        "button_hover_color": get_colors("color_accent_tertiary"),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkProgressBar": {
        "fg_color": get_colors("color_background_secondary"),
        "progress_color": get_colors("color_accent_tertiary"),
        "border_color": get_colors("color_muted"),
    },
    "CTkRadioButton": {
        "fg_color": get_colors("color_accent_tertiary"),
        "border_color": get_colors("color_muted"),
        "hover_color": get_colors("color_accent_tertiary"),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkScrollableFrame": {"label_fg_color": get_colors("color_background_secondary")},
    "CTkScrollbar": {
        "fg_color": "transparent",
        "button_color": get_colors("color_accent_tertiary"),
        "button_hover_color": get_colors("color_accent_tertiary", True),
    },
    "CTkSegmentedButton": {
        "fg_color": get_colors("color_background_secondary"),
        "selected_color": get_colors("color_accent_tertiary"),
        "selected_hover_color": get_colors("color_accent_tertiary", True),
        "unselected_color": get_colors("color_background_secondary"),
        "unselected_hover_color": get_colors("color_muted"),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkSlider": {
        "fg_color": get_colors("color_background_tertiary"),
        "progress_color": get_colors("color_accent_tertiary"),
        "button_color": get_colors("color_accent_tertiary"),
        "button_hover_color": get_colors("color_accent_tertiary", True),
    },
    "CTkSwitch": {
        "fg_color": get_colors("color_background_secondary"),
        "progress_color": get_colors("color_background_tertiary"),
        "button_color": get_colors("color_accent_tertiary"),
        "button_hover_color": get_colors("color_accent_tertiary", True),
        "text_color": get_colors("color_text_primary"),
        "text_color_disabled": get_colors("color_text_secondary"),
    },
    "CTkTextbox": {
        "fg_color": get_colors("color_background_secondary"),
        "border_color": get_colors("color_muted"),
        "text_color": get_colors("color_text_primary"),
        "scrollbar_button_color": get_colors("color_accent_tertiary"),
        "scrollbar_button_hover_color": get_colors("color_accent_tertiary"),
    },
    "DropdownMenu": {
        "fg_color": get_colors("color_background_secondary"),
        "hover_color": get_colors("color_accent_tertiary"),
        "text_color": get_colors("color_text_primary"),
    },
}


def override():
    return {
        "CTk": {"fg_color": ["#f2f2f2", "#191919"]},
        "CTkToplevel": {"fg_color": ["#f2f2f2", "#191919"]},
        "CTkFrame": {
            "fg_color": ["#e5e5e5", "#212121"],
            "top_fg_color": ["#d8d8d8", "#282828"],
            "border_color": ["#a5a5a5", "#474747"],
        },
        "CTkButton": {
            "fg_color": ["#3a7ebf", "#1f538d"],
            "hover_color": ["#325882", "#14375e"],
            "border_color": ["#3E454A", "#949A9F"],
            "text_color": ["#DCE4EE", "#DCE4EE"],
            "text_color_disabled": ["#bcbcbc", "#999999"],
        },
        "CTkLabel": {
            "fg_color": "transparent",
            "text_color": ["#232323", "#d6d6d6"],
        },
        "CTkEntry": {
            "fg_color": ["#F9F9FA", "#343638"],
            "border_color": ["#979DA2", "#565B5E"],
            "text_color": ["#232323", "#d6d6d6"],
            "placeholder_text_color": ["#848484", "#9e9e9e"],
        },
        "CTkCheckBox": {
            "fg_color": ["#3a7ebf", "#1f538d"],
            "border_color": ["#3E454A", "#949A9F"],
            "hover_color": ["#325882", "#14375e"],
            "checkmark_color": ["#DCE4EE", "#e5e5e5"],
            "text_color": ["#232323", "#d6d6d6"],
            "text_color_disabled": ["#999999", "#727272"],
        },
        "CTkSwitch": {
            "fg_color": ["#939BA2", "#4A4D50"],
            "progress_color": ["#3a7ebf", "#1f538d"],
            "button_color": ["#5b5b5b", "#D5D9DE"],
            "button_hover_color": ["#333333", "#ffffff"],
            "text_color": ["#232323", "#d6d6d6"],
            "text_color_disabled": ["#999999", "#727272"],
        },
        "CTkRadioButton": {
            "fg_color": ["#3a7ebf", "#1f538d"],
            "border_color": ["#3E454A", "#949A9F"],
            "hover_color": ["#325882", "#14375e"],
            "text_color": ["#232323", "#d6d6d6"],
            "text_color_disabled": ["#999999", "#727272"],
        },
        "CTkProgressBar": {
            "fg_color": ["#939BA2", "#4A4D50"],
            "progress_color": ["#3a7ebf", "#1f538d"],
            "border_color": ["#808080", "#808080"],
        },
        "CTkSlider": {
            "fg_color": ["#939BA2", "#4A4D50"],
            "progress_color": ["#666666", "#AAB0B5"],
            "button_color": ["#3a7ebf", "#1f538d"],
            "button_hover_color": ["#325882", "#14375e"],
        },
        "CTkOptionMenu": {
            "fg_color": ["#3a7ebf", "#1f538d"],
            "button_color": ["#325882", "#14375e"],
            "button_hover_color": ["#234567", "#1e2c40"],
            "text_color": ["#DCE4EE", "#DCE4EE"],
            "text_color_disabled": ["#bcbcbc", "#999999"],
        },
        "CTkComboBox": {
            "fg_color": ["#F9F9FA", "#343638"],
            "border_color": ["#979DA2", "#565B5E"],
            "button_color": ["#979DA2", "#565B5E"],
            "button_hover_color": ["#6E7174", "#7A848D"],
            "text_color": ["#232323", "#d6d6d6"],
            "text_color_disabled": ["#7f7f7f", "#727272"],
        },
        "CTkScrollbar": {
            "fg_color": "transparent",
            "button_color": ["#8c8c8c", "#686868"],
            "button_hover_color": ["#666666", "#878787"],
        },
        "CTkSegmentedButton": {
            "fg_color": ["#979DA2", "#494949"],
            "selected_color": ["#3a7ebf", "#1f538d"],
            "selected_hover_color": ["#325882", "#14375e"],
            "unselected_color": ["#979DA2", "#494949"],
            "unselected_hover_color": ["#b2b2b2", "#686868"],
            "text_color": ["#DCE4EE", "#DCE4EE"],
            "text_color_disabled": ["#bcbcbc", "#999999"],
        },
        "CTkTextbox": {
            "fg_color": ["#ffffff", "#333333"],
            "border_color": ["#979DA2", "#565B5E"],
            "text_color": ["#232323", "#d6d6d6"],
            "scrollbar_button_color": ["#8c8c8c", "#686868"],
            "scrollbar_button_hover_color": ["#666666", "#878787"],
        },
        "CTkScrollableFrame": {"label_fg_color": ["#cccccc", "#353535"]},
        "DropdownMenu": {
            "fg_color": ["#e5e5e5", "#333333"],
            "hover_color": ["#bfbfbf", "#474747"],
            "text_color": ["#232323", "#d6d6d6"],
        },
    }


# ctk_color_theme = override()


# print(ctk_color_theme)


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
    "Hints.CustomFont": {
        "macOS": {"family": "SF Display", "size": 13, "weight": "normal"},
        "Windows": {"family": "Arial", "size": 13, "weight": "normal"},
        "Linux": {"family": "Roboto", "size": 13, "weight": "normal"},
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
}

dimensions_definitions = {
    "Large.CTkButton": {
        "width": 300,
        "height": 50,
    },
}


def merge_dicts(base, *updates):
    for update in updates:
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                merge_dicts(base[key], value)
            else:
                base[key] = value
    return base


selected_theme = "Default"
selected_theme = "Nord"

ctk_color_theme = merge_dicts(
    ctk_color_theme,
    borders_definitions,
    font_definitions,
    dimensions_definitions,
)


class CtkStyleManager:
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

    # "Default": {
    #     "CTk": {"fg_color": ["#f2f2f2", "#191919"]},
    #     "CTkToplevel": {"fg_color": ["#f2f2f2", "#191919"]},
    #     "CTkFrame": {
    #         "fg_color": ["#e5e5e5", "#212121"],
    #         "top_fg_color": ["#d8d8d8", "#282828"],
    #         "border_color": ["#a5a5a5", "#474747"],
    #     },
    #     "CTkButton": {
    #         "fg_color": ["#3a7ebf", "#1f538d"],
    #         "hover_color": ["#325882", "#14375e"],
    #         "border_color": ["#3E454A", "#949A9F"],
    #         "text_color": ["#DCE4EE", "#DCE4EE"],
    #         "text_color_disabled": ["#bcbcbc", "#999999"],
    #     },
    #     "CTkLabel": {
    #         "fg_color": "transparent",
    #         "text_color": ["#232323", "#d6d6d6"],
    #     },
    #     "CTkEntry": {
    #         "fg_color": ["#F9F9FA", "#343638"],
    #         "border_color": ["#979DA2", "#565B5E"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "placeholder_text_color": ["#848484", "#9e9e9e"],
    #     },
    #     "CTkCheckBox": {
    #         "fg_color": ["#3a7ebf", "#1f538d"],
    #         "border_color": ["#3E454A", "#949A9F"],
    #         "hover_color": ["#325882", "#14375e"],
    #         "checkmark_color": ["#DCE4EE", "#e5e5e5"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "text_color_disabled": ["#999999", "#727272"],
    #     },
    #     "CTkSwitch": {
    #         "fg_color": ["#939BA2", "#4A4D50"],
    #         "progress_color": ["#3a7ebf", "#1f538d"],
    #         "button_color": ["#5b5b5b", "#D5D9DE"],
    #         "button_hover_color": ["#333333", "#ffffff"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "text_color_disabled": ["#999999", "#727272"],
    #     },
    #     "CTkRadioButton": {
    #         "fg_color": ["#3a7ebf", "#1f538d"],
    #         "border_color": ["#3E454A", "#949A9F"],
    #         "hover_color": ["#325882", "#14375e"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "text_color_disabled": ["#999999", "#727272"],
    #     },
    #     "CTkProgressBar": {
    #         "fg_color": ["#939BA2", "#4A4D50"],
    #         "progress_color": ["#3a7ebf", "#1f538d"],
    #         "border_color": ["#808080", "#808080"],
    #     },
    #     "CTkSlider": {
    #         "fg_color": ["#939BA2", "#4A4D50"],
    #         "progress_color": ["#666666", "#AAB0B5"],
    #         "button_color": ["#3a7ebf", "#1f538d"],
    #         "button_hover_color": ["#325882", "#14375e"],
    #     },
    #     "CTkOptionMenu": {
    #         "fg_color": ["#3a7ebf", "#1f538d"],
    #         "button_color": ["#325882", "#14375e"],
    #         "button_hover_color": ["#234567", "#1e2c40"],
    #         "text_color": ["#DCE4EE", "#DCE4EE"],
    #         "text_color_disabled": ["#bcbcbc", "#999999"],
    #     },
    #     "CTkComboBox": {
    #         "fg_color": ["#F9F9FA", "#343638"],
    #         "border_color": ["#979DA2", "#565B5E"],
    #         "button_color": ["#979DA2", "#565B5E"],
    #         "button_hover_color": ["#6E7174", "#7A848D"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "text_color_disabled": ["#7f7f7f", "#727272"],
    #     },
    #     "CTkScrollbar": {
    #         "fg_color": "transparent",
    #         "button_color": ["#8c8c8c", "#686868"],
    #         "button_hover_color": ["#666666", "#878787"],
    #     },
    #     "CTkSegmentedButton": {
    #         "fg_color": ["#979DA2", "#494949"],
    #         "selected_color": ["#3a7ebf", "#1f538d"],
    #         "selected_hover_color": ["#325882", "#14375e"],
    #         "unselected_color": ["#979DA2", "#494949"],
    #         "unselected_hover_color": ["#b2b2b2", "#686868"],
    #         "text_color": ["#DCE4EE", "#DCE4EE"],
    #         "text_color_disabled": ["#bcbcbc", "#999999"],
    #     },
    #     "CTkTextbox": {
    #         "fg_color": ["#ffffff", "#333333"],
    #         "border_color": ["#979DA2", "#565B5E"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #         "scrollbar_button_color": ["#8c8c8c", "#686868"],
    #         "scrollbar_button_hover_color": ["#666666", "#878787"],
    #     },
    #     "CTkScrollableFrame": {"label_fg_color": ["#cccccc", "#353535"]},
    #     "DropdownMenu": {
    #         "fg_color": ["#e5e5e5", "#333333"],
    #         "hover_color": ["#bfbfbf", "#474747"],
    #         "text_color": ["#232323", "#d6d6d6"],
    #     },
    # },
    # "STALKER": {
    #     "CTk": {"fg_color": ["#C4C4C4", "#1E1E1E"]},
    #     "CTkToplevel": {"fg_color": ["#C4C4C4", "#1E1E1E"]},
    #     "CTkFrame": {
    #         "fg_color": ["#B0B0B0", "#2B2B2B"],
    #         "top_fg_color": ["#A0A0A0", "#3B3B3B"],
    #         "border_color": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkButton": {
    #         "fg_color": ["#5A7F4D", "#3E5A37"],
    #         "hover_color": ["#4E6A42", "#2F4A2B"],
    #         "border_color": ["#7C7F7A", "#4A4E48"],
    #         "text_color": ["#E0E0E0", "#BEBEBE"],
    #         "text_color_disabled": ["#7A7A7A", "#4C4C4C"],
    #     },
    #     "CTkLabel": {"fg_color": "transparent", "text_color": ["#2D2D2D", "#A5A5A5"]},
    #     "CTkEntry": {
    #         "fg_color": ["#CFCFCF", "#333333"],
    #         "border_color": ["#7A7A7A", "#505050"],
    #         "text_color": ["#2D2D2D", "#D0D0D0"],
    #         "placeholder_text_color": ["#6E6E6E", "#5C5C5C"],
    #     },
    #     "CTkCheckBox": {
    #         "fg_color": ["#5A7F4D", "#3E5A37"],
    #         "border_color": ["#7C7F7A", "#4A4E48"],
    #         "hover_color": ["#4E6A42", "#2F4A2B"],
    #         "checkmark_color": ["#E0E0E0", "#A5A5A5"],
    #         "text_color": ["#2D2D2D", "#C4C4C4"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkSwitch": {
    #         "fg_color": ["#5C5C5C", "#3B3B3B"],
    #         "progress_color": ["#5A7F4D", "#3E5A37"],
    #         "button_color": ["#A5A5A5", "#5C5C5C"],
    #         "button_hover_color": ["#4E6A42", "#2F4A2B"],
    #         "text_color": ["#2D2D2D", "#C4C4C4"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkRadioButton": {
    #         "fg_color": ["#5A7F4D", "#3E5A37"],
    #         "border_color": ["#7C7F7A", "#4A4E48"],
    #         "hover_color": ["#4E6A42", "#2F4A2B"],
    #         "text_color": ["#2D2D2D", "#C4C4C4"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkProgressBar": {
    #         "fg_color": ["#7C7C7C", "#3B3B3B"],
    #         "progress_color": ["#5A7F4D", "#3E5A37"],
    #         "border_color": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkSlider": {
    #         "fg_color": ["#7C7C7C", "#3B3B3B"],
    #         "progress_color": ["#4E6A42", "#2F4A2B"],
    #         "button_color": ["#5A7F4D", "#3E5A37"],
    #         "button_hover_color": ["#4A5F42", "#2A3F2B"],
    #     },
    #     "CTkOptionMenu": {
    #         "fg_color": ["#5A7F4D", "#3E5A37"],
    #         "button_color": ["#4E6A42", "#2F4A2B"],
    #         "button_hover_color": ["#3C4A37", "#253A2A"],
    #         "text_color": ["#E0E0E0", "#C4C4C4"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkComboBox": {
    #         "fg_color": ["#CFCFCF", "#333333"],
    #         "border_color": ["#7A7A7A", "#505050"],
    #         "button_color": ["#7A7A7A", "#505050"],
    #         "button_hover_color": ["#5C5C5C", "#4A4A4A"],
    #         "text_color": ["#2D2D2D", "#D0D0D0"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkScrollbar": {
    #         "fg_color": "transparent",
    #         "button_color": ["#6E6E6E", "#4C4C4C"],
    #         "button_hover_color": ["#4E6A42", "#3A3A3A"],
    #     },
    #     "CTkSegmentedButton": {
    #         "fg_color": ["#7A7A7A", "#333333"],
    #         "selected_color": ["#5A7F4D", "#3E5A37"],
    #         "selected_hover_color": ["#4E6A42", "#2F4A2B"],
    #         "unselected_color": ["#7C7C7C", "#3B3B3B"],
    #         "unselected_hover_color": ["#6E6E6E", "#505050"],
    #         "text_color": ["#E0E0E0", "#C4C4C4"],
    #         "text_color_disabled": ["#6E6E6E", "#4C4C4C"],
    #     },
    #     "CTkTextbox": {
    #         "fg_color": ["#FFFFFF", "#2B2B2B"],
    #         "border_color": ["#6E6E6E", "#4C4C4C"],
    #         "text_color": ["#2D2D2D", "#D0D0D0"],
    #         "scrollbar_button_color": ["#6E6E6E", "#4C4C4C"],
    #         "scrollbar_button_hover_color": ["#4E6A42", "#3A3A3A"],
    #     },
    #     "CTkScrollableFrame": {"label_fg_color": ["#B0B0B0", "#2B2B2B"]},
    #     "DropdownMenu": {
    #         "fg_color": ["#C4C4C4", "#2B2B2B"],
    #         "hover_color": ["#B0B0B0", "#3C3C3C"],
    #         "text_color": ["#2D2D2D", "#D0D0D0"],
    #     },
    # },
    # "Half-Life": {
    #     "CTk": {"fg_color": ["#f2f2f2", "#1b1b1b"]},
    #     "CTkToplevel": {"fg_color": ["#f2f2f2", "#1b1b1b"]},
    #     "CTkFrame": {
    #         "fg_color": ["#e6e6e6", "#2c2c2c"],
    #         "top_fg_color": ["#d9d9d9", "#3b3b3b"],
    #         "border_color": ["#a0a0a0", "#4d4d4d"],
    #     },
    #     "CTkButton": {
    #         "fg_color": ["#d98e04", "#a35300"],
    #         "hover_color": ["#b37702", "#7d4000"],
    #         "border_color": ["#6d6d6d", "#3e3e3e"],
    #         "text_color": ["#f2f2f2", "#e0e0e0"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkLabel": {"fg_color": "transparent", "text_color": ["#1e1e1e", "#d6d6d6"]},
    #     "CTkEntry": {
    #         "fg_color": ["#f4f4f4", "#303030"],
    #         "border_color": ["#7a7a7a", "#505050"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #         "placeholder_text_color": ["#8a8a8a", "#707070"],
    #     },
    #     "CTkCheckBox": {
    #         "fg_color": ["#d98e04", "#a35300"],
    #         "border_color": ["#6d6d6d", "#3e3e3e"],
    #         "hover_color": ["#b37702", "#7d4000"],
    #         "checkmark_color": ["#f2f2f2", "#e0e0e0"],
    #         "text_color": ["#1e1e1e", "#e0e0e0"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkSwitch": {
    #         "fg_color": ["#828282", "#4d4d4d"],
    #         "progress_color": ["#d98e04", "#a35300"],
    #         "button_color": ["#5c5c5c", "#c2c2c2"],
    #         "button_hover_color": ["#4a4a4a", "#ffffff"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkRadioButton": {
    #         "fg_color": ["#d98e04", "#a35300"],
    #         "border_color": ["#6d6d6d", "#3e3e3e"],
    #         "hover_color": ["#b37702", "#7d4000"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkProgressBar": {
    #         "fg_color": ["#bdbdbd", "#505050"],
    #         "progress_color": ["#d98e04", "#a35300"],
    #         "border_color": ["#8c8c8c", "#606060"],
    #     },
    #     "CTkSlider": {
    #         "fg_color": ["#bdbdbd", "#505050"],
    #         "progress_color": ["#555555", "#9b9b9b"],
    #         "button_color": ["#d98e04", "#a35300"],
    #         "button_hover_color": ["#b37702", "#7d4000"],
    #     },
    #     "CTkOptionMenu": {
    #         "fg_color": ["#d98e04", "#a35300"],
    #         "button_color": ["#b37702", "#7d4000"],
    #         "button_hover_color": ["#8c5f02", "#5e2d00"],
    #         "text_color": ["#f2f2f2", "#e5e5e5"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkComboBox": {
    #         "fg_color": ["#f4f4f4", "#303030"],
    #         "border_color": ["#7a7a7a", "#505050"],
    #         "button_color": ["#7a7a7a", "#505050"],
    #         "button_hover_color": ["#5a5a5a", "#707070"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #         "text_color_disabled": ["#888888", "#707070"],
    #     },
    #     "CTkScrollbar": {
    #         "fg_color": "transparent",
    #         "button_color": ["#7a7a7a", "#505050"],
    #         "button_hover_color": ["#5a5a5a", "#707070"],
    #     },
    #     "CTkSegmentedButton": {
    #         "fg_color": ["#9e9e9e", "#494949"],
    #         "selected_color": ["#d98e04", "#a35300"],
    #         "selected_hover_color": ["#b37702", "#7d4000"],
    #         "unselected_color": ["#9e9e9e", "#494949"],
    #         "unselected_hover_color": ["#bfbfbf", "#606060"],
    #         "text_color": ["#f2f2f2", "#e5e5e5"],
    #         "text_color_disabled": ["#b3b3b3", "#888888"],
    #     },
    #     "CTkTextbox": {
    #         "fg_color": ["#ffffff", "#2b2b2b"],
    #         "border_color": ["#7a7a7a", "#505050"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #         "scrollbar_button_color": ["#7a7a7a", "#505050"],
    #         "scrollbar_button_hover_color": ["#5a5a5a", "#707070"],
    #     },
    #     "CTkScrollableFrame": {"label_fg_color": ["#cccccc", "#3b3b3b"]},
    #     "DropdownMenu": {
    #         "fg_color": ["#e5e5e5", "#2c2c2c"],
    #         "hover_color": ["#bfbfbf", "#4d4d4d"],
    #         "text_color": ["#1e1e1e", "#e5e5e5"],
    #     },
    # },
