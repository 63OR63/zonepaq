from app_gui import main
from backend.logger import log

if __name__ == "__main__":
    log.info("Starting the application...")
    main()
    log.info("Application finished.")
