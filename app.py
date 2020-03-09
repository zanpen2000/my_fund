import datetime
import json
import openpyxl

import requests
import time
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

excel_file = '/home/peng/文档/fund/Fund.xlsx'

# Server酱 key http://sc.ftqq.com/
sckey = 'SCU88470T2b933a481a8f217a209c8482c05e0f535e64b2a99dff4'

# 聚合接口 key https://www.juhe.cn/docs/api/id/25
jvhe_key = 'd91966e95b003374d512c746a805af69'


def send_msg(title, text):
    msg_push_url = F"https://sc.ftqq.com/{sckey}.send?text={title}&desp={text}"
    resp = requests.get(msg_push_url)
    logger.debug(resp)
    logger.info("已将消息推送到微信")


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
    now = datetime.datetime.now()
    json_data = json.loads(get_url(url)[8:-2])
    logger.info(F"{now}: {json_data['jzrq']} {json_data['name']}<{code}> -> {json_data['dwjz']} ")
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
    send_msg('以下基金估算净值低于成本单价', '\r\n'.join(green_fund_list))


def get_fund_jz(page_num, page_size):
    url = F"http://v.juhe.cn/jingzhi/query.php?page={page_num}&pagesize={page_size}&type=all&key={jvhe_key}"
    pass


if __name__ == '__main__':
    update_fund_value()
    logger.info("\n基金估值已更新.")
