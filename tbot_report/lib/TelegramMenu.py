import logging

import bpmn_dmn.bpmn as BPMN
import telegram
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

import tbot_report.database.database as db
import tbot_report.lib.loadconfig as MConfig
import tbot_report.lib.worker as Worker
import tbot_report.localization.localization as localization
# подключаем свои библиотеки
from tbot_report.lib.nuconfig import NuConfig

# подключаем библиотеку по работе с bpmn-схемами

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

    def get_parent_menu(self, step_name):
        log.debug("Start get_parent_menu")
        task = self.runner.workflow.get_tasks_from_spec_name(step_name)
        try:
            return task[0].parent.task_spec.name
        except:
            return None
        return None

    def set_menu_by_bpmn(self, step_name, tMenu):
        log.debug("Start set_menu_by_bpmn")
        task = self.runner.workflow.get_tasks_from_spec_name(step_name)
        task_list = task[0].children
        log.debug(f'task_list: {task_list}')
        # Если дошли до конца - возвращаемся на стартовую страницу
        if not task_list:
            task = self.runner.workflow.get_tasks_from_spec_name("MenuStart")
            task_list = task[0].children
        self.keyboard = []
        for_menus = []
        for menuitem in task_list:
            try:
                menuitem_desc = menuitem.task_spec.description.split('#')
                menuitem_id = menuitem_desc[0]
            except:
                log.debug(
                    f"Ошибка в формировании bpmn-схемы. Поле Description должно быть формата 1#Описание, где 1 - это порядковый номер меню.")
                return
            menuitem = menuitem.task_spec.name
            handler, locname = tMenu.loc_menu[menuitem]
            log.debug(f"add menu point handler = {handler} lname= {locname} to keyboard")
            for_menus.append((menuitem_id, menuitem, handler, locname))
        for_menus = sorted(for_menus, key=lambda menu: menu[0])
        for menuitem_id, menuitem, handler, locname in for_menus:
            self.keyboard.append([telegram.KeyboardButton(locname)])
        # self.keyboard.reverse()
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
        tMenu.coach_menu("MenuStart", "menu_coach_main_txt", self.worker)
        log.debug(f"end admin SwitchAdminToCoach handler")
        return

    def SwitchAdminToUser(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin SwitchAdminToUser handler")
        # Start the bot in user mode
        tMenu.user_menu("MenuStart", "menu_coach_main_txt", self.worker)
        log.debug(f"end admin SwitchAdminToUser handler")
        return

    def SwimpoolList(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:
        if self.worker.second_menu is None:
            menu = TelegramSecondMenu(self.worker)
            self.worker.second_menu = menu
        reply_markup = self.worker.second_menu.SwimpoolList(0)
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список бассейнов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def AddSwimpool(self, tMenu, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        sw_fileds = TelegramSecondMenu.collect_object_fields(self.worker,
                                                             [self.worker.loc.get("questions_name"),
                                                              self.worker.loc.get("questions_address"),
                                                              self.worker.loc.get("questions_swimpool_cost")],
                                                             [])
        swpool = db.SwimPool(distict_id=1, timetable_id=1, address=sw_fileds[1], name=sw_fileds[0], price=sw_fileds[2])
        self.worker.session.add(swpool)
        self.worker.session.commit()
        return keyboard, msg_txt

    def DelSwimpool(self, tMenu, menuname):
        log.debug(f"begin TelegramAdminHandler.Del_Swimpool handler")
        msg_txt = "menu_all_swimpool_list_text"
        # переопределяем клавиатуру для выбранного пункта меню
        try:
            sw = self.worker.session.query(db.SwimPool).filter_by(id=self.worker.second_menu.object_id,
                                                                  deleted=False).one()
            sw.deleted = True
            self.worker.session.commit()
            #удалили, теперь обновляем менюшечку с бассейнами
            message = self.worker.bot.last_message_inline_keyboard
            reply_markup = self.worker.second_menu.SwimpoolList(0)
            self.worker.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=message.message_id,
                                                      reply_markup=reply_markup)
            log.debug(f"Удаляем бассейн с именем:{sw.name} и id: {sw.id}")
        except:
            self.worker.bot.send_message(self.worker.chat.id, "Вы не выбрали бассейн для удаления")
        menuname = self.get_parent_menu(menuname)

        self.set_menu_by_bpmn(menuname, tMenu)
        keyboard = self.get_keyboard()
        log.debug(f"menuname={menuname}")
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
    def __init__(self, worker: Worker):
        self.worker = worker
        self.object_id = 0
        self.handler_name = None

    @staticmethod
    def startHandler(worker, updates: telegram.Update):
        message = worker.bot.last_message_inline_keyboard
        callback_query = updates.callback_query.data
        lst = callback_query.split('#')
        handlername = lst[0]
        object_id = lst[1]
        if worker.second_menu is None:
            menu = TelegramSecondMenu(worker)
            worker.second_menu = menu
        worker.second_menu.object_id = object_id
        worker.second_menu.handler_name = handlername
        reply_markup = worker.second_menu.call_handler_by_name(handlername, object_id)
        try:
            msg_id = message.message_id
        except:
            log.debug(f"Ой-ой. Кто-то позвал обработчик, а сообщений то не было!")
            return
        # за каким-то лешим если отправить в edit_message_reply_markup тоже самое меню,
        # то api telegram выдает исключение
        if (reply_markup.__eq__(worker.bot.last_message_inline_keyboard.reply_markup)):
            # @todo не забыть убрать в localization
            worker.bot.send_message(worker.chat.id, "Пункт меню уже выбран")
        else:
            worker.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=msg_id,
                                                 reply_markup=reply_markup)
        return

    def SwimpoolList(self, object_id: int):
        log.debug(f"begin SwimpoolList second menu handler")
        swimpools = self.worker.session.query(db.SwimPool).filter_by(deleted=False).all()
        object_id = int(object_id)
        keyboard_nice = []
        keyboard_nice.append([telegram.InlineKeyboardButton("Название бассейна", callback_data="none"),
                              telegram.InlineKeyboardButton("Стоимость", callback_data="none"),
                              telegram.InlineKeyboardButton("Выбрать", callback_data="none")])
        for swimpool in swimpools:
            sw_id = int(swimpool.id)
            swimpool_name = str(swimpool.name)
            if swimpool.price is None:
                swimpool_price = "не задана"
            else:
                swimpool_price = str(swimpool.price)

            # @todo не забыть убрать в localization"
            choice = "✔️"
            if sw_id == object_id: choice = f"✅"
            keyboard_nice.append([telegram.InlineKeyboardButton(swimpool_name, callback_data="none"),
                                  telegram.InlineKeyboardButton(swimpool_price, callback_data="none"),
                                  telegram.InlineKeyboardButton(choice, callback_data=f"SwimpoolList#{sw_id}")])

        reply_markup = telegram.InlineKeyboardMarkup(keyboard_nice)
        return reply_markup

    @staticmethod
    def draw_selected_menu(worker, updates: telegram.Update):
        return

    @staticmethod
    def collect_object_fields(worker, user_questions, stopwordlst):
        lst = []
        for user_question in user_questions:
            worker.bot.send_message(worker.chat.id, f"{user_question}")
            # Get the next update
            update = worker.receive_next_update()
            # Check if the message is contained in the list
            if update.message.text in stopwordlst:
                return None
            lst.append(update.message.text)
        return lst

    def call_handler_by_name(self, methodname, *args, **kwargs):
        return getattr(self, methodname)(*args, **kwargs)


class TelegramMenu(NuConfig):
    def __init__(self, file: "TextIO", loc: localization, type):
        super().__init__(file)
        self.loc = loc
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
            if b == name: return a
        return None

    @staticmethod
    def get_menu_file(cfg: MConfig, type):
        log.debug(f"get menu file for {type}")
        file_menu_path = cfg.menu_dir
        file_menu = cfg.menu[type]
        # заполняем настройки из общего конфига
        cfg_file = open(file_menu_path + file_menu, encoding="utf8")
        return cfg_file

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
        # exec("classHandler =" + handlerclass + f"(worker,camunda_schema)")
        # classHandler = type(classHandler, (object, ), dict())
        classHandler.set_menu_by_bpmn(menustart, self)
        keyboard = classHandler.get_keyboard()
        log.debug(f"Displaying {menu_type}")
        needupdatekeyboard = True
        # Loop used to returning to the menu after executing a command
        while True:
            #если предыдущее сообщение такое же, не будем дублировать
            if str(worker.bot.last_message.text_html).__eq__(worker.loc.get(header_txt)): needupdatekeyboard = False
            # Send the previously created keyboard to the user (ensuring it can be clicked only 1 time)
            if needupdatekeyboard:
                worker.bot.send_message(worker.chat.id, worker.loc.get(header_txt),
                                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=False,
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
            # try:
            keyboard, header_txt = classHandler.call_handler_by_name(handlername, self, menuname)
            # m = getattr(classHandler, handlername)
            # keyboard, header_txt = m(classHandler, menuname)
            # except AttributeError as exc:
            #    header_txt = "menu_all_inbuilding_txt"
        return

    def coach_menu(self, menustart, header_txt, worker: Worker):
        log.debug(f"Start coach_menu")
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__(menu_file, self.loc, "Coach")
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

    def user_menu(self, menustart, header_txt, worker: Worker):
        log.debug(f"Start coach_menu")
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__(menu_file, self.loc, "User")
        self.draw_menu(header_txt, worker, "User", "TelegramCoachHandler", "config/comunda_user_menu.bpmn",
                       menustart)
        return
