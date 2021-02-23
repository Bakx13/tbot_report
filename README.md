# tbot_report
Подготовка окружения:<br>
Создать бота - @BotFather. Если не понятно что там тыкать - читаем любой мануал.<br>
На выходе получаем ключик.<br>
Далее этот ключи надо внести в config/config_devel.toml. 
Конфиг используется в режиме разработки.<br>
Задачи по проекту: https://konstantinshin.atlassian.net/jira/software/projects/SVDEV/boards/1 <br>
Дока по проекту: https://konstantinshin.atlassian.net/wiki/spaces/SWIMDEV/pages/262309 <br>
Софт для разработки:<br>
PyCharm (Commynity последней версии) - фрэймворк для питона<br>
DBevear - для работы с СУБД<br>
Docker desktop - но можно и без него, для этого нужно поменять deploy/build.sh или вообще отлаживаться в Pycharm. <br>
Camunda Modeler - https://camunda.com/download/modeler/ <br>

Необходимые библиотеки: 
import sqlalchemy, необходимо отдельно поставить.

В докере развернул:<br>
Установить необходимые пакеты для проекта: 
sqlalcheme
impl
telegramm
tbot_report.lib
requests

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


 pip3 install sqlalchemy


s/tbot_report/deploy/build_anton.sh10$ /bin/bash /Users/a16673010/PycharmProject 
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 9, in <module>
    from tbot_report.lib.nuconfig import NuConfig
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/nuconfig.py", line 3, in <module>
    import toml
ModuleNotFoundError: No module named 'toml'
CAB-WSM-0002866:tbot_report a16673010$ 
CAB-WSM-0002866:tbot_report a16673010$ pip3 install toml
Collecting toml
  Using cached toml-0.10.2-py2.py3-none-any.whl (16 kB)
Installing collected packages: toml
Successfully installed toml-0.10.2
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 20, in <module>
    from tbot_report.lib.tbotlogic import TBot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/tbotlogic.py", line 3, in <module>
    import telegram
ModuleNotFoundError: No module named 'telegram'
CAB-WSM-0002866:tbot_report a16673010$ pip3 install telegram
Collecting telegram
  Using cached telegram-0.0.1.tar.gz (879 bytes)
Building wheels for collected packages: telegram
  Building wheel for telegram (setup.py) ... done
  Created wheel for telegram: filename=telegram-0.0.1-py3-none-any.whl size=1306 sha256=fd0a148e01690f0d9ba719cdf4676fb2bb3b57a5e624d48c28f561f600aaeb79
  Stored in directory: /Users/a16673010/Library/Caches/pip/wheels/11/7a/5d/62391dcb6b9a45247192c3a711bf03ed513c14218a8b275a63
Successfully built telegram
Installing collected packages: telegram
Successfully installed telegram-0.0.1
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 20, in <module>
    from tbot_report.lib.tbotlogic import TBot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/tbotlogic.py", line 9, in <module>
    import tbot_report.lib.duckbot as duckbot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/duckbot.py", line 7, in <module>
    import telegram.error
ModuleNotFoundError: No module named 'telegram.error'
CAB-WSM-0002866:tbot_report a16673010$ pip3 install telegram.error
ERROR: Could not find a version that satisfies the requirement telegram.error
ERROR: No matching distribution found for telegram.error
CAB-WSM-0002866:tbot_report a16673010$ pip3 install telegram.ext
ERROR: Could not find a version that satisfies the requirement telegram.ext
ERROR: No matching distribution found for telegram.ext
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 20, in <module>
    from tbot_report.lib.tbotlogic import TBot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/tbotlogic.py", line 9, in <module>
    import tbot_report.lib.duckbot as duckbot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/duckbot.py", line 7, in <module>
    import telegram.error
ModuleNotFoundError: No module named 'telegram.error'
CAB-WSM-0002866:tbot_report a16673010$ DD
CAB-WSM-0002866:tbot_report a16673010$ pip3 install python-telegram-bot
Collecting python-telegram-bot
  Downloading python_telegram_bot-13.3-py3-none-any.whl (436 kB)
     |████████████████████████████████| 436 kB 812 kB/s 
Collecting APScheduler==3.6.3
  Using cached APScheduler-3.6.3-py2.py3-none-any.whl (58 kB)
Collecting tornado>=5.1
  Using cached tornado-6.1-cp39-cp39-macosx_10_9_x86_64.whl (416 kB)
