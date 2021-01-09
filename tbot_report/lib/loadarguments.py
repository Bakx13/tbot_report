import sys
import argparse

class ArgParses():
    """Класс для обработки аргументов запуска"""
    def __init__(self):
        """Constructor"""
        self.configname = "config/config"
    pass
    def createParser ():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-t', '--type', choices=['dev', 'test', 'prod'], default='prod')
        namespace = parser.parse_args(sys.argv[1:])
        return namespace


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    print (namespace)

    print ("Привет, {}!".format (namespace.name) )