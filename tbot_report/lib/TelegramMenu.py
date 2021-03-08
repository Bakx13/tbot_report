import logging
import inspect
import sys
import traceback
import re

import bpmn_dmn.bpmn as BPMN
import telegram
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

import tbot_report.database.database as db
import tbot_report.lib.loadconfig as MConfig
import tbot_report.lib.worker as Worker
import tbot_report.localization.localization as localization
import tbot_report.lib.utils as utils
# подключаем свои библиотеки
from tbot_report.lib.nuconfig import NuConfig

# подключаем библиотеку по работе с bpmn-схемами

log = logging.getLogger(__name__)


class Lorder:
    def __init__(self, menuname, printedfl):
        self.menuname = menuname
        self.printedfl = printedfl


class TelegramHandler():
    def __init__(self, worker: Worker):
        self.keyboard = []
        self.worker = worker
        return

    def get_keyboard(self):
        return self.keyboard


    def call_handler_by_name(self, methodname, *args, **kwargs):
        return getattr(self, methodname)(*args, **kwargs)


class TelegramCoachHandler(TelegramHandler):
    def __init__(self, worker: Worker):
        super().__init__(worker)
        return

    def runBPMN(self):
        log.debug("балуемся с комундой")
        return

    def SwimpoolList(self, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin coach Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuCoach(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_coach = menu
        reply_markup = self.worker.second_menu_coach.SwimpoolList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список бассейнов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def AddSwimpool(self, menuname):
            msg_txt = "menu_all_swimpool_list_text"
            log.debug(f"begin Swimpoollist handler")
            # переопределяем клавиатуру для выбранного пункта меню
            self.worker.menu.set_menu_by_bpmn(menuname)
            keyboard = self.get_keyboard()
            sw_fileds = TelegramSecondMenuCoach.collect_object_fields(self.worker,
                                                                      [self.worker.loc.get("questions_name"),
                                                                       self.worker.loc.get("questions_address"),
                                                                       self.worker.loc.get("questions_swimpool_cost"),
                                                                       self.worker.loc.get("questions_timetableitem_day"),
                                                                       self.worker.loc.get("questions_timetableitem_start"),
                                                                       self.worker.loc.get("questions_timetableitem_end")
                                                                       ],
                                                                      [])
            timetableitem = db.TimeTableItem(day_of_week = sw_fileds[3], start_time = sw_fileds[4], end_time = sw_fileds[5])
            log.debug(f"timetableitem:{timetableitem}")

            self.worker.session.add(timetableitem)
            self.worker.session.commit()

            swpool = db.SwimPool(distict_id=1, timetable_id=1, address=sw_fileds[1], name=sw_fileds[0],
                                 price=sw_fileds[2])
            self.worker.session.add(swpool)
            self.worker.session.commit()
            return keyboard, msg_txt

    def AddAddressSwimPool(self, message):
        self.worker.bot.send_message(self.worker.chat.id, message)
        return

    def DelSwimpool(self, menuname):
        log.debug(f"begin Del_Swimpool handler")
        msg_txt = "menu_all_swimpool_list_text"
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        List = []
        List.append('Back')
        sent = self.worker.bot.send_message(self.worker.chat.id,
                                            'Вы находитесь в режиме добавления бассейна. Введите адрес бассейна:')
        self.worker.wait_for_specific_message(self, List, False, 'Stop')
        return keyboard, msg_txt

    def Cancel(self, menuname):
        log.debug(f"begin Cancel handler")
        msg_txt = "menu_coach_main_txt"
        menuname = 'MenuStart'
        # переопределяем клавиатуру для выбранного пункта меню
        log.debug(f"begin Cancel handler, menuname:{menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt

    def ClientList(self, menuname):
        msg_txt = "menu_all_client_list_text"
        log.debug(f"begin admin ClientList handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:
        if self.worker.second_menu_coach is None:
            menu = TelegramSecondMenuCoach(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_coach = menu
        reply_markup = self.worker.second_menu_coach.CoachClientList(0)
        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список клиентов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def ClientSchedule(self, menuname):
        msg_txt = "menu_all_client_list_text"
        log.debug(f"begin admin ClientSchedule handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:
        if self.worker.second_menu_coach is None:
            menu = TelegramSecondMenuCoach(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_coach = menu
        reply_markup = self.worker.second_menu_coach.CoachClientList(0)
        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Расписание клиента:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt


class TelegramAdminHandler(TelegramHandler):
    def __init__(self, worker: Worker):
        super().__init__(worker)

    def SwitchAdminToCoach(self, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin SwitchAdminToCoach handler")
        # Start the bot in user mode
        self.worker.role = utils.ROLES[1]
        self.worker.menu.coach_menu("MenuStart", "menu_coach_main_txt", self.worker)
        log.debug(f"end admin SwitchAdminToCoach handler")
        return

    def SwitchAdminToUser(self, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin SwitchAdminToUser handler")
        # Start the bot in user mode
        self.worker.menu.user_menu(menuname, "menu_coach_main_txt", self.worker)
        log.debug(f"end admin SwitchAdminToUser handler")
        return

    def SwimpoolList(self, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin admin Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список бассейнов:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        reply_markup = self.worker.second_menu_admin.SwimpoolList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список бассейнов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def CoachList(self, menuname):
        msg_txt = "menu_admin_coach_list_txt"
        log.debug(f"begin admin Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список тренеров:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        reply_markup = self.worker.second_menu_admin.CoachList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список тренеров:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def AddSwimpool(self, menuname):
        msg_txt = "menu_all_swimpool_list_text"
        log.debug(f"begin Swimpoollist handler")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        sw_fileds = TelegramSecondMenuAdmin.collect_object_fields(self.worker,
                                                             [self.worker.loc.get("questions_name"),
                                                              self.worker.loc.get("questions_address"),
                                                              self.worker.loc.get("questions_swimpool_cost")],
                                                             [])
        swpool = db.SwimPool(distict_id=1, timetable_id=1, address=sw_fileds[1], name=sw_fileds[0], price=sw_fileds[2])
        self.worker.session.add(swpool)
        self.worker.session.commit()
        return keyboard, msg_txt

    def DelSwimpool(self, menuname):
        log.debug(f"begin TelegramAdminHandler.Del_Swimpool handler")
        msg_txt = "menu_all_swimpool_list_text"
        # переопределяем клавиатуру для выбранного пункта меню
        try:
            sw = self.worker.session.query(db.SwimPool).filter_by(id=self.worker.second_menu_admin.object_id,
                                                                  deleted=False).one()
            sw.deleted = True
            self.worker.session.commit()
            # удалили, теперь обновляем менюшечку с бассейнами
            message = self.worker.bot.last_message_inline_keyboard
            reply_markup = self.worker.second_menu_admin.SwimpoolList(0)
            self.worker.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=message.message_id,
                                                      reply_markup=reply_markup)
            log.debug(f"Удаляем бассейн с именем:{sw.name} и id: {sw.id}")
        except:
            # @todo убрать в локализацию
            self.worker.bot.send_message(self.worker.chat.id, "Вы не выбрали бассейн для удаления")
        menuname = self.worker.menu.get_parent_menu(menuname)

        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        log.debug(f"menuname={menuname}")
        return keyboard, msg_txt

    def DelCoach(self, menuname):
        log.debug(f"begin TelegramAdminHandler.DelCoach handler")
        msg_txt = "menu_admin_coach_list_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        try:
            sw = self.worker.session.query(db.Coach).filter_by(id=self.worker.second_menu_admin.object_id,
                                                               deleted=False).one()
            sw.deleted = True
            self.worker.session.commit()
            # удалили, теперь обновляем менюшечку с тренерами
            message = self.worker.bot.last_message_inline_keyboard
            reply_markup = self.worker.second_menu_admin.CoachList(0)
            self.worker.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=message.message_id,
                                                      reply_markup=reply_markup)
            log.debug(f"Удаляем тренера с '{sw.about}' и id: {sw.id}")
        except Exception as error:
            # @todo убрать в локализацию
            self.worker.bot.send_message(self.worker.chat.id, "Вы не выбрали тренера для удаления")
            log.debug(f"Ошибка:\n {traceback.format_exc()}")
        menuname = self.worker.menu.get_parent_menu(menuname)
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        log.debug(f"menuname={menuname}")
        return keyboard, msg_txt

    def Cancel(self, menuname):
        log.debug(f"begin Cancel handler")
        log.debug(f"begin menuname =  {menuname}")
        msg_txt = "menu_admin_main_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt

    def ClientDetails(self, menuname):
        log.debug(f"begin ClientDetails handler")
        log.debug(f"begin menuname =  {menuname}")
        msg_txt = "menu_coach_main_txt"
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        return keyboard, msg_txt

    def ClientList(self, menuname):
        msg_txt = "menu_admin_coach_list_txt"
        log.debug(f"begin admin Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список тренеров:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        reply_markup = self.worker.second_menu_admin.UserList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список клиентов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def AddCoachList(self, menuname):
        msg_txt = "menu_admin_coach_add_txt"
        log.debug(f"begin admin AddCoachList handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        log.debug(f"keyboard after set_menu_by_bpmn={keyboard}")
        # отображаем текущий список тренеров:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        reply_markup = self.worker.second_menu_admin.AddCoachList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список клиентов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def AddCoach(self, menuname):
        msg_txt = "menu_admin_coach_add_txt"
        log.debug(f"begin admin AddCoach handler")
        log.debug(f"menuname={menuname}")
        # после добавления тренера поднимаемся на два пункта меню выше, чтобы посмотреть обновленный список тренеров
        menuname = self.worker.menu.get_parent_menu(menuname)
        menuname = self.worker.menu.get_parent_menu(menuname)
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        log.debug(f"keyboard after set_menu_by_bpmn={keyboard}")
        # отображаем текущий список тренеров:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        log.debug(f"callback= {self.worker.second_menu_admin.callback_query}")
        if self.worker.second_menu_admin.callback_query:
            lst = self.worker.second_menu_admin.callback_query.split('#')
            handlername = lst[0]
            object_id = lst[1]
            if (handlername == "AddCoachList"):
                # на всякий случай, чтобы сделать добавление только один раз
                self.worker.second_menu_admin.callback_query = ""
                coach = db.Coach(user_id=object_id, timetable_id=1,
                                 about="Не забудьте добавить свое краткое описание")
                self.worker.session.add(coach)
                self.worker.session.commit()
                log.debug(f"Добавили тренера с user_id = {object_id}")
        reply_markup = self.worker.second_menu_admin.AddCoachList(0)
        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список клиентов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt

    def Inventory(self, menuname):
        msg_txt = "menu_admin_coach_list_txt"
        log.debug(f"begin admin Swimpoollist handler")
        log.debug(f"menuname={menuname}")
        # переопределяем клавиатуру для выбранного пункта меню
        self.worker.menu.set_menu_by_bpmn(menuname)
        keyboard = self.get_keyboard()
        # отображаем текущий список тренеров:
        if self.worker.second_menu_admin is None:
            menu = TelegramSecondMenuAdmin(self.worker)
            self.worker.second_menu = menu
            self.worker.second_menu_admin = menu
        reply_markup = self.worker.second_menu_admin.UserList(0)

        # @todo не забыть убрать в локализацию
        self.worker.bot.send_message(self.worker.chat.id, "<b>Список клиентов:</b>", reply_markup=reply_markup)
        return keyboard, msg_txt


'''
    Базовый класс для SecondMenu
'''


class TelegramSecondMenuBase():
    def __init__(self, worker: Worker):
        self.worker = worker
        self.object_id = 0
        self.handler_name = None
        self.callback_query = ""
        return

    def startHandler(self, worker, updates: telegram.Update):
        message = worker.bot.last_message_inline_keyboard
        callback_query = updates.callback_query.data
        self.callback_query = callback_query
        lst = callback_query.split('#')
        handlername = lst[0]
        object_id = lst[1]
        if worker.second_menu is None:
            worker.second_menu = self
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

    def CoachClientList(self, object_id: int):
        log.debug(f"begin CoachClientList second menu handler")
        msg_txt = "menu_coach_client_list_text"
        log.debug(f"begin Coach ClientList handler")
        object_id = int(object_id)
        c_id = 0
        user_id = int(self.worker.telegram_user.id)
        log.debug(f"Object_id:{user_id}")
        coach = self.worker.session.query(db.Coach).filter_by(user_id=user_id).one()
        log.debug(f"coach_id:{coach}")
        c_id = int(coach.id)
        clientlist = self.worker.session.query(db.Client).filter_by(coach_id=c_id).all()
        log.debug(f"c_id:{c_id}")

        keyboard_nice = []
        keyboard_nice.append([telegram.InlineKeyboardButton("ФИО:", callback_data="none")])
        for clients in clientlist:
            cl_id = int(clients.id)
            coach_id = int(clients.coach_id)
            user_id = int(clients.user_id)

            try:
                user = self.worker.session.query(db.User).filter_by(user_id=user_id).one()
                name = f"{user.last_name} {user.first_name}"

            except:
                name = "Ваш список клиентов пуст!"
                choice = "✔️"
                if cl_id == object_id : f"✅"
            keyboard_nice.append([telegram.InlineKeyboardButton(f"{name}", callback_data="none"),
                                  ])

        reply_markup = telegram.InlineKeyboardMarkup(keyboard_nice)
        return reply_markup

    def CoachList(self, object_id: int):
        log.debug(f"begin SwimpoolList second menu handler")
        column_names = ["ФИО", "О тренере"]
        coach_table = self.worker.session.query(db.Coach).filter_by(deleted=False).all()
        columns = []
        for coach in coach_table:
            id = coach.id
            user_id = coach.user_id
            about = coach.about
            user = self.worker.session.query(db.User).filter_by().one()
            name = f"{user.last_name} {user.first_name}" if user is not None else "Не задано"
            column = [id, name, about]
            columns.append(column)
        reply_markup = self.draw_object_list_light(object_id, column_names, columns, "CoachList")
        # reply_markup = self.draw_object_list(object_id, "Coach", column_names, ["id","about"], "CoachList")
        return reply_markup

    ''' метод формирует произвольное inline меню телеграмма для вывода таблицы с данными
        Автоматические добавляет еще одну колонку в конце для возможности выбора конкретной строки
        Параметры:
        object_id - напротив объекта с этим id будет выставлен признак выбран ✅
        column_names - название колонок таблицы в виде списка []
        columns - список строк с данными, каждая строка - тоже список [[],[],[]]. Первый элемент в каждой строке должен быть id объекта.
        Он в меню не выводится
        call_back_data - добавляем в возвращаемое значение при нажатии на меню
    '''

    @staticmethod
    def draw_object_list_light(object_id, column_names, columns, call_back_data):
        ''' метод формирует произвольное inline меню телеграмма для вывода таблицы с данными
            Автоматические добавляет еще одну колонку в конце для возможности выбора конкретной строки
            Параметры:
            object_id - напротив объекта с этим id будет выставлен признак выбран ✅
            column_names - название колонок таблицы в виде списка []
            columns - список строк с данными, каждая строка - тоже список [[],[],[]]. Первый элемент в каждой строке должен быть id объекта.
            Он в меню не выводится
            call_back_data - добавляем в возвращаемое значение при нажатии на меню
        '''
        log.debug(f"begin draw_object_list_light second menu")
        column_names_full = []
        for column_name in column_names:
            column_name = telegram.InlineKeyboardButton(column_name, callback_data="none")
            column_names_full.append(column_name)
        # добавить стандартную колонку для проставления галочки
        # @todo не забыть убрать в локализацию
        column_name = telegram.InlineKeyboardButton("Выбрать", callback_data="none")
        column_names_full.append(column_name)
        keyboard_nice = [column_names_full]
        for column in columns:
            lst = []
            choice = "✔️"
            sw_id = 0
            id = 0
            for element in column:
                if sw_id == 0:
                    element = int(element)
                    id = element
                    if element == int(object_id): choice = "✅"
                    sw_id = 1
                    continue
                lst.append(telegram.InlineKeyboardButton(element, callback_data="none"))
            lst.append(telegram.InlineKeyboardButton(choice, callback_data=f"{call_back_data}#{id}"))
            keyboard_nice.append(lst)
        reply_markup = telegram.InlineKeyboardMarkup(keyboard_nice)
        return reply_markup

    def draw_object_list(self, object_id: int, db_class_name: str, column_names, columns, call_back_data):
        log.debug(f"begin draw_object_list second menu")
        db_class_name = self.get_db_class_by_name(db_class_name)
        objects = self.worker.session.query(db_class_name).filter_by(deleted=False).all()
        object_id = int(object_id)
        keyboard_nice = [column_names]
        for object in objects:
            lst = []
            choice = "✔️"
            sw_id = ""
            for column in columns:
                property = getattr(object, column)
                log.debug(f"{column} = {property}")
                if property is None:
                    # @todo не забыть убрать в localization"
                    property = "не задана"
                if column == "id":
                    property = int(property)
                    sw_id = property
                    if property == object_id: choice = f"✅"
                else:
                    property = str(property)
                    lst.append(telegram.InlineKeyboardButton(property, callback_data="none"))
            lst.append(telegram.InlineKeyboardButton(choice, callback_data=f"{call_back_data}#{sw_id}"))
            log.debug(f"lst={lst}")
            keyboard_nice.append(lst)
        log.debug(f"keyboard_nice={keyboard_nice}")
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

    @staticmethod
    def get_db_class_by_name(class_name: str):
        clsmembers = inspect.getmembers(sys.modules[db.current_module_name], inspect.isclass)
        for cls in clsmembers:
            if str(class_name) == str(cls[0]):
                return cls[1]
        return None


class TelegramSecondMenuAdmin(TelegramSecondMenuBase):
    '''
        Дополнительное меню Админа. Решили разделить между админом, тренером и пользователем, чтобы
        не толкаться локтями и вести параллельную разработку.
    '''
    def __init__(self, worker: Worker):
        super().__init__(worker)
        return

    def CoachList(self, object_id: int):
        log.debug(f"begin SwimpoolList second menu handler")
        column_names = ["ФИО", "О тренере"]
        coach_table = self.worker.session.query(db.Coach).filter_by(deleted=False).all()
        columns = []
        for coach in coach_table:
            id = coach.id
            user_id = coach.user_id
            about = coach.about
            user = self.worker.session.query(db.User).filter_by(user_id=user_id).first()
            name = f"{user.last_name} {user.first_name}" if user is not None else "Не задано"
            column = [id, name, about]
            columns.append(column)
        reply_markup = self.draw_object_list_light(object_id, column_names, columns, "CoachList")
        # reply_markup = self.draw_object_list(object_id, "Coach", column_names, ["id","about"], "CoachList")
        return reply_markup

    def UserList(self, object_id: int):
        log.debug(f"begin UserList second menu handler")
        column_names = ["ФИО", "Тренер"]
        object_table = self.worker.session.query(db.Client).filter_by(deleted=False).all()
        columns = []
        for object in object_table:
            id = object.id
            user_id = object.user_id
            coach_id = object.coach_id
            user = self.worker.session.query(db.User).filter_by(user_id=user_id).first()
            name = f"{user.last_name} {user.first_name}" if user is not None else "Не задано"
            coach = self.worker.session.query(db.Coach).filter_by(id=coach_id).first()
            coach_user_id = coach.user_id
            coach_user = self.worker.session.query(db.User).filter_by(user_id=coach_user_id).first()
            coach_name = f"{coach_user.last_name} {coach_user.first_name}" if coach_user is not None else "Не задано"
            column = [id, name, coach_name]
            columns.append(column)
        reply_markup = self.draw_object_list_light(object_id, column_names, columns, "UserList")
        # reply_markup = self.draw_object_list(object_id, "Coach", column_names, ["id","about"], "CoachList")
        return reply_markup

    def AddCoachList(self, object_id: int):
        log.debug(f"begin UserListAddCoach second menu handler")
        column_names = ["Ник в telegram", "ФИО из телеграм"]
        object_table = self.worker.session.query(db.User).filter_by().all()
        columns = []
        for object in object_table:
            user_id = object.user_id
            name = f"{object.last_name} {object.first_name}" if object is not None else "Не задано"
            nick = object.username
            column = [user_id, nick, name]
            columns.append(column)
        reply_markup = self.draw_object_list_light(object_id, column_names, columns, "AddCoachList")
        # reply_markup = self.draw_object_list(object_id, "Coach", column_names, ["id","about"], "CoachList")
        return reply_markup


class TelegramSecondMenuCoach(TelegramSecondMenuBase):
    '''
        Дополнительное меню Админа. Решили разделить между админом, тренером и пользователем, чтобы
        не толкаться локтями и вести параллельную разработку.
    '''
    def __init__(self, worker: Worker):
        super().__init__(worker)
        return

    def CoachClientList(self, object_id: int):
        log.debug(f"begin CoachClientList second menu handler")
        column_names = ["ФИО Клиента"]
        object_id = int(object_id)
        c_id = 0
        user_id = int(self.worker.telegram_user.id)
        log.debug(f"Object_id:{user_id}")
        coach = self.worker.session.query(db.Coach).filter_by(user_id=user_id).first()
        log.debug(f"coach_id:{coach}")
        c_id = int(coach.id)
        clientlist_table = self.worker.session.query(db.Client).filter_by(coach_id=c_id).all()
        log.debug(f"c_id:{c_id}")
        columns = []

        for clients in clientlist_table:
            client_id = clients.user_id
            user = self.worker.session.query(db.User).filter_by(user_id=client_id).first()
            name = f"{user.last_name} {user.first_name}" if user is not None else "Не задано"
            column = [client_id, name]
            columns.append(column)

        reply_markup = self.draw_object_list_light(object_id, column_names, columns, "CoachClientList")
        return reply_markup

    def SwimpoolList(self, object_id: int):
        log.debug(f"begin SwimpoolList second menu handler")
        usr_id = int(self.worker.telegram_user.id)
        coach_id = self.worker.session.query(db.Coach).filter_by(user_id = usr_id).first()
        table_timetable = self.worker.session.query(db.TimeTable).filter_by(coach_id = coach_id.id)

        for row in table_timetable:
            swimpools = self.worker.session.query(db.SwimPool).filter_by(id = row.swimpool_id).all()
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


class TelegramSecondMenuUser(TelegramSecondMenuBase):
    '''
        Дополнительное меню Админа. Решили разделить между админом, тренером и пользователем, чтобы
        не толкаться локтями и вести параллельную разработку.
    '''
    def __init__(self, worker: Worker):
        super().__init__(worker)
        return


class TelegramMenu():

    def __init__(self, bpmnfile, worker, menustart):
        self.bpmnfile = bpmnfile
        self.bpmnfile = worker.cfg.tbot_home + self.bpmnfile
        # загружем BPMN схему
        # Это для ручной подгрузки workflow, без запуска обработки.
        self.runner = BPMN.BPMNXMLWorkflowRunner(bpmnfile, debug=False)
        package = self.runner.packager.package_in_memory(self.runner.workflowProcessID, self.runner.path,
                                                 self.runner.workflowEditor)
        workflowSpec = BpmnSerializer().deserialize_workflow_spec(package)
        self.runner.workflow = BpmnWorkflow(workflowSpec, **self.runner.kwargs)
        self.keyboard = []
        self.loc = worker.loc
        self.loc_menu = {}
        self.localnames = []
        self.handler_list = []
        self.keyboard_handler = []
        self.worker = worker
        self.set_menu_by_bpmn(menustart)
        return
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

    def get_parent_menu(self, step_name):
        log.debug(f"Start get_parent_menu for step = {step_name}")
        try:
            task = self.runner.workflow.get_tasks_from_spec_name(step_name)
            return task[0].parent.task_spec.name
        except:
            try:
                task = self.runner.workflow.get_task_spec_from_name(step_name)
                log.debug(f"task = {task.inputs[0].name}")
                return task.inputs[0].name
            except:
                log.debug(f"task = None")
                return None
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

    def set_menu_by_bpmn(self, step_name):
        log.debug(f"Start set_menu_by_bpmn for step_name = {step_name}")
        task_list = []
        try:
            task = self.runner.workflow.get_tasks_from_spec_name(step_name)
            task_list = task[0].children
        except:
            task = self.runner.workflow.get_task_spec_from_name(step_name)
            task_list_tmp = task.outputs
            for task in task_list_tmp:
                task = self.runner.workflow.get_task_spec_from_name(task.name)
                task.task_spec = task
                task_list.append(task)
        # log.debug(f"task[0] = {task[0].__dict__}")
        # log.debug(f"task[0].task_spec = {task[0].task_spec.__dict__}")
        # log.debug(f"task_list = {task_list}")
        # Если дошли до конца - возвращаемся на стартовую страницу
        if not task_list:
            if task[0].task_spec:
                if task[0].task_spec.outgoing_sequence_flows:
                    lsts = task[0].task_spec.outgoing_sequence_flows
                    for lst in lsts:
                        task = self.runner.workflow.get_task_spec_from_name(lst)
                        task.task_spec = task
                        log.debug(f"task name ({lst}) ={task.__dict__}")
                        task_list.append(task)
                else:
                    task = self.runner.workflow.get_tasks_from_spec_name("MenuStart")
                    task_list = task[0].children
        # log.debug(f"task_list = {task_list}")
        self.keyboard = []
        self.localnames = []
        self.loc_menu = {}
        for_menus = []
        for menuitem in task_list:
            try:
                # log.debug(f"menuitem={menuitem.__dict__}")
                menuitem_desc = menuitem.task_spec.description.split('#')
                menuitem_id = int(menuitem_desc[0])
                # удаляем всякое возможное непотребство типа перевода строк из имени обработчика
                reg = re.compile('[^a-zA-Z0-9]')
                menuitem_handler = reg.sub('', str(menuitem_desc[1]))
            except:
                log.debug(
                    f"Ошибка в формировании bpmn-схемы. Поле Description должно быть формата 1#Описание, где 1 - это порядковый номер меню.")
                return
            menuitem = menuitem.task_spec.name
            #handler, locname = self.worker.menu.loc_menu[menuitem]
            for_menus.append((menuitem_id, menuitem, menuitem_handler, self.worker.loc.get(menuitem)))
        for_menus = sorted(for_menus, key=lambda menu: menu[0])

        for menuitem_id, menuitem, handler, locname in for_menus:
            self.loc_menu[menuitem] = [handler, locname]
            self.localnames.append(locname)
            self.keyboard.append([telegram.KeyboardButton(locname)])
        # self.keyboard.reverse()
        log.debug("End set_menu_by_bpmn")
        return

    def draw_menu(self, header_txt, handlerclass, menustart):
        # возвращает класс по имени класса из текущего модуля
        get_class = lambda x: globals()[x]
        c = get_class(handlerclass)
        log.debug(f"method {c}")
        classHandler = c(self.worker)
        log.debug(f"before set_menu_by_bpmn ")
        self.set_menu_by_bpmn(menustart)
        log.debug(f"after set_menu_by_bpmn ")
        needupdatekeyboard = True
        # Loop used to returning to the menu after executing a command
        while True:
            log.debug(f"user role {self.worker.role}")
            # если предыдущее сообщение такое же, не будем дублировать
            if str(self.worker.bot.last_message.text_html).__eq__(self.worker.loc.get(header_txt)):
                needupdatekeyboard = False
                log.debug("Предыдушее сообщение равно текущему")
                log.debug(f"self.worker.bot.last_message.text_html={self.worker.bot.last_message.text_html}")
            # Send the previously created keyboard to the user (ensuring it can be clicked only 1 time)
            log.debug(f"needupdatekeyboard={needupdatekeyboard}")
            if needupdatekeyboard:
                # log.debug(f"keyboard={self.keyboard}")
                self.worker.bot.send_message(self.worker.chat.id, self.worker.loc.get(header_txt),
                                        reply_markup=telegram.ReplyKeyboardMarkup(self.keyboard, one_time_keyboard=False,
                                                                                  resize_keyboard=True))
            # Wait for a reply from the user
            log.debug(f"get localnames: {self.localnames}")
            selection = self.worker.wait_for_specific_message(self.localnames)
            # Если сделали выбор из второго меню.
            needupdatekeyboard = True
            if isinstance(selection, telegram.Update):
                if utils.IsAdmin(self.worker.role):
                    self.worker.second_menu_admin = TelegramSecondMenuAdmin(self.worker)
                    self.worker.second_menu = self.worker.second_menu_admin
                else:
                    if utils.IsCoach(self.worker.role):
                        self.worker.second_menu_coach = TelegramSecondMenuCoach(self.worker)
                        self.worker.second_menu = self.worker.second_menu_coach
                    else:
                        if utils.IsRegisterUser(self.worker.role):
                            self.worker.second_menu_user = TelegramSecondMenuUser(self.worker)
                            self.worker.second_menu = self.worker.second_menu_user
                self.worker.second_menu.startHandler(self.worker, selection)
                needupdatekeyboard = False
                continue
            handlername = self.get_handler_by_displayname(selection)
            menuname = self.get_name_by_displayname(selection)
            log.debug(f"worker menu selected name: {selection}")
            log.debug(f"worker menu selected handler: {handlername}")
            log.debug(f"worker menu selected menuname: {menuname}")

            # After the user reply, update the user data
            self.worker.update_user()

            # Вызываем обработчик в зависимости от выбранной команды.
            # try:
            log.debug(f"Drawmenu handlername: {handlername}")
            log.debug(f"Drawmenu menuname: {menuname}")
            log.debug(f"Drawmenu HandlerClass: {handlerclass}")
            keyboard, header_txt = classHandler.call_handler_by_name(handlername, menuname)
            # except AttributeError as exc:
            #    header_txt = "menu_all_inbuilding_txt"
        return

    def coach_menu(self, menustart, header_txt, worker: Worker):
        log.debug(f"Start coach_menu")
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        self.__init__("config/comunda_coach_menu.bpmn", self.worker, menustart)
        log.debug(f"header_txt: {header_txt}")
        log.debug(f" menustart: {menustart}")
        self.draw_menu(header_txt, "TelegramCoachHandler",
                       menustart)
        return

    def admin_menu(self, menustart, header_txt):
        '''Work in admin menu'''
        # переопределяем сами себя из-за возможного перехода из другого режима, например Coach -> Admin
        self.__init__("config/comunda_admin_menu.bpmn", self.worker, menustart)

        header_txt = "menu_admin_main_txt"
        self.draw_menu(header_txt, "TelegramAdminHandler",
                       menustart)
        return

    def user_menu(self, menustart, header_txt):
        log.debug(f"Start coach_menu")
        # переопределяем сами себя из-за возможного перехода из другого режима, например Admin-> Coach
        menu_file = TelegramMenu.get_menu_file(worker.cfg, "coach_menu")
        self.__init__("config/comunda_user_menu.bpmn", self.worker, menustart)
        self.draw_menu(header_txt,  "TelegramUserHandler",
                       menustart)
        return
