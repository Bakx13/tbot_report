import logging
import os
import threading
import sqlalchemy
import sqlalchemy.ext.declarative as sed
import sqlalchemy.orm
from datetime import datetime

from tbot_report.lib.nuconfig import NuConfig

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

# подгружаем свои библиотеки
import tbot_report.lib.loadarguments as loadarguments
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
from tbot_report.lib.tbotlogic import TBot
import tbot_report.database.database as database


def main():
    """The core code of the program. Should be run only in the main process!"""
    # init variables
    CONFIG_COMMON = "config/config_common.toml"
    threading.current_thread().name = "Core"
    log = logging.getLogger(threading.current_thread().name)
    logging.basicConfig(filename='logs/' + threading.current_thread().name + '.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    # Загружаем общий конфиг
    if not os.path.isfile(CONFIG_COMMON):
        log.fatal(CONFIG_COMMON + " does not exist!")
        exit(254)
    # разбираем параметр запуска bot.py env -среда исполнения. От этого зависит какой второй конфиг мы подтянем.
    arguments = loadarguments.ArgParses.createParser()
    ENV_LEVEL = arguments.env
    dev_name = arguments.programmist
    config_all = MConfig.MyConfig()
    config_all.Load(CONFIG_COMMON, ENV_LEVEL, dev_name)

    # Обновляем настройки логирования после загрузку конфигов

    logging.root.setLevel(config_all.log_level)
    stream_handler = logging.FileHandler(filename=config_all.log_dir + threading.current_thread().name + '.log')
    if coloredlogs is not None:
        stream_handler.formatter = coloredlogs.ColoredFormatter(config_all.log_format, style="{")
    else:
        stream_handler.formatter = logging.Formatter(config_all.log_format, style="{")

    logging.root.handlers.clear()
    logging.root.addHandler(stream_handler)
    log.debug("Logging setup successfully!")
    # Ignore most python-telegram-bot logs, as they are useless most of the time
    logging.getLogger("telegram").setLevel("ERROR")

    # подтягиваем локализацию
    default_language = config_all.language["default_language"]
    default_loc = localization.Localization(language=default_language, fallback=default_language)
    # подключаем СУБД
    log.debug("Creating the sqlalchemy engine...")
    engine = sqlalchemy.create_engine(config_all.database["engine"], echo=False)
    log.debug("Binding metadata to the engine...")
    database.TableDeclarativeBase.metadata.bind = engine
    log.debug("Creating all missing tables...")
    database.TableDeclarativeBase.metadata.create_all()
    log.debug("Preparing the tables through deferred reflection...")
    sed.DeferredReflection.prepare(engine)
    '''
    добавляем тестовые данные
    '''
    if ENV_LEVEL == 'dev':
        '''Удаляем все данные из таблиц'''
        meta = database.TableDeclarativeBase.metadata
        con = engine.connect()
        trans = con.begin()
        for table in meta.sorted_tables:
            # con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
            con.execute(table.delete())
            # con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
        trans.commit()
        '''Создаем тестовые данные
        @todo Переделать, чтобы брать данные из файликов для каждой таблицы'''
        session = sqlalchemy.orm.sessionmaker(bind=engine)()

        # загружаем файлик с тестовыми данными
        file_test_data = config_all.test_data
        f_test_data = open(file_test_data, encoding="utf8")
        test_data = NuConfig(f_test_data)
        cities = test_data['City']
        for city_id in cities:
            city = cities[city_id]
            log.debug(f"Загружаем тестовый город: {city['name']}")
            city = database.City(id=city_id, name=city['name'], description=city['description'])
            session.add(city)
        districts = test_data['District']
        for district_id in districts:
            district = districts[district_id]
            log.debug(f"Загружаем тестовый район: {district['name']}")
            district = database.District(id=district_id, city_id=district['city_id'], name=district['name'],
                                         description=district['description'])
            session.add(district)

        #timetable = database.TimeTable(creation_date=datetime.now())
        #session.add(timetable)
        timetables = test_data['TimeTable']

        for timetable_id in timetables:
            timetable = timetables[timetable_id]
            ttable = database.TimeTable(id=timetable_id, creation_date=timetable['creation_date'],coach_id = timetable['coach_id'],
                                        swimpool_id = timetable['swimpool_id'])
            session.add(ttable)

        timetableitems = test_data['TimeTableItem']

        for timetableitem_id in timetableitems:
            timetableitem = timetableitems[timetableitem_id]
            ttableitem = database.TimeTableItem(id=timetableitem_id, item=timetableitem['item'], day_of_week = timetableitem['day_of_week'],
                                                prop = timetableitem['prop'],start_time = timetableitem['start_time'],
                                                end_time=timetableitem['end_time'], timetable_id=timetableitem['timetable_id'])
            session.add(ttableitem)

        swimpools = test_data['SwimPool']
        for swimpool_id in swimpools:
            swimpool = swimpools[swimpool_id]
            log.debug(f"Загружаем тестовый бассейн: {swimpool['name']}")
            spool = database.SwimPool(id=swimpool_id, distict_id=swimpool['distict_id'],
                                      timetable_id=swimpool['timetable_id'],
                                      address=swimpool['address'], name=swimpool['name'], price=swimpool['price'])
            session.add(spool)

        coachs = test_data['Coach']
        for coach_id in coachs:
            coach = coachs[coach_id]
            log.debug(f"Загружаем тестовых тренеров: {coach['about']}")
            cch = database.Coach(user_id=coach['user_id'], timetable_id=coach['timetable_id'], id=coach_id,
                                 about=coach['about'])

            session.add(cch)

        clients = test_data['Client']
        for client_id in clients:
            client = clients[client_id]
            log.debug(f"Загружаем тестовых клиентов: {client['user_id']}")
            cl = database.Client(id=client_id, user_id=client['user_id'], timetable_id=client['timetable_id'],
                                 coach_id=client['coach_id'])

            session.add(cl)

      #  users = test_data['User']
       # for user_id in users:
        #    user = users[user_id]
         #   log.debug(f"Загружаем тестовых пользователей: {user['first_name']}")
          #  usr = database.User(user_id=user_id, first_name=user['first_name'], last_name=user['last_name'],
          #                      username=user['username'], language=user['language'], w = user['w'])

        #    session.add(usr)

        session.commit()

    bot = TBot.initbot(config_all)

    TBot.run(config_all, default_loc, bot, engine)


if __name__ == '__main__':
    main()
