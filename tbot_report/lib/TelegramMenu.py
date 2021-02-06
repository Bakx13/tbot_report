import logging
import toml
import telegram
#подключаем библиотеку по работе с bpmn-схемами

from SpiffWorkflow import Task
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser, full_tag
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.serializer.Packager import Packager
from SpiffWorkflow.bpmn.specs import ExclusiveGateway
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from bpmn_dmn.bpmn import BPMNXMLWorkflowRunner

#подключаем свои библиотеки
from tbot_report.lib.nuconfig import NuConfig
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
import tbot_report.lib.worker as Worker
import tbot_report.lib.utils as utils

log = logging.getLogger(__name__)

class Lorder:
    def __init__(self, menuname,printedfl):
        self.menuname = menuname
        self.printedfl = printedfl

class TelegramHandler():
    def __init__(self, worker: Worker, bpmnfile):
        self.keyboard = []
        self.worker = worker
        self.bpmnfile = bpmnfile
        self.bpmnfile = worker.cfg.tbot_home+self.bpmnfile
        #загружем BPMN схему
        #Это для ручной подгрузки workflow, без запуска обработки.
        self.runner = BPMNXMLWorkflowRunner(bpmnfile, debug=True)
        package = self.runner.packager.package_in_memory(self.runner.workflowProcessID, self.runner.path, self.runner.workflowEditor)
        workflowSpec = BpmnSerializer().deserialize_workflow_spec(package)
        self.runner.workflow = BpmnWorkflow(workflowSpec, **self.runner.kwargs)
        return
    def get_keyboard(self):
        return self.keyboard
    def set_menu_by_bpmn(self, step_name, tMenu):
        log.debug("Start set_menu_by_bpmn")
        task = self.runner.workflow.get_tasks_from_spec_name(step_name)
        task_list = task[0].children
        log.debug(f"task_list: {task_list}")
        # Если дошли до конца - возвращаемся на стартовую страницу
        if not task_list:
            task = self.runner.workflow.get_tasks_from_spec_name("MenuStart")
            task_list = task[0].children
        self.keyboard=[]
        for menuitem in task_list:
            menuitem = menuitem.task_spec.name
            handler, locname = tMenu.loc_menu[menuitem]
            log.debug(f"add menu point handler = {handler} lname= {locname} to keyboard")
            self.keyboard.append([telegram.KeyboardButton(locname)])
        self.keyboard.reverse()
        log.debug("End set_menu_by_bpmn")
        return


