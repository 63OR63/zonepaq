from backend.logger import log
from config.translations import translate
from gui.template_base import TemplateBase


class WindowMain(TemplateBase):
    """Launch screen GUI for navigating to primary application features."""

    def __init__(self, master=None):

        super().__init__(title=translate("launch_screen_title"))
        self._setup2()

        self.adjust_to_content(self)

        log.info("Main window opened.")

    def on_closing(self):
        log.info("Main window closed.")
        self.destroy()

    def _open_repak_gui(self):
        from gui.window_repak import WindowRepak

        self.withdraw()
        log.debug("Main window withdrawn.")
        WindowRepak(self)

    def _open_merge_gui(self):
        from gui.window_merge import WindowMerge

        self.withdraw()
        log.debug("Main window withdrawn.")
        WindowMerge(self)

    # !RENAME method
    def _setup2(self):
        self.create_header(self, text=translate("launch_screen_header"))

        buttons_frame = self.create_frame(
            self,
            style="Transparent.CTkFrame",
            padx=self.padding // 2,
            pady=self.padding // 2,
            row_weights=[(0, 1)],
            column_weights=[(0, 1), (1, 1)],
        )
        width = 300
        height = 60
        self.create_button(
            buttons_frame,
            text=translate("launch_screen_button_repak"),
            command=self._open_repak_gui,
            width=width,
            height=height,
            row=0,
            column=0,
            padx=self.padding // 2,
            pady=self.padding // 2,
        )
        self.create_button(
            buttons_frame,
            text=translate("launch_screen_button_merge"),
            command=self._open_merge_gui,
            width=width,
            height=height,
            row=0,
            column=1,
            padx=self.padding // 2,
            pady=self.padding // 2,
        )

        self.create_settings_button(self)
