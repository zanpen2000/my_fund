import datetime
import json
import openpyxl

import requests
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

excel_file = './Fund.xlsx'

# Server酱 key http://sc.ftqq.com/
sckey = 'SCU88470T2b933a481a8f217a209c8482c05e0f535e64b2a99dff4'

# 聚合接口 key https://www.juhe.cn/docs/api/id/25
jvhe_key = 'd91966e95b003374d512c746a805af69'

scheduler = BlockingScheduler()


def send_msg(title, text):
    msg_push_url = F"https://sc.ftqq.com/{sckey}.send?text={title}&desp={text}"
    resp = requests.get(msg_push_url)
    logger.debug(resp)
    logger.info(F"{datetime.datetime.now()}: 已将消息推送到微信")


def get_timestamp():
    millis = int(round(time.time() * 1000))
    return millis


def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


def get_fund_valuation(code):
    ts = get_timestamp()
    url = F"http://fundgz.1234567.com.cn/js/{code}.js?rt={ts}"
    content = get_url(url)[8:-2]
    json_data = json.loads(content)
    logger.debug(F"{datetime.datetime.now()}: {content} ")
    return json_data


def update_fund_value():
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb['基金']
    green_fund_list = ["|名称|成本单价|估值|跌幅|", "| :---- | :-------- | ----: | ---: |"]
    for r in sheet.rows:
        fund_code = str(r[0].value)
        if fund_code[0] in '0123456789':
            data = get_fund_valuation(fund_code)  # get val and write back
            from openpyxl.styles import numbers, colors, Font
            r[4].number_format = r[7].number_format = r[8].number_format = numbers.FORMAT_GENERAL
            r[9].number_format = numbers.FORMAT_PERCENTAGE_00
            r[7].value, r[8].value, r[9].value = float(data['dwjz']), float(data['gsz']), float(data['gszzl']) / 100
            if r[4].value > r[8].value:
                p = str(round(float((((r[8].value - r[4].value) / r[4].value) * 100)), 2)) + '%'
                line = F"|{r[1].value} | {r[4].value} | {r[8].value}| {p} "
                green_fund_list.append(line)
                r[8].font = Font(color=colors.RED)

    wb.save(excel_file)
    wb.close()
    if len(green_fund_list) > 0:
        send_msg(F'共有{len(green_fund_list)}只基金估算净值低于成本单价', '\r\n'.join(green_fund_list))


def get_fund_val():
    """判断是否交易日，是否交易时间，然后获取估值信息"""
    import tradeday
    if tradeday.today_is_trade_day():
        update_fund_value()


def add_schedule_jobs():
    scheduler.add_job(get_fund_val, "cron", hour='9-11', minute=30, id='get_fund_val1')
    scheduler.add_job(get_fund_val, "cron", hour='13-14', minute=10, id='get_fund_val2')
    scheduler.add_job(get_fund_val, "cron", hour='22-23', minute=30, id='get_fund_val3')
    # just for debug
    # scheduler.add_job(get_fund_val, "interval", minutes=1, id='get_fund_val4')


if __name__ == '__main__':
    logger.info(F"{datetime.datetime.now()}: 定时任务已启动，将分别在9:30,10:30,11:30,13:10,14:10,22:30,23:30获取持仓基金估值信息")
    add_schedule_jobs()
    scheduler.start()
