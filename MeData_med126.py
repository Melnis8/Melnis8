# coding=gb2312
# @Author : Melnis
# @Time : 2024/10/25 21:20
# @File : MeData_med126
# @Project : PycharmProjects

from __future__ import unicode_literals
import pandas as pd
import requests
from lxml import etree
from bs4 import BeautifulSoup
import csv
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session


def random_sleep(mu=1, sigma=0.4):
    secs = random.normalvariate(mu, sigma)
    if secs <= 0:
        secs = mu
    time.sleep(secs)


def get_data(url):

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    }
    proxies = {
        "http": "39.105.27.30:3128"
    }
    session = Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(url, headers=headers, timeout=30)
    response.encoding = 'gbk'
    random_sleep()
    return response

if __name__ == '__main__':
    url = 'https://m.med126.com/drug/data/manual/'
    main = get_data(url)
    # print(main.text)
    main_page = BeautifulSoup(main.text, 'lxml')
    divs = main_page.find_all("div", attrs={"class":"lm_top"})
    sec_urls = []
    trd_urls = []
    for div in divs:
        href = div.find('a')
        # print(href['href'])
        sec_urls.append('https://m.med126.com/'+href['href'])
    # print(sec_urls)
    for sl in sec_urls:
        sec = get_data(sl)
        sec_page = BeautifulSoup(sec.text,'lxml')
        hrefs = sec_page.find_all("a", class_="e")
        for href in hrefs:
            url = 'https://m.med126.com/' + href['href']
            # print(url)
            trd_urls.append(url)
index_list = list(range(1, len(trd_urls) + 1))
for tl in trd_urls:
    med = get_data(tl)
    med_page = BeautifulSoup(med.text,'lxml')
    name = med_page.find("div", class_="timu").text
    print(name)
    tree = etree.HTML(med.text)
    type = tree.xpath('//*[@id="dbu"]/div[4]/a[5]/text()')[0]
    print(type)
    table = med_page.find_all("table")[2]
    tds = table.find_all("td")
    feature = tds[11].text  # xingzhuang
    yldl = tds[13].text  #yaoliduli
    print(yldl)
    yddlx = tds[15].text
    syz = tds[17].text  # shiyingzheng
    print(syz)
    yfyl = tds[19].text
    print(yfyl)
    blfy = tds[21].text
    print(blfy)
    jjz = tds[23].text
    print(jjz)
    zysx = tds[25].text
    print(zysx)
    preg = tds[27].text
    kid = tds[29].text
    eld = tds[31].text
    xhzy = tds[33].text
    ywgl = tds[35].text
    storage = tds[37].text
    pack = tds[39].text
    times = tds[41].text


    data = {
        '通用名': name,
        '药品类别': type,
        '性状': feature,
        '药理毒理': yldl,
        '药代动力学':yddlx,
        '适应症': syz,
        '用法用量': yfyl,
        '不良反应': blfy,
        '禁忌症': jjz,
        '注意事项': zysx,
        '孕妇及哺乳期妇女用药': preg,
        '儿童用药': kid,
        '老年患者用药': eld,
        '药物相互作用': xhzy,
        '药物过量': ywgl,
        '贮藏': storage,
        '包装': pack,
        '有效期': times
    }
    print(data)
    df = pd.DataFrame(data, index=index_list)
    df.to_csv('med126.csv', index=False, encoding='utf-8')
