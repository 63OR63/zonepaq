def get_styles(theme_dict):
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
    return styles
