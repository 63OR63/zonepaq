from app_gui import main
from backend.logger import log
from gui.window_launch_screen import GUI_LaunchScreen

if __name__ == "__main__":
    log.info("Starting the application...")
    # main()
    gui = GUI_LaunchScreen()
    gui.mainloop()
    log.info("Application finished.")
