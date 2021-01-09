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