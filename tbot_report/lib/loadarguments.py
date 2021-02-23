import sys
import argparse

class ArgParses(object):
    """Класс для обработки аргументов запуска"""
    def __init__(self):
        """Constructor"""
        self.configname = "config/config"
    pass
    def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-e', '--env', choices=['dev', 'test', 'prod'], default='prod')
        parser.add_argument('-p', '--programmist', choices=['anton', 'konstantin'], default='konstantin')
        #namespace = parser.parse_args(sys.argv[1:])
        namespace = parser.parse_args()
        return namespace
