import logging
import random
log = logging.getLogger(__name__)

class Picture(object):
    """Класс для работы с картинками"""

    def __init__(self):
        """Constructor"""
        pass
    def get_pict(update, context):
        """Ищем картинку в сервисе https://source.unsplash.com/"""
        #print ('random pict')
        log.info("random pict")
        text = update.message.text.split(' ',1)[1]
        #print ('split')
        url = 'https://source.unsplash.com/800x600/?{0}/{1}'.format(text, str(random.randint(1,100000)))
        log.info(url)
        #print(url)
        chat_id = update.message.chat_id
        log.info("sending image")
        context.bot.send_photo(chat_id=chat_id, photo=url)
        #bot.send_text(chat_id=chat_id, text = "text1")
        print("sending image end")