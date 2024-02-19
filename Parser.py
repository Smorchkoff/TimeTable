from datetime import date

import requests
from bs4 import BeautifulSoup as BS
from groups import parseGroups
import json
import re

rulesDW = {'<div>': '', '</div>': '', '\t': '', '\r': '', '\n': ' '}
rulesObj = {
    '\r': '',
    '\n': '',
    '\t': '',
    '\\[<td><span class="blue lowercase">': '',
    '</span>': '',
    '                                                        ': '',
    '        </td>\\]': '',
    '        </td>': '',
    '</td>\\]': '',
    '<td><span class="blue lowercase">': ''
}
rulesPG = {'\r': '', '\n': '', '\t': '', '0': ''}


def filtering(rules, string):
    for k, v in rules.items():
        string = re.sub(k, v, string)
    return string


def parse(numberOfGroup, day, month, year):
    mes = ''
    with open('groups.txt') as f:
        data = f.read()
    current_day = date.today().day
    print(current_day)
    dictGroups = json.loads(data)
    if dictGroups.get(numberOfGroup) is None:
        mes = 'Введенная вами группа не была найдена, либо вы написали какой - то бред :)'
        return mes
    else:
        r = requests.get(
            f'http://timetable.nvsuedu.ru/tm/index.php/timetable/show_timetable/group/{dictGroups.get(numberOfGroup)}//0/?date={day}_{month}_{year}'
        )
        soup = BS(r.content, "html.parser")
        gr_ls = list(soup.find_all('span', class_='target')[0].children)
        num_gr = gr_ls[0]
        name_gr = gr_ls[2]
        mes += '🔘' + num_gr + f" <b>{name_gr}</b>" + '\n'

        # ОбщийЦикл
        try:
            Cicle1 = soup.find('table', class_='table gradient-table').findAll('thead')
            for day in Cicle1:
                DayWeek = day.find('div', class_='')
                test = day.find('td', class_='title inactive-gradient')
                if DayWeek is not None:
                    DayWeek = str(DayWeek)
                    DayWeek = filtering(rulesDW, DayWeek)
                    DayWeek = DayWeek.replace(' ', '', 1)

                    today = '\t' * 30+'<b><u>СЕГОДНЯ</u></b>' if current_day == int(re.search(r'\d+', DayWeek)[0]) else ''

                    mes += f"\n{today}\n" + "⬛️" * 2 + '<b>' + DayWeek + f"</b>" + "⬛️" * 2 + '\n\n'
                    if test is not None:
                        mes += '🎉\tЗанятий нет🎉\n'
                    else:
                        tr = day.find_next('tbody')
                        trs = tr.findAll('tr', class_='')
                        for line in trs:
                            obj = line.select('td:has(>span, a.blue)')
                            obj = str(obj)
                            obj = filtering(rulesObj, obj)
                            obj = "".join(obj.rstrip())
                            obj = obj.replace(
                                'Элективные дисциплины (модули) по физической культуре и спорту',
                                'Физра')
                            time = line.find('td', class_='time').find('div').text
                            if time is not None:
                                mes += '⬜️<b><i>' + time[:6] + "- " + time[6:] + "</i></b>\t"
                            podgruppa = line.find('td', class_='center', attrs={"width": "1"})
                            if podgruppa is not None:
                                podgruppa = podgruppa.text
                                if podgruppa == '\n':
                                    podgruppa = str(podgruppa)
                                    podgruppa = podgruppa.replace('\n', 'Общая')
                                podgruppa = filtering(rulesPG, podgruppa)
                                mes += '<i>' + podgruppa + "</i>\t"
                            else:
                                podgruppa = '<i>Общая</i>'
                                mes += podgruppa + '\t'
                            mes += '<u>' + obj + '</u>\t'
                            cabs = line.findAll('td', class_='blue center')
                            for cab in cabs:
                                cabinet = cab.find('a').text
                                if cabinet == 'в.з.-Дистанционная':
                                    cabinet = str(cabinet)
                                    cabinet = cabinet.replace('в.з.-Дистанционная', 'Дистант')
                                mes += '<i>' + cabinet + '</i>\n'
        except AttributeError:
            mes = f'\n\n{"⬛️" * 2}<b>Понедельник</b>{"⬛️" * 2}\n\n⚠️\tРасписание отсутствует⚠️\n' \
                  f'\n\n{"⬛️" * 2}<b>Вторник</b>{"⬛️" * 2}\n\n⚠️\tРасписание отсутствует⚠️\n' \
                  f'\n\n{"⬛️" * 2}<b>Среда</b>{"⬛️" * 2}\n\n⚠️\tРасписание отсутствует⚠️\n' \
                  f'\n\n{"⬛️" * 2}<b>Четверг</b>{"⬛️" * 2}\n⚠️\tРасписание отсутствует⚠️\n' \
                  f'\n\n{"⬛️" * 2}<b>Пятница</b>{"⬛️" * 2}\n⚠️\tРасписание отсутствует⚠️\n' \
                  f'\n\n{"⬛️" * 2}<b>Суббота</b>{"⬛️" * 2}\n\n⚠️\tРасписание отсутствует⚠️\n'

        return mes
