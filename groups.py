import requests
from bs4 import BeautifulSoup as BS
import json
import dates


def parseGroups():
    groups = dict()
    for i in range(1, 8):
        if i != 2:
            r = requests.get(
                f'http://timetable.nvsuedu.ru/tm/index.php/list_of/inst/{i}?date={dates.day}_{dates.month}_{dates.year}'
            )
            soup = BS(r.content, "html.parser")
            tables = soup.findAll('table', class_='table gradient-table')
            for table in tables:
                tds = table.findAll('td', class_='')
                for td in tds:
                    group = td.find('a', class_='block', href=True)
                    if group is not None:
                        hr = str(group['href'])[72:76]
                        num = group.text
                        groups[num] = hr
    with open('groups.txt', 'w') as f:
        f.write(json.dumps(groups))
