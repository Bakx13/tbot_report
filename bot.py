import logging
import os
import threading
import sqlalchemy
import sqlalchemy.ext.declarative as sed
import sqlalchemy.orm
from datetime import datetime

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

# подгружаем свои библиотеки
import tbot_report.lib.picture
import tbot_report.lib.loadarguments as loadarguments
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
import tbot_report.lib.tbotlogic as tbotlogic
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
    ENV_LEVEL = loadarguments.ArgParses.createParser().env
    config_all = MConfig.MyConfig()
    config_all.Load(CONFIG_COMMON, ENV_LEVEL)

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
    # TODO Не забыть выключить отладку для БД. Либо обернуть в логику уровня логирования.
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
        city = database.City(name="Москва", description="Столица России")
        session.add(city)

        district = database.District(city_id=city.id, name="Строгино", description="Спальный район на западе Москвы")
        session.add(district)
        timetable = database.TimeTable(creation_date=datetime.now())
        session.add(timetable)
        spool = database.SwimPool(distict_id=district.id, timetable_id=timetable.id, address="Живописная 11",
                                  name="Энигма", price="500 руб")
        spool2 = database.SwimPool(distict_id=district.id, timetable_id=timetable.id, address="Где-то на западе",
                                   name="Западный бассейн", price="300 руб")
        session.add(spool)
        session.add(spool2)
        session.commit()

    bot = tbotlogic.TBot.initbot(config_all)

    tbotlogic.TBot.run(config_all, default_loc, bot, engine)


if __name__ == '__main__':
    main()
