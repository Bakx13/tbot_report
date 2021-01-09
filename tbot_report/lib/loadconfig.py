import logging
log = logging.getLogger(__name__)

class MyConfig(object):
    """Класс для работы с картинками"""

    def __init__(self):
        """Constructor"""
        self.configname = "config/config"
    def load(self):
        log.debug("load config")
