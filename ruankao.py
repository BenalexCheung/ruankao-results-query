#!/usr/bin/python3
# -*- coding: utf-8 -*-

from ast import Try
from time import sleep
from numpy import empty
import requests
from bs4 import BeautifulSoup
import ddddocr
import logging

STAGE = '2022年上半年'
KEY_WORD = '%s计算机技术与软件专业技术资格(水平)考试成绩' % STAGE

CANDIDATE_NAME = '张三'  # 准考证姓名
CANDIDATE_NO = '20228888888888888'  # 准考证号 or 身份证号
SELECT_TYPE = '0'  # 0: 准考证号 1: 身份证号

PUSH_KEY = 'xxx'  # 推送消息的key


def init_log():
    logging.basicConfig(
        level=logging.INFO  # 设置日志输出格式
        ,
        filename="/var/log/ruankao.log"  # log日志输出的文件位置和文件名
        ,
        # 日志输出的格式
        # -8表示占位符，让输出左对齐，输出长度都为8位
        format="%(asctime)s %(filename)-8s [line: %(lineno)s] : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # 时间输出的格式
    )


def check_result():
    try:
        response = requests.get("https://www.ruankao.org.cn/index/work")
    except:
        logging.warn("Failed to get response, retrying")
        sleep(600)
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        newsList = soup.findAll('ul', attrs={"class": "ui-item15 newsList"})
        for title in newsList:
            if KEY_WORD in title.text:
                return True
    return False


def query_result():
    response1 = requests.get(
        'https://query.ruankao.org.cn//score/captcha?1654599907554')
    with open('/tmp/captcha.png', 'wb') as f:
        f.write(response1.content)

    ocr = ddddocr.DdddOcr(show_ad=False)
    with open('/tmp/captcha.png', 'rb') as f:
        image_bytes = f.read()

    captcha = ocr.classification(image_bytes)
    logging.info(captcha)

    data = {"captcha": captcha}
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    response2 = requests.post(
        'https://query.ruankao.org.cn//score/VerifyCaptcha',
        data=data,
        headers=headers,
        cookies=response1.cookies.get_dict())

    logging.info(response2.json()["flag"])

    if response2.json()["flag"] == 1:
        params = {
            'stage': STAGE,
            'xm': CANDIDATE_NAME,
            'zjhm': CANDIDATE_NO,
            'jym': captcha,
            'select_type': SELECT_TYPE
        }
        response3 = requests.post('https://query.ruankao.org.cn//score/result',
                                  data=params,
                                  headers=headers,
                                  cookies=response1.cookies.get_dict())
        logging.info(response3.json()["flag"])
        if response3.json()["flag"] == 1:
            SWCJ = float(response3.json()["data"]["SWCJ"])
            XWCJ = float(response3.json()["data"]["XWCJ"])
            LWCJ = float(response3.json()["data"]["LWCJ"])

            prefix = '恭喜通过考试!'
            if SWCJ < 45 or XWCJ < 45 or LWCJ < 45:
                prefix = '很遗憾, 请再接再厉!'
            msg = "%s %s%s: 上午成绩%s, 下午成绩%s, 论文成绩%s" % (prefix, response3.json()["data"]["KSSJ"], response3.json()["data"]["ZGMC"], response3.json()[
                "data"]["SWCJ"], response3.json()["data"]["XWCJ"], response3.json()["data"]["LWCJ"])
            return msg
    return ""


def push_result(msg=""):
    pushurl = 'https://api2.pushdeer.com/message/push?pushkey={0}&text={1}'.format(
        PUSH_KEY, msg)
    response = requests.get(pushurl)
    if response.status_code == 200:
        return True
    else:
        return False


def main():
    ret = 1
    if check_result():
        logging.info("The results have been announced, please check in time")
        push_result("%s软考成绩已公布, 请及时查询" % STAGE)
        sleep(2)
        while True:
            result = query_result()
            if result == "":
                logging.warn("Failed to query results, retrying")
                sleep(2)
            else:
                logging.info("The score is: %s" % result)
                push_result("%s软考, %s" % (STAGE, result))
                ret = 0
                break
    return ret


if __name__ == '__main__':
    init_log()
    while main():
        logging.info("Results have not been announced yet, please be patient")
        sleep(60)
