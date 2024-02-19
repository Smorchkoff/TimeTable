import requests
from bs4 import BeautifulSoup as BS

r = requests.get(
    f'http://timetable.nvsuedu.ru/tm/index.php/timetable/show_timetable/group/7599//0/?date=02_10_2023'
)
soup = BS(r.content, "html.parser")
gr_ls = list(soup.find_all('span', class_='target')[0].children)
num_gr = gr_ls[0]
name_gr = gr_ls[2]
if __name__ == "__main__":
    print(num_gr)
    print(name_gr)

