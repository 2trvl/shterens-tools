import logging
from .paths import *

def create_logger(name: str, filename: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fileHandler = os.path.join(botFolderPath, filename)
    fileHandler = logging.FileHandler(fileHandler, "a", "utf-8")
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fileHandler.setFormatter(formatter)
    
    logger.addHandler(fileHandler)
    return logger


logger = create_logger("shterens-tools", "runtime.log")
errors = create_logger("shterens-panic", "critical.log")
