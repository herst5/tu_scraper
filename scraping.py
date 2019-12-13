# -*- coding: utf-8 -*-
import requests
import csv
import sys
from bs4 import BeautifulSoup
from functools import total_ordering
from datetime import datetime as d
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from logging import getLogger, config
import os
import yaml

@total_ordering
class News:
    """News class"""

    def __init__(self):
        self.date = ""
        self.title = ""
        self.url = ""

    def getDate(self):
        return self.date

    def getTitle(self):
        return self.title

    def getUrl(self):
        return self.url

    def setDate(self, date):
        self.date = date

    def setTitle(self, title):
        self.title = title

    def setUrl(self, url):
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, News):
            return NotImplemented
        return (self.date, self.title, self.url) == (other.date, other.title, other.url)

    def __lt__(self, other):
        if not isinstance(other, News):
            return NotImplemented
        return (self.date, self.title, self.url) < (other.date, other.title, other.url)

def create_message(from_addr, to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    return msg

def send(host, from_addr, my_password, to_addrs, msg):
    smtpobj = smtplib.SMTP_SSL(host, 465, timeout=10)
    smtpobj.login(from_addr, my_password)
    smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
    smtpobj.close()

SUBJECT_FORMAT="{} {}件の新しいお知らせが掲載されました"
BODY_FORMAT="新しいお知らせは、以下の通りです。\n\n\n{}\n以上"

config.fileConfig('logging.conf')
logger = getLogger(__name__)

def main():

    logger.info("Scraping Program Start")

    if not(os.path.exists('fromAddr.yaml')):
        logger.error("ERROR! fromAddr.yaml doesn't exist.")
        logger.info("Scraping Program Abend")
        sys.exit(1)

    if not(os.path.exists('toAddr.txt')):
        logger.error("ERROR! toAddr.txt doesn't exist.")
        logger.info("Scraping Program Abend")
        sys.exit(1)

    res=requests.get('http://www.l.u-tokyo.ac.jp/student/student_news/news_pg.html')

    soup = BeautifulSoup(res.text, "html.parser")

    block = soup.find(class_="block")

    dt = block.find_all("dt")
    dd = block.find_all("dd")

    if(len(dt) != len(dd)):
        logger.error("ERROR! The number of DTs and DDs didn't match up.")
        logger.info("Scraping Program Abend")
        sys.exit(1)

    newsList = []

    for i in range(len(dt)):
        try:
            date = dt[i].text
            title = dd[i].find("a")
            url = dd[i].find("a").attrs['href']

            if (url.startswith("assets/")):
                url = "http://www.l.u-tokyo.ac.jp/student/student_news/" + url

            logger.info("Got a news. Date:" + date +", title:" + title.string + ", url:" + url)

            news = News()
            news.setDate(date)
            news.setTitle(title.string)
            news.setUrl(url)

            newsList.append(news)

        except:
            logger.error("ERROR! Couldn't get a news.")
            pass

    if not(os.path.exists('oldNews.csv')):
        logger.info("oldNews.csv doesn't exist. Create oldNews.csv and end program. Mails won't be sent.")

        for news in newsList:
            with open('oldNews.csv', 'a', encoding='utf-8', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([news.getDate(), news.getTitle(), news.getUrl()])

        logger.info("Scraping Program End")
        sys.exit(0)

    oldNewsList = []

    with open('oldNews.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            news = News()
            news.setDate(row[0])
            news.setTitle(row[1])
            news.setUrl(row[2])
            oldNewsList.append(news)

    newNewsList = []

    for news in newsList:
        match = False
        for oldNews in oldNewsList:
            if (news == oldNews):
                match = True
                break
        if (match):
            continue
        newNewsList.append(news)

    if (len(newNewsList) == 0):
        logger.info("No new news.")
        logger.info("Scraping Program End")
        sys.exit(0)

    logger.info(str(len(newNewsList)) + " new newses were found.")

    newsStr = ""

    for newNews in newNewsList:

        with open('oldNews.csv', 'a', encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([newNews.getDate(), newNews.getTitle(), newNews.getUrl()])

        newsStr += newNews.getTitle()+"\n"+newNews.getUrl()+"\n"

    dateStr = ""

    try:
        tdatetime = d.strptime(newNewsList[0].getDate(), '%Y.%m.%d')
        dateStr = tdatetime.strftime('%Y{0}%m{1}%d{2}').format(*'年月日')
    except:
        dateStr = newNewsList[0].getDate()

    subject = SUBJECT_FORMAT.format(dateStr,str(len(newNewsList)))
    body = BODY_FORMAT.format(newsStr)

    from_addr=""
    my_password=""
    host=""
    with open('fromAddr.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        from_addr = data['from_addr']
        my_password = data['my_password']
        host = data['host']

    to_addrses=[]
    with open('toAddr.txt', encoding='utf-8') as f:
        to_addrses = f.readlines()

    for to_addrs in to_addrses:
        to_addrs = to_addrs.replace('\n','')
        logger.info("Send mail to " + to_addrs)
        msg = create_message(from_addr, to_addrs, subject, body)
        send(host, from_addr, my_password, to_addrs, msg)
        logger.info("Mail was sent.")

    logger.info("Scraping Program End")

if __name__ == "__main__":
    main()
