import os
import time
import dates
from background import keep_alive
from icecream import ic
import telebot
import flask
import requests
from importlib.metadata import version
from groups import parseGroups
from telebot import types
from datetime import datetime
import Parser
from pytz import timezone

# import requests
# from bs4 import BeautifulSoup as BS
format = "%Y-%m-%d %H:%M:%S"
token = "5830418531:AAHNwKbINt9OCYUXaWAE7k7TZSAlpO0y39g"
bot = telebot.TeleBot(token)


####Start#####


MainReply = types.ReplyKeyboardMarkup(resize_keyboard=True)
feedback = types.KeyboardButton('🔷Обратная связь🔷')
nextW = types.KeyboardButton('Следующая неделя➡️')
MainReply.add(feedback, nextW)
main_buttons = [feedback, nextW]

AdminReply = types.ReplyKeyboardMarkup(resize_keyboard=True)
get_logs = types.KeyboardButton('Показать последние логи бота')
get_mesgs = types.KeyboardButton('Показать последние сообщения')
ex = types.KeyboardButton('Выйти из админпанели')
AdminReply.add(get_logs, get_mesgs, ex)
@bot.message_handler(commands=['start'])
def start(message):
    Mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    feedback = types.KeyboardButton('🔷Обратная связь🔷')
    admin = types.KeyboardButton('АдминПанель')
    Mark.add(feedback)
    start_buttons = [feedback]
    if message.from_user.id == 761686016:
        if len(start_buttons) != 2:
            start_buttons.append(admin)
            Mark.add(admin)

    f_name = message.from_user.first_name if message.from_user.first_name else ''
    l_name = message.from_user.last_name if message.from_user.last_name else ''
    mess = f'Привет, <b>{f_name} <u>{l_name}</u></b>\nЧтобы получить расписание, введи номер своей группы:'
    msg = bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=Mark)

    bot.register_next_step_handler(msg, Timetable)




last_time = {}

try:
    @bot.message_handler(content_types=['text'])
    def Timetable(message):
        start = time.time()
        if message.chat.type == 'private':
            now_utc = datetime.now(timezone('Asia/Yekaterinburg'))
            with open('userMessages.txt', "a+", encoding="utf-8") as a_log:
                a_log.write(
                    f'{now_utc.strftime(format)}--{message.from_user.first_name} {message.from_user.last_name}--{message.text}\n'
                )
            if message.text.isdigit():
                flag = True
                global num, countpress
                countpress = 1
                num = message.text
                # markup_inline = types.InlineKeyboardMarkup()
                # an_yes = types.InlineKeyboardButton(text='Подписаться на рассылку этой группы', callback_data='Acces')
                # markup_inline.add(an_yes)

                if message.from_user.id == 761686016:
                    admin = types.KeyboardButton('АдминПанель')
                    if len(main_buttons) != 3:
                        main_buttons.append(admin)
                        MainReply.add(admin)
                if message.chat.id not in last_time:
                    last_time[message.chat.id] = time.time()
                else:
                    if (time.time() - last_time[message.chat.id]) * 1000 < 5000:
                        bot.send_message(message.chat.id,
                                         'Слишком частые запросы, подожди 5 секунд!')
                        return 0
                mssg = bot.send_message(message.chat.id, 'Собираю данные... (<i>~5 секунд</i>)', reply_markup=MainReply, parse_mode='html')
                parseGroups()
                last_time[message.chat.id] = time.time()
                mes = ''
                while flag:
                    bot.send_chat_action(message.chat.id, 'typing')
                    mes = Parser.parse(num, dates.day, dates.month, dates.year)
                    flag = False
                # bot.send_chat_action(message.chat.id, 'typing')
                # time.sleep(1)
                #             bot.edit_message_text(chat_id=message.chat.id,
                #                         message_id=message.message_id + 1,
                #                         text=mes,
                #                         parse_mode='html',
                # disable_web_page_preview=True)
                time.sleep(1)
                bot.delete_message(message.chat.id, mssg.message_id)
                bot.send_message(message.chat.id,
                                 mes,
                                 parse_mode='html',
                                 disable_web_page_preview=True, reply_markup=MainReply)

            elif message.text == 'Следующая неделя➡️':
                if message.chat.id not in last_time:
                    last_time[message.chat.id] = time.time()
                else:
                    interval = (time.time() - last_time[message.chat.id]) * 5000
                    if interval < 500:
                        bot.send_message(message.chat.id,
                                         'Слишком частые запросы, подожди 5 секунд!')
                        return 0
                last_time[message.chat.id] = time.time()
                try:
                    mssg = bot.send_message(message.chat.id, 'Собираю данные...(<i>~5 секунд</i>)', parse_mode='html')
                    mes = Parser.parse(num, dates.day + 7 * countpress, dates.month, dates.year)
                    bot.delete_message(message.chat.id, mssg.message_id)
                    bot.send_message(message.chat.id, mes, parse_mode='html', disable_web_page_preview=True)
                    countpress += 1
                except NameError as E:
                    print(f"ERROR: {E}")
                    bot.send_message(message.chat.id, 'Сперва введите номер группы')
                    return 0
            # Вывод обратной связи
            elif message.text == '🔷Обратная связь🔷':
                mes = ('<b><i>Если заметили какой - то баг или бот просто встал, пишите на ниже указанные '
                       'контакты</i></b>\n\t<a href="https://vk.com/extazyice">🔻VK</a>\n <a '
                       'href="https://discordapp.com/users/472111376324886529/">🔻Discord</a>\n <a '
                       'href="mailto:extazyice2002@gmail.com">🔻Почта</a>')
                bot.send_message(message.chat.id, mes, parse_mode='html', disable_web_page_preview=True)
            elif message.text == 'АдминПанель':
                if message.from_user.id == 761686016:
                    msg = bot.send_message(message.chat.id, 'Вы в панели админа!', reply_markup=AdminReply)
                    bot.register_next_step_handler(msg, AdminPanel)
            else:
                bot.send_message(message.chat.id, "Введите номер группы")

    @bot.message_handler(content_types=['text'])
    def AdminPanel(message):

        if message.chat.type == 'private':
            if message.text == 'Показать последние логи бота':
                logs = ''
                with open('logs.txt', 'r') as f:
                    for line in (f.readlines()[-20:]):
                        logs += line + '\n'
                msg = bot.send_message(message.chat.id, 'Последние 20 логов:\n' + logs, reply_markup=AdminReply)
                bot.register_next_step_handler(msg, AdminPanel)
            elif message.text == 'Показать последние сообщения':
                msgs = ''
                with open('userMessages.txt', 'r', encoding='utf-8') as f:
                    for line in (f.readlines()[-20:]):
                        msgs += line + '\n'
                msg = bot.send_message(message.chat.id, 'Последние 20 сообщений:\n' + msgs, reply_markup=AdminReply)
                bot.register_next_step_handler(msg, AdminPanel)
            elif message.text == 'Выйти из админпанели':
                msg = bot.send_message(message.chat.id, 'Вы вышли из админпанели',reply_markup=MainReply)
                bot.register_next_step_handler(msg, Timetable)
except Exception as e:
    with open('logs.txt', 'a+') as log:
        now_utc = datetime.now(timezone('Asia/Yekaterinburg'))
        log.write(f'{now_utc.strftime(format)} -- {e}')

# RUN
keep_alive()
bot.polling(none_stop=True, timeout=123)
