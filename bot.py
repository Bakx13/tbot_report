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
try:
    import coloredlogs
except ImportError:
    coloredlogs = None


from tbot_report.lib.picture import Picture
from tbot_report.lib.loadarguments import ArgParses
from tbot_report.lib.nuconfig import NuConfig
from tbot_report.lib.loadconfig import MyConfig


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
    ENV_LEVEL = ArgParses.createParser().env
    config_all = MyConfig()
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

    TOKEN=config_all.telegram_token
    REQUEST_KWARGS={
    config_all.telegram_proxy_string,
    # Optional, if you need authentication:
    #'username': 'PROXY_USER',
    #'password': 'PROXY_PASS',
    #'secret' : '7hfpeVBbrqORfvAofrlDY/l3d3cuYW1hem9uLmNvbQ',

    }
    #updater = Updater(TOKEN)


    # end init variables
    print("1111");
    exit(254)
    log.info("1111")
    updater = Updater(token = TOKEN, use_context=True, request_kwargs = REQUEST_KWARGS)
    print("2")
    dp = updater.dispatcher
    print("3")
    
    #text_message_handler = MessageHandler(Filters.text, textMessage)
    
    
    dp.add_handler(CommandHandler('pict',Picture.get_pict))
    #dp.add_handler(CommandHandler('office',in_office))
    #dp.add_handler(CommandHandler('who',who))
    #dp.add_handler(text_message_handler)
    print("4")
    updater.start_polling()
    print("5")
    updater.idle()
    print("6")
if __name__ == '__main__':
    main()
