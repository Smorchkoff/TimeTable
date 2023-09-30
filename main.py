import os
import time
import dates
from background import keep_alive
import telebot
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
@bot.message_handler(commands=['start'])
def start(message):
    Mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    feedback = types.KeyboardButton('🔷Обратная связь🔷')
    Mark.add(feedback)
    mess = f'Привет, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>\nЧтобы получить расписание, введи номер своей группы:'
    msg = bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=Mark)
    bot.register_next_step_handler(msg, Timetable)


last_time = {}

try:
    @bot.message_handler(content_types=['text'])
    def Timetable(message):
        if message.chat.type == 'private':
            now_utc = datetime.now(timezone('Asia/Yekaterinburg'))
            with open('userMessages.txt', "w", encoding="utf-8") as a_log:
                a_log.write(
                    f'{now_utc.strftime(format)}--{message.from_user.first_name} {message.from_user.last_name}--{message.text}\n'
                )
            if message.text.isdigit():
                global num, countpress
                countpress = 1
                num = message.text
                # markup_inline = types.InlineKeyboardMarkup()
                # an_yes = types.InlineKeyboardButton(text='Подписаться на рассылку этой группы', callback_data='Acces')
                # markup_inline.add(an_yes)
                replyM = types.ReplyKeyboardMarkup(resize_keyboard=True)
                feedback = types.KeyboardButton('🔷Обратная связь🔷')
                nextW = types.KeyboardButton('Следующая неделя➡️')
                replyM.add(feedback, nextW)

                if message.chat.id not in last_time:
                    last_time[message.chat.id] = time.time()
                else:
                    if (time.time() - last_time[message.chat.id]) * 1000 < 5000:
                        bot.send_message(message.chat.id,
                                         'Слишком частые запросы, подожди 5 секунд!')
                        return 0
                mssg = bot.send_message(message.chat.id, 'Собираю данные...', reply_markup=replyM)
                parseGroups()
                last_time[message.chat.id] = time.time()
                mes = Parser.parse(num, dates.day, dates.month, dates.year)
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
                                 disable_web_page_preview=True, reply_markup=replyM)
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
                    mssg = bot.send_message(message.chat.id, 'Собираю данные...')
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
            else:
                bot.send_message(message.chat.id, "Введите номер группы")
except Exception as e:
    with open('logs.txt', 'w') as log:
        now_utc = datetime.now(timezone('Asia/Yekaterinburg'))
        log.write(f'{now_utc.strftime(format)} -- {e}')

# RUN
keep_alive()
bot.polling(none_stop=True)
