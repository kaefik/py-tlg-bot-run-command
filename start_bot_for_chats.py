"""
 Версия телеграмм бота с использованием библиотеки Telethon

 которая прослушивает указанный чат/чаты и по стоп-словам делает пользователю замечание на его сообщения
"""
import os
# pip3 install python-dotenv
from dotenv import load_dotenv
# pip3 install Telethon
from telethon import TelegramClient, events, connection, Button
import asyncio
import logging
# import re

from i_utils import run_cmd
from sqlitelib.sqliteutils import User, SettingUser, Role, SettingOne, SettingTwo

# ---- Начальные данные ----

# подготовка для логирования работы программы
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR)
# END подготовка для логирования работы программы

# загрузка данных для того чтобы телеграмм бот залогинился в Телеграмм
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# print((dotenv_path))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
app_api_id = os.getenv("TLG_APP_API_ID")
app_api_hash = os.getenv("TLG_APP_API_HASH")
app_name = os.getenv("TLG_APP_NAME")
bot_token = os.getenv("I_BOT_TOKEN")
proxy_server = os.getenv("TLG_PROXY_SERVER")
proxy_port = os.getenv("TLG_PROXY_PORT")
proxy_key = os.getenv("TLG_PROXY_KEY")
# клиент с правами администратора
admin_client = int(os.getenv("TLG_ADMIN_ID_CLIENT"))
# END загрузка данных для того чтобы телеграмм бот залогинился в Телеграмм

# настройки пользователей бота в том числе и администратора admin_client
name_file_settings = 'settings.db'
if not os.path.exists(name_file_settings):
    print('нет файла настроек')
    name_admin = ''
    settings = SettingUser(namedb=name_file_settings)
    admin_User = User(id=admin_client, role=Role.admin, active=True)
    settings.add_user(admin_User)
else:
    print('есть файл настроек')
    settings = SettingUser(namedb=name_file_settings)

# получение всех пользователей из БД
# clients = settings.get_all_user()  # список всех клиентов
admin_client = settings.get_user_type(Role.admin)  # список администраторов бота
# END настройки бота


if proxy_server is None or proxy_port is None or proxy_key is None:
    print("Нет настроек MTProto прокси сервера телеграмма.\n" \
          "Попытка подключения клиента без прокси.")
    bot = TelegramClient(app_name, app_api_id, app_api_hash).start(
        bot_token=bot_token
    )
else:
    proxy = (proxy_server, int(proxy_port), proxy_key)
    bot = TelegramClient(app_name, app_api_id, app_api_hash,
                         connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                         proxy=proxy).start(bot_token=bot_token)

# кнопки главного режима для администратора
button_main_admin = [
    [Button.text("/help"),
     Button.text("/admin"),
     Button.text("/settings")]
]

# кнопки главного режима для обычного пользователя
button_main_user = [
    [Button.text("/help"),
     Button.text("/admin")]
]

# кнопки для режима администратора
button_admin = [
    [Button.text("/AddUser"),
     Button.text("/DelUser"),
     Button.text("/InfoUser"),
     Button.text("/ExitAdmin")]
]

# кнопки для режима настроек пользователя
button_settings = [
    [Button.text("/SettingOne"),
     Button.text("/ExitSettings")]
]

# выбор типа результирующего файла
button_settingone = [
    [
        Button.text("/SubSettingOne"),
        Button.text("/ExitTypeResult"),
    ]
]


# ---- END Начальные данные ----

# ----- Вспомогательные функции

def get_help(filename='help.txt'):
    """
        получаем текст для помощи о командах бота
    """
    help_text = ""
    with open(filename, "r") as f:
        help_text = f.read()
    return help_text


# проверка на разрешенного пользователя
def is_allow_user(iduser, allow_users):
    for user in allow_users:
        if user.id == iduser:
            return True
    return False


# добавляем пользователя в БД пользователей которые имеют доступ к боту
# возвращает True 
def add_new_user(id, settings):
    new_user = User(id=id)
    settings.add_user(new_user)
    return True


# возвращает список пользователей которые имеют доступ к боту
def read_user_db(settings):
    result = []
    clients = settings.get_all_user()
    for cl in clients:
        result.append(cl.__str__())
    return result


async def get_name_user(client, user_id):
    """
        получаем информацию о пользователе телеграмма по его user_id (user_id тип int)
    """
    try:
        new_name_user = await client.get_entity(user_id)
        new_name_user = new_name_user.first_name
    except ValueError as err:
        print('Ошибка получения информации о пользователе по id: ', err)
        new_name_user = ''
    return new_name_user


async def check_name_user_empty(client, sender_id, db):
    """
        проверим есть ли у этого пользователя имя пользователя в нашей БД настроек
        возвращает имя пользователя
    """
    user_name = db.get_user(sender_id)
    # print(f'Имя пользователя в БД {user_name}')
    user_name_tlg = await get_name_user(client, sender_id)
    # print(f'Имя пользователя в Телеграмме {user_name_tlg}')
    if len(user_name.name) == 0:
        user_name.name = user_name_tlg
        db.update_user(user_name)
    return user_name


def allow_user_id(users):
    result = []
    for user in users:
        result.append(user.id)
    return set(result)


