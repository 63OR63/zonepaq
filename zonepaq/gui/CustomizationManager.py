import tkinter as tk
from collections import deque
from tkinter import ttk

from backend.logger import log
from config.settings import settings
from config.styles import get_styles
from gui.InstanceManager import InstanceManager

# from gui.gui_main import GUI_LaunchScreen


class CustomizationManager:
    """Singleton class to apply and manage UI themes and customizations."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, style, theme_dict):
        self.style = style
        self.theme_dict = theme_dict
        self.instances = InstanceManager()  # Central instance tracking
        self._reload_styles(self.theme_dict)

    @classmethod
    def get(cls, theme_dict):
        if cls._instance is None:
            style = ttk.Style()
            style.theme_use("clam")
            # style.theme_use("alt")
            # style.theme_use("default")
            # style.theme_use("classic")
            # style.theme_use("vista")
            # style.theme_use("xpnative")
            cls._instance = cls(style, theme_dict)
        return cls._instance

    def reset(self):
        self.instances._reset()
        log.deep_debug("'CustomizationManager' instance cleared.")
        CustomizationManager._instance = None

    def apply_theme(self, window, theme_name):
        settings.update_config("SETTINGS", "theme_name", theme_name)

        self._reload_styles(settings.THEME_DICT)

        for widget in self.instances.widgets:
            widget.apply_style()

        for window in self.instances.windows:
            self._apply_specific_styles(window)

    def apply_translation(self, window, lang_name):
        settings.update_config("SETTINGS", "lang_name", lang_name)

        self.reset()

        window.destroy()

        # gui = GUI_LaunchScreen()
        # gui.run()

    def apply_show_hints(self, window, show_hints):
        settings.SHOW_HINTS = str(show_hints)
        settings.update_config("SETTINGS", "show_hints", show_hints)

        self.reset()

        window.destroy()
        # gui = GUI_LaunchScreen()
        # gui.run()

    def _reload_styles(self, theme_dict):
        styles = get_styles(theme_dict)
        for widget, config in styles.items():
            self.style.configure(widget, **config)

        self._map_style("TCheckbutton", theme_dict["color_background"])
        self._map_style("Treeview.Heading", theme_dict["color_background"])

    def _map_style(self, widget, color):
        self.style.map(
            widget,
            background=[
                ("active", color),
                ("!active", color),
            ],
        )

    def _apply_specific_styles(self, widget, generic={}, listboxes={}):
        excluded_widgets = (
            tk.Menu,
            tk.Entry,
        )

        default_generic = {
            "bg": settings.THEME_DICT["color_background"],
            "fg": settings.THEME_DICT["color_foreground"],
        }
        default_listboxes = {
            "bg": settings.THEME_DICT["color_background_highlight"],
            "fg": settings.THEME_DICT["color_foreground"],
            "selectbackground": settings.THEME_DICT["color_highlight"],
            "font": (
                settings.THEME_DICT["font_family_code"],
                settings.THEME_DICT["font_size_small"],
                "normal",
            ),
        }
        treeview_tags = {
            "no_conflicts": {"foreground": settings.THEME_DICT["color_success"]},
            "dual_match": {"foreground": settings.THEME_DICT["color_foreground"]},
            "dual_no_match": {"foreground": settings.THEME_DICT["color_attention"]},
            "tri": {"foreground": settings.THEME_DICT["color_warning"]},
            "complex": {"foreground": settings.THEME_DICT["color_error"]},
        }

        generic = {**default_generic, **generic}
        listboxes = {**default_listboxes, **listboxes}

        queue = deque([widget])

        while queue:
            current_widget = queue.popleft()
            if not isinstance(current_widget, excluded_widgets):
                if isinstance(current_widget, tk.Listbox):
                    for key, value in listboxes.items():
                        try:
                            if hasattr(current_widget, "configure"):
                                current_widget.configure({key: value})
                        except:
                            pass
                elif isinstance(current_widget, ttk.Treeview):
                    for tag, style in treeview_tags.items():
                        try:
                            current_widget.tag_configure(tag, **style)
                        except:
                            pass
                else:
                    for key, value in generic.items():
                        try:
                            if hasattr(current_widget, "configure"):
                                current_widget.configure({key: value})
                        except:
                            pass

            queue.extend(current_widget.winfo_children())