Collecting certifi
  Using cached certifi-2020.12.5-py2.py3-none-any.whl (147 kB)
Collecting pytz>=2018.6
  Using cached pytz-2021.1-py2.py3-none-any.whl (510 kB)
Requirement already satisfied: setuptools>=0.7 in /usr/local/lib/python3.9/site-packages (from APScheduler==3.6.3->python-telegram-bot) (52.0.0)
Collecting tzlocal>=1.2
  Using cached tzlocal-2.1-py2.py3-none-any.whl (16 kB)
Requirement already satisfied: six>=1.4.0 in /usr/local/lib/python3.9/site-packages (from APScheduler==3.6.3->python-telegram-bot) (1.15.0)
Installing collected packages: pytz, tzlocal, tornado, certifi, APScheduler, python-telegram-bot
Successfully installed APScheduler-3.6.3 certifi-2020.12.5 python-telegram-bot-13.3 pytz-2021.1 tornado-6.1 tzlocal-2.1
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 20, in <module>
    from tbot_report.lib.tbotlogic import TBot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/tbotlogic.py", line 10, in <module>
    import tbot_report.lib.worker as worker
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/worker.py", line 13, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
CAB-WSM-0002866:tbot_report a16673010$ pip3 install requests
Collecting requests
  Using cached requests-2.25.1-py2.py3-none-any.whl (61 kB)
Collecting chardet<5,>=3.0.2
  Using cached chardet-4.0.0-py2.py3-none-any.whl (178 kB)
Collecting idna<3,>=2.5
  Using cached idna-2.10-py2.py3-none-any.whl (58 kB)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.9/site-packages (from requests) (2020.12.5)
Collecting urllib3<1.27,>=1.21.1
  Using cached urllib3-1.26.3-py2.py3-none-any.whl (137 kB)
Installing collected packages: urllib3, idna, chardet, requests
Successfully installed chardet-4.0.0 idna-2.10 requests-2.25.1 urllib3-1.26.3
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory
Traceback (most recent call last):
  File "/Users/a16673010/PycharmProjects/tbot_report/bot.py", line 20, in <module>
    from tbot_report.lib.tbotlogic import TBot
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/tbotlogic.py", line 10, in <module>
    import tbot_report.lib.worker as worker
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/worker.py", line 22, in <module>
    from tbot_report.lib.TelegramMenu import TelegramMenu, TelegramCoachHandler, TelegramAdminHandler
  File "/Users/a16673010/PycharmProjects/tbot_report/tbot_report/lib/TelegramMenu.py", line 3, in <module>
    import bpmn_dmn.bpmn as BPMN
ModuleNotFoundError: No module named 'bpmn_dmn'
CAB-WSM-0002866:tbot_report a16673010$ pip3 install bpmn_dmn
Collecting bpmn_dmn
  Using cached bpmn_dmn-0.1.7-py3-none-any.whl
Collecting SpiffWorkflow
  Using cached SpiffWorkflow-0.5.22-py2.py3-none-any.whl (133 kB)
Collecting future
  Using cached future-0.18.2.tar.gz (829 kB)
Collecting lxml
  Using cached lxml-4.6.2-cp39-cp39-macosx_10_9_x86_64.whl (4.6 MB)
Collecting configparser
  Using cached configparser-5.0.1-py3-none-any.whl (22 kB)
Building wheels for collected packages: future
  Building wheel for future (setup.py) ... done
  Created wheel for future: filename=future-0.18.2-py3-none-any.whl size=491059 sha256=b6b772d01d45fbeb8eb125bf8df81baf25cf8d77a0af5490b54bbb98bcc20241
  Stored in directory: /Users/a16673010/Library/Caches/pip/wheels/2f/a0/d3/4030d9f80e6b3be787f19fc911b8e7aa462986a40ab1e4bb94
Successfully built future
Installing collected packages: lxml, future, configparser, SpiffWorkflow, bpmn-dmn
Successfully installed SpiffWorkflow-0.5.22 bpmn-dmn-0.1.7 configparser-5.0.1 future-0.18.2 lxml-4.6.2
CAB-WSM-0002866:tbot_report a16673010$ /bin/bash /Users/a16673010/PycharmProjects/tbot_report/deploy/build_anton.sh
rm: database.sqlite: No such file or directory

 
