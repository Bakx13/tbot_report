import logging
import telegram

# подключаем библиотеку по работе с bpmn-схемами

from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
import bpmn_dmn.bpmn as BPMN

# подключаем свои библиотеки
from tbot_report.lib.nuconfig import NuConfig
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
import tbot_report.lib.worker as Worker
import tbot_report.database.database as db

log = logging.getLogger(__name__)


class Lorder:
    def __init__(self, menuname, printedfl):
        self.menuname = menuname
        self.printedfl = printedfl


class TelegramHandler():
    def __init__(self, worker: Worker, bpmnfile):
        self.keyboard = []
        self.worker = worker
        self.bpmnfile = bpmnfile
        self.bpmnfile = worker.cfg.tbot_home + self.bpmnfile
        # загружем BPMN схему
        # Это для ручной подгрузки workflow, без запуска обработки.
        self.runner = BPMN.BPMNXMLWorkflowRunner(bpmnfile, debug=True)
        package = self.runner.packager.package_in_memory(self.runner.workflowProcessID, self.runner.path,
                                                         self.runner.workflowEditor)
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
        self.keyboard = []
        for menuitem in task_list:
            menuitem = menuitem.task_spec.name
            handler, locname = tMenu.loc_menu[menuitem]
            log.debug(f"add menu point handler = {handler} lname= {locname} to keyboard")
            self.keyboard.append([telegram.KeyboardButton(locname)])
        self.keyboard.reverse()
        log.debug("End set_menu_by_bpmn")
        return
    def call_handler_by_name(self, methodname, *args, **kwargs):
        return getattr(self, methodname)(*args, **kwargs)

