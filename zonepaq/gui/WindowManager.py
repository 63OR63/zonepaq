import sys


# !WORKAROUND for CTk spawning errors in logs due to delayed calls on destroyed windows
class WindowManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent):
        if not hasattr(self, "initialized"):
            self.open_windows = {type(parent): parent}
            self.initialized = True

    def open_window(self, parent, new_window, toplevel=False):
        print(self.open_windows)
        if new_window in self.open_windows:
            window = self.open_windows[new_window]
            if not toplevel:
                parent.withdraw()
            window.iconify()  # reduces flashing
            window.after_idle(window.deiconify)
        else:
            if not toplevel:
                parent.withdraw()
            window = new_window()
            self.open_windows[new_window] = window
            window.mainloop()
            window.iconify()  # reduces flashing
            window.after_idle(window.deiconify)

    def close_window(self, parent, forced=False):
        """Close the current window."""
        if forced:
            parent.destroy()
            sys.exit(0)
        else:
            parent.withdraw()
            self.open_windows[type(parent)] = parent