class TelegramQoachHandler(TelegramHandler):
    def __init__(self, worker: Worker, bpmnfile):
        super().__init__(worker, bpmnfile)

        #bpmnfile = worker.cfg.tbot_home+"config/Coach.MenuSwimpool.comunda.bpmn"
    def runBPMN(self):
        log.debug("балуемся с комундой")
        return
    def SwimpoolList(self, tMenu, menuname):
        log.debug(f"begin Swimpoollist handler")
        msg_txt = "menu_all_swimpool_list_text"
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        log.debug(f"end Swimpoollist handler")
        return keyboard, msg_txt
    def AddSwimpool(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt
    def DelSwimpool(self, tMenu, menuname):
        log.debug(f"begin Del_Swimpool handler")
        msg_txt = "menu_all_swimpool_list_text"
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt
    def Cancel(self, tMenu, menuname):
        log.debug(f"begin Cancel handler")
        msg_txt = "menu_coach_main_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        log.debug(f"begin Cancel handler")
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt

class TelegramAdminHandler(TelegramHandler):
    def __init__(self, worker: Worker, bpmnfile):
        super().__init__(worker, bpmnfile)

    def SwitchAdminToCoach(self, tMenu, worker: Worker):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin SwitchAdminToCoach handler")
        # Start the bot in user mode
        tMenu.coach_menu("MenuStart", "menu_coach_main_txt", worker)
        return
    def SwimpoolList(self, tMenu, worker: Worker):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        tMenu.set_menu_by_type("Admin")
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
    def __init__(self, file: "TextIO", loc: localization, type):
        super().__init__(file)
        self.loc = loc
        # loc_menu = [menu_name = [hadnler_name, display_name]]
        self.loc_menu = {}
        self.localnames = []
        self.handler_list = []
        self.type = ""
        self.keyboard_handler=[]
        log.debug(f"self.data={self.data}")
        self.menu = self.data[type]
        log.debug(f"self.menu={self.menu}")
        for menuitem in self.menu.values():
            for mnt, handler in menuitem.items():
                self.loc_menu[mnt] = [handler, loc.get(mnt)]
                self.localnames.append(loc.get(mnt))
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def get_name_by_displayname(self, display_name):
        for i in self.loc_menu:
            a, b = self.loc_menu[i]
            if b == display_name: return i
        return None
    def get_handler_by_displayname(self, name):
        for mnt in self.loc_menu:
            a, b = self.loc_menu[mnt]
            if (b == name): return a
        return None
    @staticmethod
    def get_menu_file(cfg: MConfig, type):
        log.debug(f"get menu file for {type}")
        file_menu_path = cfg.menu_dir
        file_menu = cfg.menu[type]
        #заполняем настройки из общего конфига
        cfg_file = open(file_menu_path+file_menu, encoding="utf8")
        return cfg_file
    @staticmethod
    def send_msg_nicekeyboard(worker):
        keyboard = [[telegram.InlineKeyboardButton("Hackerearth", callback_data='HElist8'),
                     telegram.InlineKeyboardButton("Hackerrank", callback_data='HRlist8')],
                    [telegram.InlineKeyboardButton("Codechef", callback_data='CClist8'),
                     telegram.InlineKeyboardButton("Spoj", callback_data='SPlist8')],
                    [telegram.InlineKeyboardButton("Codeforces", callback_data='CFlist8'),
                     telegram.InlineKeyboardButton("ALL", callback_data='ALLlist8')]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        worker.bot.send_message(worker.chat.id, 'please select the judge or select all for showing all',
                              reply_markup=reply_markup)

    def get_menuname_by_name(self, name):
        return self.loc_menu[name][1]

    def get_keyboard_by_menus(self, menus):
        keyboard = []
        for menu in menus:
            keyboard.append(self.loc_menu[menu][1])
        return keyboard

    def set_menu_by_bpmn(self, name):
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
            self.keyboard.append([telegram.KeyboardButton(self.loc.get(menuitem))])
            self.loc_menu.append(self.loc.get(menuitem))
            self.handler_list.append(self.menu[menuitem])
            tmp=[self.menu[menuitem],self.loc.get(menuitem)]
            self.keyboard_handler.append(tmp)

    def coach_menu(self, name, header_txt, worker: Worker):
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__(menu_file, self.loc,  "Coach")
        qoachHandler = TelegramQoachHandler(worker, "config/comunda_coach_menu.bpmn")
        qoachHandler.set_menu_by_bpmn("MenuStart", self)
        header_txt = "menu_coach_main_txt"
        keyboard = qoachHandler.get_keyboard()
        self.send_msg_nicekeyboard(worker)
        log.debug("Displaying coach_menu")

        # Loop used to returning to the menu after executing a command
        while True:

            # Send the previously created keyboard to the user (ensuring it can be clicked only 1 time)
            worker.bot.send_message(worker.chat.id, worker.loc.get(header_txt),
                                  reply_markup=telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
            # Wait for a reply from the user
            #log.debug(f"get loc menu worker: {self.keyboard_handler}")
            selection = worker.wait_for_specific_message(self.localnames)
            handlername = self.get_handler_by_displayname(selection)
            menuname = self.get_name_by_displayname(selection)
            log.debug(f"worker menu selected name: {selection}")
            log.debug(f"worker menu selected {handlername}")

            # After the user reply, update the user data
            worker.update_user()

            #Вызываем обработчик в зависимости от выбранной команды.
            try:
                m = getattr(TelegramQoachHandler, handlername)
                keyboard, header_txt = m(qoachHandler, self, menuname)
            except AttributeError as exc:
                header_txt = "menu_all_inbuilding_txt"
        return

