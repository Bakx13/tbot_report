import logging
import toml
import telegram


#подключаем свои библиотеки
from tbot_report.lib.nuconfig import NuConfig
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
import tbot_report.lib.worker as Worker

log = logging.getLogger(__name__)


class TelegramHandler():
    def __init__(self):
        return
class TelegramQoachHandler(TelegramHandler):
    def __init__(self):
        super().__init__()
    def SwimpoolList(self, tMenu, worker: Worker):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        tMenu.set_menu_by_type("Coach")
        tMenu.set_menu_by_name("MenuSwimpool", worker.loc)
        keyboard = tMenu.get_keyboard()
        return keyboard, msg_txt
    def AddSwimpool(self, tMenu, worker: Worker):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        tMenu.set_menu_by_type("Coach")
        tMenu.set_menu_by_name("MenuSwimpool", worker.loc)
        keyboard = tMenu.get_keyboard()
        return keyboard, msg_txt
    def DelSwimpool(self, tMenu, worker: Worker):
        log.debug(f"begin Del_Swimpool handler")
        msg_txt = "menu_all_swimpool_list_text"
        # переопределяем клавиатуру для выбранного пункта меню
        tMenu.set_menu_by_type("Coach")
        tMenu.set_menu_by_name("MenuSwimpool", worker.loc)
        keyboard = tMenu.get_keyboard()
        return keyboard, msg_txt
    def Cancel(self, tMenu, worker: Worker):
        log.debug(f"begin Cancel handler")
        msg_txt = "menu_coach_main_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        tMenu.set_menu_by_type("Coach")
        tMenu.set_menu_by_name("MenuStart", worker.loc)
        keyboard = tMenu.get_keyboard()
        return keyboard, msg_txt
class TelegramMenu(NuConfig):
    def __init__(self, file: "TextIO"):
        super().__init__(file)
        self.menu = {}
        self.loc_menu = []
        self.handler_list = []
        self.type = ""
        self.keyboard = []
        self.keyboard_handler=[]
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    @staticmethod
    def get_menu_file(cfg: MConfig, type):
        log.debug(f"get menu file for {type}")
        file_menu_path = cfg.menu_dir
        file_menu = cfg.menu[type]
        #заполняем настройки из общего конфига
        cfg_file = open(file_menu_path+file_menu, encoding="utf8")
        return cfg_file

    def get_menu_by_name(self, type, name):
        log.debug(f"get menu by {type} and {name}")
        if (not type): return None
        if (name): return self.data[type][name]
        return self.data[type]

    def set_menu_by_type(self, type):
        log.debug(f"set menu by {type}")
        if (not type): return None
        self.type = type
        log.debug(f"set menu = {self.data}")
        self.menu = self.data[type]

    def set_menu_by_name(self, name, loc: localization):
        log.debug(f"set menu by {name}")
        if (not self.type):
            log.error(f"type menu is not set")
            return None
        self.menu = self.data[self.type][name]
        log.debug(f"menu setting: {self.menu}")

        self.loc_menu=[]
        self.handler_list=[]
        self.keyboard=[]
        self.keyboard_handler=[]
        #self.keyboard = self.menu.keys()
        for menuitem in self.menu.keys():
            #menuitem = self.menu[menuitem]
            #log.debug(f"add menu point {menuitem} to keyboard")
            self.keyboard.append([telegram.KeyboardButton(loc.get(menuitem))])
            self.loc_menu.append(loc.get(menuitem))
            self.handler_list.append(self.menu[menuitem])
            tmp=[self.menu[menuitem],loc.get(menuitem)]
            self.keyboard_handler.append(tmp)

    def get_keyboard(self):
        return self.keyboard