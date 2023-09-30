from datetime import date, timedelta

today = date.today()

den = today.weekday()
if den == 6:
    today = today + timedelta(2)
#Today
day = today.day
month = today.month
year = today.year
#NextWeek
NextDate = date.today() + timedelta(7)

nDay = NextDate.day
nMonth = NextDate.month
nYear = NextDate.year
#PrevWeek
PrevDate = date.today() - timedelta(7)
pDay = PrevDate.day
pMonth = PrevDate.month
pYear = PrevDate.year