class TelegramCoachHandler(TelegramHandler):
    def __init__(self, worker: Worker, bpmnfile):
        super().__init__(worker, bpmnfile)

        # bpmnfile = worker.cfg.tbot_home+"config/Coach.MenuSwimpool.comunda.bpmn"

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

    def SwitchAdminToCoach(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin SwitchAdminToCoach handler")
        # Start the bot in user mode
        log.debug(f"worker = {self.worker}")
        tMenu.coach_menu("MenuStart", "menu_coach_main_txt", self.worker)
        log.debug(f"end admin SwitchAdminToCoach handler")
        return

    def SwimpoolList(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:

        swimpools = self.worker.session.query(db.SwimPool).filter_by(deleted=False).all()
        swimpool_names = [swimpool.name for swimpool in swimpools]


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
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt

    def ClientList(self, tMenu, menuname):
        log.debug(f"begin CoachList handler")
        msg_txt = "menu_coach_main_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt


class TelegramSecondMenu():
    def __init__(self):
        return

    @staticmethod
    def startHandler(worker, updates: telegram.Update):
        worker.bot.send_message(worker.chat.id,
                                f"Ой, вы нажали кнопочку из дополнительного меню с обработчиком: {updates.callback_query.data}")
        return


class TelegramMenu(NuConfig):
    def __init__(self, file: "TextIO", loc: localization, type):
        super().__init__(file)
        self.loc = loc
        # loc_menu = [menu_name = [hadnler_name, display_name]]
        self.loc_menu = {}
        self.localnames = []
        self.handler_list = []
        self.type = ""
        self.keyboard_handler = []
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
        # заполняем настройки из общего конфига
        cfg_file = open(file_menu_path + file_menu, encoding="utf8")
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

        self.loc_menu = []
        self.handler_list = []
        self.keyboard = []
        self.keyboard_handler = []
        # self.keyboard = self.menu.keys()
        for menuitem in self.menu.keys():
            # menuitem = self.menu[menuitem]
            # log.debug(f"add menu point {menuitem} to keyboard")
            self.keyboard.append([telegram.KeyboardButton(self.loc.get(menuitem))])
            self.loc_menu.append(self.loc.get(menuitem))
            self.handler_list.append(self.menu[menuitem])
            tmp = [self.menu[menuitem], self.loc.get(menuitem)]
            self.keyboard_handler.append(tmp)

    def draw_menu(self, header_txt, worker: Worker, menu_type, handlerclass, camunda_schema, menustart):
        get_class = lambda x: globals()[x]
        c = get_class(handlerclass)
        log.debug(f"worker in draw_menu {worker}")
        classHandler = c(worker, camunda_schema)
        #exec("classHandler =" + handlerclass + f"(worker,camunda_schema)")
        # classHandler = type(classHandler, (object, ), dict())
        classHandler.set_menu_by_bpmn(menustart, self)
        keyboard = classHandler.get_keyboard()
        log.debug(f"Displaying {menu_type}")
        needupdatekeyboard = True
        # Loop used to returning to the menu after executing a command
        while True:
            # Send the previously created keyboard to the user (ensuring it can be clicked only 1 time)
            if (needupdatekeyboard):
                worker.bot.send_message(worker.chat.id, worker.loc.get(header_txt),
                                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                                  resize_keyboard=True))
            # Wait for a reply from the user
            # log.debug(f"get loc menu worker: {self.keyboard_handler}")
            selection = worker.wait_for_specific_message(self.localnames)
            # Если сделали выбор из второго меню.
            needupdatekeyboard = True
            if isinstance(selection, telegram.Update):
                TelegramSecondMenu.startHandler(worker, selection)
                needupdatekeyboard = False
                continue
            handlername = self.get_handler_by_displayname(selection)
            menuname = self.get_name_by_displayname(selection)
            log.debug(f"worker menu selected name: {selection}")
            log.debug(f"worker menu selected {handlername}")

            # After the user reply, update the user data
            worker.update_user()

            # Вызываем обработчик в зависимости от выбранной команды.
            #try:
            keyboard, header_txt = classHandler.call_handler_by_name(handlername, self, menuname)
            #m = getattr(classHandler, handlername)
            #keyboard, header_txt = m(classHandler, menuname)
            #except AttributeError as exc:
            #    header_txt = "menu_all_inbuilding_txt"
        return

    def coach_menu(self, menustart, header_txt, worker: Worker):
        log.debug(f"Start coach_menu")
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__(menu_file, self.loc, "Coach")
        # @todo не забыть убрать. Только для теста красивого меню
        self.send_msg_nicekeyboard(worker)

        self.draw_menu(header_txt, worker, "Coach", "TelegramCoachHandler", "config/comunda_coach_menu.bpmn",
                       menustart)
        return

    def admin_menu(self, name, header_txt, worker: Worker):
        '''Work in admin menu'''
        # переопределяем сами себя из-за возможного перехода из другого режима, например Coach -> Admin
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__(menu_file, self.loc, "Admin")

        header_txt = "menu_admin_main_txt"
        self.draw_menu(header_txt, worker, "Admin", "TelegramAdminHandler", "config/comunda_admin_menu.bpmn",
                       "MenuStart")
        '''
            # If the user has selected the Products option...
            if selection == self.loc.get("menu_products"):
                # Open the products menu
                self.__products_menu()
            # If the user has selected the Orders option...
            elif selection == self.loc.get("menu_orders"):
                # Open the orders menu
                self.__orders_menu()
            # If the user has selected the Transactions option...
            elif selection == self.loc.get("menu_edit_credit"):
                # Open the edit credit menu
                self.__create_transaction()
            # If the user has selected the User mode option...
            elif selection == self.loc.get("menu_admin_user_mode"):
                # Tell the user how to go back to admin menu
                self.bot.send_message(self.chat.id, self.loc.get("conversation_switch_to_user_mode"))
                # Start the bot in user mode
                self.__user_menu()
            # If the user has selected the Add Admin option...
            elif selection == self.loc.get("menu_edit_admins"):
                # Open the edit admin menu
                self.__add_admin()
            # If the user has selected the Transactions option...
            elif selection == self.loc.get("menu_transactions"):
                # Open the transaction pages
                self.__transaction_pages()
            # If the user has selected the .csv option...
            elif selection == self.loc.get("menu_csv"):
                # Generate the .csv file
                self.__transactions_file()
        '''
