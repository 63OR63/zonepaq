from backend.logger import log


from collections import deque


class InstanceManager:
    """Manages registration and cleanup of windows and widgets."""

    def __init__(self):
        self._reset()

    def register_window(self, window):
        if window not in self.windows:
            log.deep_debug(f"Registering window: {window}")
            self.windows.append(window)

    def unregister_window(self, window):
        if window in self.windows:
            log.deep_debug(f"Unregistering window: {window}")
            self.windows.remove(window)

        for widget in list(self.widgets.keys()):
            if self.widgets[widget] == window:
                log.deep_debug(f"Unregistering widget: {widget} @ {window}")
                self.widgets.pop(widget)

    def register_widget(self, widget, window):
        if widget not in self.widgets:
            log.deep_debug(f"Registering widget: {widget} @ {window}")
            self.widgets[widget] = window

    def _reset(self):
        log.deep_debug("'windows' and 'widgets' instance storages reset.")
        self.windows = deque()
        self.widgets = {}
