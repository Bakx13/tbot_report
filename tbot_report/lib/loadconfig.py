import logging
from tbot_report.lib.nuconfig import NuConfig

log = logging.getLogger(__name__)

class MyConfig(object):
    """Класс для загрузки конфигов"""

    def __init__(self):
        """Constructor"""
        self.configname = "config/config"
        self.logs_dir = ""
        self.log_level = ""
        self.env_conf = ""
        self.tbot_home = ""
        self.log_format = ""
        self.telegram = {}
        self.telegram_proxy_string = ""
        self.language = {}
        self.database = {}
        self.payments = {}
        self.ccard = {}
        self.appearance = {}
        self.menu_dir = ""
        self.menu = {}
        self.test_data = ""
    def Load(self, file_conf, env_level, dev_name):
        log.debug("load config")
        #заполняем настройки из общего конфига
        cfg_file = open(file_conf, encoding="utf8")
        common_cfg = NuConfig(cfg_file)
        #каталог для хранения логов
        self.log_dir = common_cfg["Path"]["logs_dir"]
        #домашний каталог бота (лучше не пользоваться до создания инсталлятора)
        self.tbot_home = common_cfg["Path"]["tbot_home"]
        self.menu_dir = common_cfg["Path"]["menu_dir"]
        #названия файлов с меню для каждой роли
        self.menu = common_cfg["Menu"]
        #параметры для локализации
        self.language["enabled_languages"] = common_cfg["Language"]["enabled_languages"]
        self.language["default_language"] = common_cfg["Language"]["default_language"]
        self.language["fallback_language"] = common_cfg["Language"]["fallback_language"]

        #TODO не забыть удалить, когда переделаю worker
        # Bot appearance settings
        self.appearance["full_order_info"] = common_cfg["Appearance"]["full_order_info"]
        self.appearance["refill_on_checkout"] = common_cfg["Appearance"]["refill_on_checkout"]
        self.appearance["display_welcome_message"] = common_cfg["Appearance"]["display_welcome_message"]
        #выбираем среду запуска программы: dev, test, prod
        tmp = {
            'dev': common_cfg["Path"]["dev_conf"],
            'test': common_cfg["Path"]["test_conf"],
            'prod': common_cfg["Path"]["prod_conf"],
        }
        #Трудности одновременной отладки. Поэтому конфиг в режиме дев для каждого разрабочика свои.
        if env_level == 'dev':
            CONFIG_FILE = f"{tmp[env_level]}_{dev_name}.toml"
        else:
            CONFIG_FILE = tmp[env_level]
        cfg_file.close()
        #Загружаем конфиг среды запуска
        log.debug("Open env config: "+CONFIG_FILE)
        cfg_file = open(CONFIG_FILE, encoding="utf8")
        common_cfg = NuConfig(cfg_file)
        self.log_level = common_cfg["Logging"]["level"]
        log.debug("log_level: "+self.log_level)
        self.log_format = common_cfg["Logging"]["format"]
        log.debug("log_format: "+self.log_format)
        self.telegram["token"] = common_cfg["Telegram"]["token"]
        self.telegram["proxy_string"] = common_cfg["Telegram"]["proxy_string"]
        self.telegram["conversation_timeout"] = common_cfg["Telegram"]["conversation_timeout"]
        self.telegram["long_polling_timeout"] = common_cfg["Telegram"]["long_polling_timeout"]
        self.telegram["timed_out_pause"] = common_cfg["Telegram"]["timed_out_pause"]
        self.telegram["error_pause"] = common_cfg["Telegram"]["error_pause"]
        log.debug("Конфиг телеги:")
        log.debug(self.telegram)
        self.database["engine"] = common_cfg["Database"]["engine"]
        #на всякий случай, чтобы не затереть пром. данные. Всякое бывает.
        if env_level == 'dev':
            self.test_data = common_cfg["Path"]["test_data"]
        return

