import os
from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()

    if not os.path.exists(filename):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    parser.read(filename)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

if __name__ == '__main__':
    config = load_config()
    print(config)
