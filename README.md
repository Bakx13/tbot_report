# tbot_report
Подготовка окружения:<br>
Создать бота - @BotFather. Если не понятно что там тыкать - читаем любой мануал.<br>
На выходе получаем ключик.<br>
Далее этот ключи надо внести в config/config_devel.toml. 
Конфиг используется в режиме разработки.<br>
Софт для разработки:<br>
PyCharm (Commynity последней версии) - фрэймворк для питона<br>
DBevear - для работы с СУБД<br>
Docker desktop - но можно и без него, для этого нужно поменять deploy/build.sh или вообще отлаживаться в Pycharm. <br>
Camunda Modeler - https://camunda.com/download/modeler/ <br>
В докере развернул:<br>
debian - взял с официального сайта<br>
  внутри дополнительно:<br>
    python3 --version<br>
    Python 3.7.3<br>
    +  нужные для работы библиотеки питона<br>
    <br>
Запуск: <br>
python3 ./bot.py -e dev<br>
-e - режим работы. <br>
Всего их три:<br>
  dev - разработка, БД - sqlite, локальная<br>
  test - тестирование, БД - postgre.  Используется база у Попова.<br>
  prom - промышленная эксплуатация. Ни разу не запускалась.<br>

    


Полезные проекты с гита.<br>
Про BPMN:<br>
https://github.com/labsolutionlu/bpmn_dmn/blob/7c2a632dab542ab81da56961193fc2235310934c/bpmn_dmn/bpmn/camunda.py <br>
https://spiffworkflow.readthedocs.io/en/latest/SpiffWorkflow.task.html <br>
Про API telegram:<br>
https://python-telegram-bot.readthedocs.io/en/stable/telegram.botcommand.html <br>
https://tlgrm.ru/docs/bots/api <br>
https://core.telegram.org/api <br>
https://github.com/tdlib/telegram-bot-api <br>
https://core.telegram.org/bots <br>
 
