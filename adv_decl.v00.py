#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import argparse
import sys
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import csv
import gspread

# def parse_cmdline(args):
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-n", "--dry-run", help="Do not make any changes",
#                         action="store_true")
#     return parser.parse_args(args)


def get_all_data(url_all):
    r = requests.get(url_all)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    uls = soup.find_all("ul",{"class": "cleanList floatList"})
    for ul in uls[0].find_all("li"):
        win = ""
        str = ul.find_all("span", class_="descriptionText")[0].next_element.strip()
        start = str.find('(') + 1
        end = str.find(' st',start)
        win = win + (str[start:end])
        entries.append(win)
    return entries


def open_gsheet():
    gc = gspread.service_account(filename='adv-decl-5f46e18b7139.json')
    gsh = gc.open('adv_decl')
    return gsh


def get_sheet(gsh,n):
    sheet = gsh.get_worksheet(n)
    return sheet


def get_index(sh):
    last_index = len(sh.get_all_values())
    next_row = last_index + 1
    return next_row


def get_last(sh,n):
    last = sh.get_all_values()[n]
    return last


def push_data(worksheet,next_row,entries,last,file):
    entries.append(str(int(last[4]) + int(entries[1])))
    entries.append(str(int(last[5]) + int(entries[3])))
    entries.append(str(int(entries[4]) - int(entries[5])))

    print(entries)
    adv = entries[1]
    noch = entries[2]
    decl = entries[3]
    acc_adv = int(entries[1]) + int(last[4])
    acc_decl = int(entries[3]) + int(last[5])


    worksheet.update_cell(next_row, 1, currentDate)
    worksheet.update_cell(next_row, 2, adv)
    worksheet.update_cell(next_row, 3, noch)
    worksheet.update_cell(next_row, 4, decl)
    worksheet.update_cell(next_row, 5, acc_adv)
    worksheet.update_cell(next_row, 6, acc_decl)
    worksheet.update_cell(next_row, 7, entries[6])

    with open(file, "a") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(entries)
    f.close

def scrape(url,sheet,file):
    entries = get_all_data(url)
    gsh = open_gsheet()
    sh = get_sheet(gsh,sheet)
    index = get_index(sh)
    last = get_last(sh,index - 2)
    print(entries)
    # cmdline = parse_cmdline(sys.argv[1:])
    # if cmdline.dry_run:
    if 'DRYRUN' in os.environ:
        if "dry" in os.environ.get('DRYRUN'): 
            print("Running dry. No changes will be made.")
        else:
            # check if we have a record for today
            if currentDate not in last:
                print("let's do it")
                push_data(sh,index,entries,last,file)



if __name__ == "__main__":
    
    # initialise some vars
    file_all = "adv_decl_all.csv"
    file_fastigh ="adv_decl_fastigh.csv"
    currentDate = datetime.today().strftime('%Y-%m-%d')
    tmp_date = ""
    url_all = "https://www.avanza.se/aktier/vinnare-forlorare.html"
    url_fastigh = "https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=53&timeUnit=TODAY"
    url_omxs30 = "https://www.avanza.se/index/om-indexet.html/19002/omx-stockholm-30"
    url_omxspi = "https://www.avanza.se/index/om-indexet.html/19002/omx-stockholm-30"

    print(currentDate)
    entries = []
    entries.append(currentDate)
    scrape(url_all,1,file_all)
    entries = []
    entries.append(currentDate)
    scrape(url_fastigh,2,file_fastigh)
