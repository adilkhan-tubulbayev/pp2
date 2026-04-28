import os
from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    if not os.path.exists(filename):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    parser.read(filename)
    config = {}
    if parser.has_section(section):
        for param in parser.items(section):
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')
    return config
