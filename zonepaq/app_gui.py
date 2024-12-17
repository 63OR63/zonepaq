from gui.custom_set_titlebar_icon import CTk
from gui.gui_main import GUI_LaunchScreen


class App(CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        gui = GUI_LaunchScreen()
        gui.mainloop()


def main():
    app = App()
    app.mainloop()
