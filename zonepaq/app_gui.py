from gui.window_launch_screen import GUI_LaunchScreen

# from gui.ctk_wraps import CTk
# class App(CTk):
#     def __init__(self):
#         super().__init__()
#         self.withdraw()
#         gui = GUI_LaunchScreen()
#         gui.mainloop()


class App:
    def __init__(self):
        gui = GUI_LaunchScreen()
        gui.mainloop()


def main():
    app = App()
    app.mainloop()
