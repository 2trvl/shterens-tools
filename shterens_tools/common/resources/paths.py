import os

def get_root_path() -> str:
    return os.path.abspath(os.curdir)

def get_bot_folder_path() -> str:
    return os.path.join(get_root_path(), "shterens_tools")

rootPath = get_root_path()
botFolderPath = get_bot_folder_path()
