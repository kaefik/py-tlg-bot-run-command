О проекте

[py-tlg-bot-run-command](https://github.com/kaefik/py-tlg-bot-run-command) - Телеграмм бот для выполнения команд (запуска программ)

## Реализованные возможности:

### Администрирование учетных записей которые имеют доступ к боту
1. администратор бота только один пользователь
2. администратор может выполнять следующие действия: добавить пользователя по id, удалить пользователя из доступа к данному боту, информация о тех пользователях кто имеет доступ


### Основная функциональность

1. **start_bot_async.py** - выполнение команды на сервере и вывод в телеграмм процесса выполнения команды (команда ls или dir с параметром пути)
2. **start_bot_for_chats.py** -  прослушивает указанный чат/чаты и по стоп-словам делает пользователю замечание на его сообщения

## Настройка проекта для запуска

### Библиотеки:

* ```bash
  pip3 install python-dotenv	
  pip3 install Telethon
  pip3 install requests
  ```

  или просто выполняем 

  ```bash
  pip install -r requirements.txt
  ```
### Конфигурационные файлы проекта:

* **.env** 

  ```
  TLG_APP_API_ID=123456 # APP API ID get from https://my.telegram.org
  TLG_APP_API_HASH=fdgdfgdgdfgdfgd # APP API HASH get from https://my.telegram.org
  TLG_APP_NAME=app  # APP NAME get from https://my.telegram.org
  I_BOT_TOKEN=12345:fdgdfgdfgdfdfgdfg    # TOKEN Bot drom BotFather
  TLG_ADMIN_ID_CLIENT=12568999  # id administarator bot
  TLG_PROXY_SERVER = server # адрес MTProxy Telegram
  TLG_PROXY_PORT = 555 # порт  MTProxy Telegram
  TLG_PROXY_KEY=sf23231231  # secret key  MTProxy Telegram
  ```

### Запуск проекта:

```bash
python start_bot_async.py
```


### Добавление в автозапуск программы при загрузке сервера Ubuntu

в папке /etc/systemd/system/ создадим файл start-telegrambot.service

Содержимое файла:
```bash
[Unit]
Description=Telegram bot for run commands
After=network.target

[Service]
ExecStart=путь до скрипта запуска программы

[Install]
WantedBy=default.target
```

выполним команды
```bash
systemctl daemon-reload
systemctl enable start-telegrambot.service
systemctl start start-telegrambot.service
```

## Запуск docker контейнера с программой

1. скопировать всю программу в папку на компьютере например в папку *tlg-bot/app*:

2. сохранить файл *Dockerfile* в папке *tlg-bot*:
   ```
   ENV TZ=Europe/Moscow
   RUN apt-get update && apt-get install -y python3 && apt-get install -y python3-pip 
   RUN pip3 install python-dotenv && pip3 install Telethon && pip3 install requests
   WORKDIR /home/app
   #VOLUME /home/app
   COPY app /home/app
   CMD ["python3", "start_bot_async.py"]
   ```

3. в папку *tlg-bot/cfg* файлы конфигурации проекта:
   1. *.env*

4. Создание образа контейнера

`docker build --tag=tlgbot .`

5. Запуск docker контейнера (после завершения работы контейнера)

 `docker run -it --rm  -v "/полный_путь_до_проекта/tlg-bot/cfg/.env:/home/app/.env" tlgbot`

### Полезные ссылки

* https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot
* https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets
* [https://api.telegram.org/botТОКЕН/sendMessage?chat_id=ЧАТ_ID&text=HelloBot](https://api.telegram.org/botТОКЕН/sendMessage?chat_id=ЧАТ_ID&text=HelloBot) 