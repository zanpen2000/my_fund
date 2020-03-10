import datetime
import time

import requests


def is_trade_day(query_date):
    url = F"http://tool.bitefu.net/jiari/?d={query_date}"
    resp = requests.get(url=url)
    content = resp.text
    return int(content) == 0


def today_is_trade_day():
    query_date = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
    return is_trade_day(query_date)


def in_time_range(ranges):
    now = time.strptime(time.strftime("%H%M%S"), "%H%M%S")
    ranges = ranges.split(",")
    for r in ranges:
        r = r.split("-")
        if time.strptime(r[0], "%H%M%S") <= now <= time.strptime(r[1], "%H%M%S") or \
                time.strptime(r[0], "%H%M%S") >= now >= time.strptime(r[1], "%H%M%S"):
            return True
    return False


def now_is_trade_time(area='cn'):
    """
    :param area:
        cn: am 9:30 - 11:30 pm 13:00 - 15:00
        us: pm: 22:30 - 5:00
    :return: True / False
    """

    if area == 'cn':
        result = in_time_range("093000-113000,130000-150000")
    elif area == 'us':
        result = in_time_range("223000-240000,000000-050000")
    elif area == 'all':
        result = in_time_range("093000-113000,130000-150000,223000-240000,000000-050000")

    return result


if __name__ == '__main__':
    print(today_is_trade_day())
