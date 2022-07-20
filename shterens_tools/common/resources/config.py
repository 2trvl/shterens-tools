import sys
import configparser
from .paths import *

def generate_config(configPath):
    config = configparser.ConfigParser()
    #  Change option parser to preserve uppercase letters
    config.optionxform = lambda option: option

    config.add_section("BotAPI")
    config.set("BotAPI", "botToken", "None")

    config.add_section("MTProtoAPI")
    config.set("MTProtoAPI", "apiId", "None")
    config.set("MTProtoAPI", "apiHash", "None")

    config.add_section("MultipleInstances")
    config.set("MultipleInstances", "enable", "False")
    config.set("MultipleInstances", "instances", "1")
    config.set("MultipleInstances", "ngrokAuthtoken", "xxxxxxxxxxxx")

    if sys.platform == "win32":
        config.set("MultipleInstances", "nginxFolderPath", "C:\\nginx")

    with open(configPath, "w") as configFile:
        config.write(configFile)

    raise ValueError(f"Fill your config file : {configPath}")


def read_config():
    '''
    Reads config, if does not exist generates one

    '''
    configPath = os.path.join(rootPath, "config.ini")

    if not os.path.exists(configPath):
        generate_config(configPath)
    
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    config.read(configPath)

    for section in config.sections():
        if "None" in dict(config.items(section)).values():
            raise ValueError(f"Fill your config file : {configPath}")

    return config


config = read_config()
