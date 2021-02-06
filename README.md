# tbot_report

Софт для разработки:<br>
PyCharm (Commynity последней версии) - фрэймворк для питона<br>
DBevear - для работы с СУБД<br>
Docker desktop - но можно и без него, для этого нужно поменять deply/build.sh или вообще отлаживаться в Pycharm. <br>
Camunda Modeler - https://camunda.com/download/modeler/ <br>
В докере развернул:
debian - взял с официального сайта
  внутри дополнительно:
    python3 --version
    Python 3.7.3
    +  нужные для работы библиотеки питона
    
Запуск: 
python3 ./bot.py -e dev
-e - режим работы. 
Всего их три:
  dev - разработка, БД - sqlite, локальная
  test - тестирование, БД - postgre.  Используется база у Попова.
  prom - промышленная эксплуатация. Ни разу не запускалась.

    


Полезные проекты с гита.
Про BPMN:
https://github.com/labsolutionlu/bpmn_dmn/blob/7c2a632dab542ab81da56961193fc2235310934c/bpmn_dmn/bpmn/camunda.py
https://spiffworkflow.readthedocs.io/en/latest/SpiffWorkflow.task.html
Про API telegram:
https://python-telegram-bot.readthedocs.io/en/stable/telegram.botcommand.html
https://tlgrm.ru/docs/bots/api
https://core.telegram.org/api
https://github.com/tdlib/telegram-bot-api
https://core.telegram.org/bots
