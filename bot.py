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
import tbot_report.lib.nuconfig

def get_connection():
    connected = psycopg2.connect(dbname='ditrb', user='ditrb', password='#d1trb',
                                      host='ovz1.harry-popoff.n461m.vps.myjino.ru', port='5432')
    return connected


def who(update, context):
    print('all_issue start')

    try:
        connection = get_connection()       
        cursor = connection.cursor()
        now_date = datetime.date.today()
        cursor.execute('SELECT FIO,PHONE,CITY FROM office_date where date_office = %(date_office)s', 
                       {"date_office":now_date})
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            context.bot.send_message(update.message.chat_id, row[0] + ", " + row[1] +  ", " + row[2])
    except (Exception, psycopg2.Error) as error:
        print("Failed to select record from table", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()


def all_issue_by_date(update, context):
    print('all_close start')
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_name, author, description, mobile_number, create_time, status FROM issue where status='CLOSE'")
        for row in cursor:
            context.bot.send_message(update.message.chat_id, str(row[0]) + ", " + row[1])
    except (Exception, psycopg2.Error) as error:
        print("Failed to select record from table", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()


def in_office(update, context):
    print('office start')
    try:
        # author = update.message.text.split('auth:')[1]
        # description = update.message.text.split('desc:')[1]
        # mobile_number = update.message.text.split('mob:')[1]
       
        msg = update.message.text.split(" ", 1)[1]
        print(msg)
        author = msg.split('#')[0]
        print(author)
        mobile_number = msg.split('#')[1]
        print(mobile_number)
        city = msg.split('#')[2]
        print(city)
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO office_date (FIO,PHONE,CITY) VALUES (%s,%s,%s)"
        record_to_insert = [author, mobile_number, city]
        cursor.execute(insert_query, record_to_insert)
        #issue_id = cursor.fetchone()[0]
        connection.commit()
        context.bot.send_message(update.message.chat_id, 'Зарегистрирован сотрудник  ' + author)
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Connection is closed")
            
def textMessage(update, context):
    print ('all start')
    url = 'https://source.unsplash.com/800x600/?{0}/{1}'.format(update.message.text,str(random.randint(1,100000)))
    print(url)
    chat_id = update.message.chat_id
    print("sending image")
    context.bot.send_photo(chat_id=chat_id, photo=url)
    #bot.send_text(chat_id=chat_id, text = "text1")
    print("sending image end")


            
        
def main():
    #init variables
    CONFIG_COMMON = "config/config_common.toml"

    log = logging.getLogger("core")
    #logging.root.setLevel("DEBUG")
    logging.basicConfig(filename='logs/'+threading.current_thread().name+'.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    """The core code of the program. Should be run only in the main process!"""
    # Rename the main thread for presentation purposes
    threading.current_thread().name = "Core"

    #Загружаем общий конфиг
    if not os.path.isfile(CONFIG_COMMON):
        log.fatal(CONFIG_COMMON + " does not exist!")
        exit(254)

    user_cfg = nuconfig.NuConfig(user_cfg_file)
    #выбираем среду запуска программы: dev, test, prod
    ENV_LEVEL = ArgParses.createParser().env
    unit_to_multiplier = {
        'dev': "config/config_devel.toml",
        'test': "config/config_test.toml",
        'prod': "config/config_prod.toml",
    }
    #Загружаем конфиг среды запуска
    CONFIG_FILE = unit_to_multiplier[ENV_LEVEL]
    log.debug("conf_file:"+CONFIG_FILE)
    # Start logging setup
    log.debug("Set logging level to INFO while the config is being loaded")

    log.debug('This is a debug message')
    log.info('This is an info message')
    log.warning('This is a warning message')
    log.error('This is an error message')
    log.critical('This is a critical message')

    TOKEN='966917460:AAEssBFBIRI7eQuTl2Vqc595bep7AOFJKLU'
    REQUEST_KWARGS={
    'proxy_url': 'socks4://24.181.205.134:54321', 
    # Optional, if you need authentication:
    #'username': 'PROXY_USER',
    #'password': 'PROXY_PASS',
    #'secret' : '7hfpeVBbrqORfvAofrlDY/l3d3cuYW1hem9uLmNvbQ',

    }
    #updater = Updater(TOKEN)


    # end init variables
    print("1111");
    log.info("1111")
    updater = Updater(token = TOKEN, use_context=True, request_kwargs = REQUEST_KWARGS)
    print("2")
    dp = updater.dispatcher
    print("3")
    
    text_message_handler = MessageHandler(Filters.text, textMessage)
    
    
    dp.add_handler(CommandHandler('pict',Picture.get_pict))
    dp.add_handler(CommandHandler('office',in_office))
    dp.add_handler(CommandHandler('who',who))
    dp.add_handler(text_message_handler)
    print("4")
    updater.start_polling()
    print("5")
    updater.idle()
    print("6")
if __name__ == '__main__':
    main()