# ----- END Вспомогательные функции


# @bot.on(events.CallbackQuery)
# async def handler(event):
#     await event.answer('You clicked {}!'.format(event.data))


# выполнение команды /start
@bot.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id

    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    user_name = await check_name_user_empty(event.client, sender_id, settings)

    if user_name.role == Role.admin:
        buttons = button_main_admin
    else:
        buttons = button_main_user

    await event.respond(f"Привет, {user_name.name}! Я рад видеть тебя!\n" \
                        "Этот бот выполняет ваши команды.",
                        buttons=buttons)
    raise events.StopPropagation


# выполнение команды /about
@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/about'))
# параметр chats - множество id пользователей которые имеют доступ к методу
async def about_cmd(event):
    print(allow_user_id(settings.get_all_user()))
    await event.respond("Я выполняю ваши команды.")


# выполнение команды /help
@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/help'))
async def help_cmd(event):
    sender = await event.get_sender()
    await event.respond(get_help('help.txt'))


# -------------------- команды администрирования пользователей телеграмм бота ----------------------------------
@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/admin'))
async def admin_cmd(event):
    sender = await event.get_sender()
    await event.respond("Вы вошли в режим администратора",
                        buttons=button_admin)


@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/AddUser'))
async def add_user_admin(event):
    # sender = await event.get_sender()
    await event.respond("Выполняется команда /AddUSer")
    # диалог с запросом информации нужной для работы команды /AddUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя"
                                "который нужно добавить для доступа к боту:")
        id_new_user = await conv.get_response()
        id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)
        while not all(x.isdigit() for x in id_new_user):
            await conv.send_message("ID нового пользователя - это число. Попробуйте еще раз.")
            id_new_user = await conv.get_response()
            id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)

        new_name_user = await get_name_user(event.client, int(id_new_user))

        print('Имя нового пользователя', new_name_user)
        add_new_user(id_new_user, settings)
        await conv.send_message(f"Добавили нового пользователя с ID: {id_new_user} с именем {new_name_user}")


@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/DelUser'))
async def del_user_admin(event):
    # sender = await event.get_sender()
    await event.respond("Выполняется команда /DelUSer")
    # диалог с запросом информации нужной для работы команды /DelUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя "
                                "который нужно запретить доступ к боту")
        id_del_user = await conv.get_response()
        id_del_user = id_del_user.message
        while not any(x.isdigit() for x in id_del_user):
            await conv.send_message("ID пользователя - это число. "
                                    "Попробуйте еще раз.")
            id_del_user = await conv.get_response()
            id_del_user = id_del_user.message
        # проверяем на то если пользователь админ который захочет удалить себя это не получится
        if not is_allow_user(int(id_del_user), admin_client):
            settings.del_user(int(id_del_user))
            await conv.send_message(f"Пользователю с ID: {id_del_user} "
                                    "доступ к боту запрещен.")
        else:
            await conv.send_message("Удаление пользователя с правами администратора запрещено.")


@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/InfoUser'))
async def info_user_admin(event):
    ids = read_user_db(settings)
    ids = [str(x) for x in ids]
    strs = '\n'.join(ids)
    await event.respond(f"Пользователи которые имеют доступ:\n{strs}")


@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/ExitAdmin'))
async def exit_admin_admin(event):
    sender = await event.get_sender()
    await event.respond(f"Вы вышли из режима администратора.",
                        buttons=button_main_admin)


# -------------------- END команды администрирования пользователей телеграмм бота ----------------------------------


# ---------------------- Команды settings

@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/settings'))
async def settings_cmd(event):
    await event.respond("Вы вошли в режим настроек пользователя",
                        buttons=button_settings)


@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='/ExitSettings'))
async def exit_settings_cmd(event):
    sender = await event.get_sender()
    sender_id = sender.id
    user_name = await check_name_user_empty(event.client, sender_id, settings)

    if user_name.role == Role.admin:
        buttons = button_main_admin
    else:
        buttons = button_main_user

    await event.respond("Вы вышли из режима настроек пользователя.", buttons=buttons)


# ---------------------- END Команды settings


# ---------------------- Команды для телеграмм бота которые образуют его основные функции
@bot.on(events.NewMessage(chats=allow_user_id(settings.get_all_user()), pattern='ls|dir'))
async def run_cmd_one(event):
    """
    пример реализации команды ls Linux
    """
    # выделение параметра команды
    message_text = event.raw_text.split()
    # print(message_text)

    param_cmds = ''
    if len(message_text) > 1:
        param_cmds = message_text[1]

    print(param_cmds)
    # проверка существования папки
    if not os.path.exists(param_cmds):
        await event.respond(f"Папки {param_cmds} не существует.")
        return

    # команда которая будет выполняться на сервере
    cmds = f"ls {param_cmds}"

    await event.respond(f"Выполняем команду {cmds}")

    done, _ = await asyncio.wait([run_cmd(cmds)])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(f"!!!! код: {code} \n" f"Внутренняя ошибка: {error}")
        return

    result = result.decode("utf-8")
    str_result = result  # result.split("\n")

    await event.respond(f"Результат: \n {str_result}")


# ---------------------- END Команды для телеграмм бота которые образуют его основные функции


def main():
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
