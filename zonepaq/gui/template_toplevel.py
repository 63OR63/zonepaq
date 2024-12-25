from backend.logger import log
from config.metadata import APP_NAME, APP_VERSION
from gui.ctk_wraps import CTkToplevel


class TemplateToplevel(CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.master = master

        self.title(f"{APP_NAME} v{APP_VERSION} - {title}")

        self.lift()  # Bring to front
        self.focus()  # Request focus
        self.grab_set()  # Make it modal

        self._bind_master_attributes()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        raise NotImplementedError("Subclasses must implement the 'on_closing' method.")

    def _bind_master_attributes(self):

        attribute_names = [
            "games_manager",
            "tools_manager",
            "theme_manager",
            "style_manager",
            "padding",
            "cog_image",
            "cog_image_hover",
            "help_image",
            "help_image_hover",
        ]

        method_names = [
            "adjust_to_content",
            "find_max_req_dimensions",
            "create_ctk_widget",
            "create_header",
            "create_subheader",
            "create_frame",
            "create_spacer",
            "create_separator",
            "create_hints",
            "_get_next_row",
            "_get_next_column",
            "create_button",
            "create_header_button",
            "create_settings_button",
        ]

        for name in attribute_names + method_names:
            if hasattr(self.master, name):
                try:
                    setattr(self, name, getattr(self.master, name))
                    # log.debug(
                    #     f"Bound '{name}' from {self.master.__class__.__name__} to {self.__class__.__name__}"
                    # )
                except AttributeError as e:
                    log.exception(f"Failed to bind '{name}': {e}")
            else:
                log.warning(
                    f"'{name}' does not exist in {self.master.__class__.__name__}. Skipping."
                )
