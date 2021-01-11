from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import requests
import re
import random
import psycopg2
import datetime
import logging
import os
import sys
import threading
import sqlalchemy
import sqlalchemy.ext.declarative as sed
import sqlalchemy.orm

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

# подгружаем свои библиотеки
import tbot_report.lib.picture
import tbot_report.lib.loadarguments as loadarguments
import tbot_report.lib.loadconfig as MConfig
import tbot_report.lib.duckbot as duckbot
import tbot_report.localization.localization as localization
import tbot_report.lib.tbotlogic as tbotlogic
import tbot_report.database.database as database


def main():
    #init variables
    CONFIG_COMMON = "config/config_common.toml"
    threading.current_thread().name = "Core"

    log = logging.getLogger(threading.current_thread().name)
    #logging.root.setLevel("DEBUG")
    logging.basicConfig(filename='logs/'+threading.current_thread().name+'.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    """The core code of the program. Should be run only in the main process!"""
    # Rename the main thread for presentation purposes
    #Загружаем общий конфиг
    if not os.path.isfile(CONFIG_COMMON):
        log.fatal(CONFIG_COMMON + " does not exist!")
        exit(254)
    #разбираем параметр запуска bot.py env -среда исполнения. От этого зависит какой второй конфиг мы подтянем.
    ENV_LEVEL = loadarguments.ArgParses.createParser().env
    config_all = MConfig.MyConfig()
    config_all.Load(CONFIG_COMMON, ENV_LEVEL)

    # Обновляем настройки логирования после загрузку конфигов

    logging.root.setLevel(config_all.log_level)
    stream_handler = logging.FileHandler(filename=config_all.log_dir+threading.current_thread().name+'.log')
    if coloredlogs is not None:
        stream_handler.formatter = coloredlogs.ColoredFormatter(config_all.log_format, style="{")
    else:
        stream_handler.formatter = logging.Formatter(config_all.log_format, style="{")

    logging.root.handlers.clear()
    logging.root.addHandler(stream_handler)
    log.debug("Logging setup successfully!")
    # Ignore most python-telegram-bot logs, as they are useless most of the time
    logging.getLogger("telegram").setLevel("ERROR")

    #подтягиваем локализацию
    default_language = config_all.language["default_language"]
    default_loc = localization.Localization(language= default_language, fallback= default_language)

    # подключаем СУБД
    log.debug("Creating the sqlalchemy engine...")
    engine = sqlalchemy.create_engine(config_all.database["engine"])
    log.debug("Binding metadata to the engine...")
    database.TableDeclarativeBase.metadata.bind = engine
    log.debug("Creating all missing tables...")
    database.TableDeclarativeBase.metadata.create_all()
    log.debug("Preparing the tables through deferred reflection...")
    sed.DeferredReflection.prepare(engine)

    #инициализируем бота
    bot = duckbot.factory(config_all)
    log.debug("Testing bot token...")
    me = bot.get_me()
    if me is None:
        logging.fatal("The token you have entered in the config file is invalid. Fix it, then restart greed.")
        sys.exit(1)
    log.debug("Bot token is valid!")


    # Notify on the console that the bot is starting
    log.info(f"@{me.username} is starting!")
    tbotlogic.TBot.run(config_all, default_loc, bot, engine)
    exit(254)

if __name__ == '__main__':
    main()
