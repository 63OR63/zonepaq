import sys
from backend.logger import log
from config.settings import translate
from gui.template_base import GUI_Base


class GUI_LaunchScreen(GUI_Base):
    """Launch screen GUI for navigating to primary application features."""

    def __init__(self, master=None):
        super().__init__(title=translate("launch_screen_title"))
        self._setup2()

        self.adjust_to_content(self)

        log.info("Launch screen opened.")

    def on_closing(self):
        self.destroy()

    def _open_repak_gui(self):
        from gui.window_repak_screen import GUI_RepakScreen

        self.withdraw()
        GUI_RepakScreen(self)

    def _open_merge_gui(self):
        from gui.window_merge_screen import GUI_MergeScreen

        self.withdraw()
        GUI_MergeScreen(self)

    # !RENAME method
    def _setup2(self):
        self.create_header(self, text=translate("launch_screen_header"))

        buttons = {
            "custom": [
                {
                    "text": translate("launch_screen_button_repak"),
                    "width": 300,
                    "height": 60,
                    "command": self._open_repak_gui,
                    "row": 0,
                    "column": 0,
                },
                {
                    "text": translate("launch_screen_button_merge"),
                    "width": 300,
                    "height": 60,
                    "command": self._open_merge_gui,
                    "row": 0,
                    "column": 1,
                },
            ],
            "grid": {"padx": self.padding // 2, "pady": self.padding // 2},
        }

        self.create_buttons(
            buttons,
            self,
            frame_grid_args={
                "row": 1,
                "column": 0,
                "padx": self.padding // 2,
                "pady": self.padding // 2,
            },
            row_weights=[(0, 1)],
            column_weights=[(0, 1), (1, 1)],
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
