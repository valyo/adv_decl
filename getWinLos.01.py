#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import re
import codecs
from bs4 import BeautifulSoup
import requests
import requests.packages.urllib3
import sqlite3 as lite
from operator import itemgetter
from datetime import datetime, timedelta

# from HTMLParser import HTMLParser
# from IPython.core.debugger import Tracer

# get rid of a warning message
requests.packages.urllib3.disable_warnings()

# fix for encoding issue with swedish characers
# reload(sys)
# sys.setdefaultencoding('utf8')

currentDate = datetime.today().strftime('%Y-%m-%d')

def connectDB():

    db_file = dir_path + "/win_los.sqlite"
    return  lite.connect(db_file)


entries = []

def get_tables_data(tables):
    for tr in tables[0].find_all("tr"):
        win = []
        # print(tr.find_all("a", class_="link")[0].string.encode('utf-8'))
        sname = tr.find_all("a", class_="link")[0].string.encode('utf-8')
        win.append(sname.decode('utf-8').strip())
        # print(tr.find_all("a", class_="link")[0].get('href'))
        slink =  tr.find_all("a", class_="link")[0].get('href').replace("/aktier/om-aktien.html/", "")
        win.append(slink)
        # print(tr.find("td", class_="positive changePercent").string.encode('utf-8'))
        # print(tr.find("td", class_="positive changePercent").string)
        pchange = tr.find("td", class_="positive changePercent").string.replace(",", ".")
        win.append(pchange)
        plast = tr.find("td", class_="lastPrice last").string.replace(",", ".")
        win.append(plast)
        win.append(currentDate)
        win.append("W")
        entries.append(win)
        # print(win)

    for tr in tables[1].find_all("tr"):
        los = []
        sname = tr.find_all("a", class_="link")[0].string.encode('utf-8')
        los.append(sname.decode('utf-8').strip())
        # print tr.find_all("a", class_="link")[0].get('href')
        slink = tr.find_all("a", class_="link")[0].get('href').replace("/aktier/om-aktien.html/", "")
        los.append(slink)
        # print tr.find("td", class_="negative changePercent").string.encode('utf-8')
        pchange = tr.find("td", class_="negative changePercent").string.replace(",", ".")
        los.append(pchange)
        plast = tr.find("td", class_="lastPrice last").string.replace(",", ".")
        los.append(plast)
        los.append(currentDate)
        los.append("L")
        entries.append(los)
    return entries


url_stchlm = "https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&marketPlaceCodes=XSTO&timeUnit=TODAY"
r = requests.get(url_stchlm)
data = r.text
soup = BeautifulSoup(data, "html.parser")
all_tables = soup.find_all("tbody")

res = get_tables_data(all_tables)

dir_path = os.path.dirname(os.path.realpath(__file__))

db = connectDB()
cur = db.cursor()

# print "today is " + currentDate

# check if we already have a record for today
query1 = "Select count(*) from win_los where date = \'%s\'" % currentDate
cur.execute(query1)
present = cur.fetchone()[0]

# if we don't have 80 records, insert the scraped data
if present < 80 :

    print(present)

    for r in res:
        print(r[0])
        # query = u"INSERT OR REPLACE INTO win_los (sname, slink, pchange, plast, date, type) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');" % (r[0], r[1], r[2], r[3], r[4], r[5])
        try:
            cur.execute("INSERT OR REPLACE INTO win_los (sname, slink, pchange, plast, date, type) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');" % (r[0], r[1], r[2], r[3], r[4], r[5]))
            db.commit()
        except Exception as e:
            raise e
