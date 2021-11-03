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
from time import sleep


# ---- Global variables ----

#TODO   take out the dictionary into adv_decl.config file
links_dict = {
    'adv_decl': 'https://www.avanza.se/aktier/vinnare-forlorare.html',
    'adv_decl_fastigh': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=53&timeUnit=TODAY',
    'adv_decl_allmennyttig': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=210&timeUnit=TODAY',
    'adv_decl_energi': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=100&timeUnit=TODAY',
    'adv_decl_finans': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=148&timeUnit=TODAY',
    'adv_decl_industri': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=31&timeUnit=TODAY',
    'adv_decl_kommunikation': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=66&timeUnit=TODAY',
    'adv_decl_konsument_cykl': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=112&timeUnit=TODAY',
    'adv_decl_konsument_stab': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=108&timeUnit=TODAY',
    'adv_decl_ravaror': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=175&timeUnit=TODAY',
    'adv_decl_sjukvard': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=154&timeUnit=TODAY',
    'adv_decl_teknik': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=180&timeUnit=TODAY',
    'adv_decl_allmennyttig': 'https://www.avanza.se/aktier/vinnare-forlorare.html?countryCode=SE&sectorIds=210&timeUnit=TODAY',
    'energi': 'https://www.avanza.se/index/om-indexet.html/334578/energi', 
    'fin_fast': 'https://www.avanza.se/index/om-indexet.html/334593/finans-fastighet',
    'fordon': 'https://www.avanza.se/index/om-indexet.html/334580/fordon-och-reservdelar',
    'health': 'https://www.avanza.se/index/om-indexet.html/334584/halsovard',
    'industrials': 'https://www.avanza.se/index/om-indexet.html/334586/industrivaror',
    'power_support': 'https://www.avanza.se/index/om-indexet.html/334591/kraftforsorjning',
    'livsmedel': 'https://www.avanza.se/index/om-indexet.html/334581/livsmedel',
    'material': 'https://www.avanza.se/index/om-indexet.html/334577/material',
    'resor_fritid': 'https://www.avanza.se/index/om-indexet.html/334603/resor-och-fritid',
    'teknologi': 'https://www.avanza.se/index/om-indexet.html/334597/teknologi',
    'telekom': 'https://www.avanza.se/index/om-indexet.html/334602/telekom',
    'omxs30': 'https://www.avanza.se/index/om-indexet.html/19002/omx-stockholm-30',
    'omxspi': 'https://www.avanza.se/index/om-indexet.html/18988/omx-stockholm-pi'
}

def get_soup(url):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    return soup


def get_quote(url):
    entries = []
    soup = get_soup(url)
    uls = soup.find_all("ul",{"class": "cleanList floatList clearFix quoteBar"})
    for li in uls[0].find_all("li"):
        str = li.find_all("span", class_="pushBox roundCorners3")
        if len(str) != 0:
            str = str[0].string.replace(u'\xa0', u'')
            entries.append(str.replace(",","."))
            return entries

def get_all_data(url):
    entries = []
    soup = get_soup(url)
    uls = soup.find_all("ul",{"class": "cleanList floatList"})
    for ul in uls[0].find_all("li"):
        win = ""
        str = ul.find_all("span", class_="descriptionText")[0].next_element.strip()
        start = str.find('(') + 1
        end = str.find(' st',start)
        win = win + (str[start:end])
        entries.append(win)
    return entries

def get_dest(gsheet):
    dest = {}
    gc = gspread.service_account(filename='adv-decl-5f46e18b7139.json')
    gsh = gc.open(gsheet)
    wsheet = gsh.get_worksheet(0)
    dest['wsheet'] = wsheet
    last_index = len(wsheet.get_all_values())
    dest['last_i'] = last_index
    next_row = last_index + 1
    dest['next_i'] = next_row
    last = wsheet.get_all_values()[next_row - 2]
    dest['last'] = last
    return dest

def push_data(entries,dest,key):
    print(entries)
    if "adv_decl" in key:
        print("pushing adv_decl")
        dest['wsheet'].update_cell(dest['next_i'], 1, currentDate)
        dest['wsheet'].update_cell(dest['next_i'], 2, entries[0])
        dest['wsheet'].update_cell(dest['next_i'], 3, entries[1])
        dest['wsheet'].update_cell(dest['next_i'], 4, entries[2])

    else:
        print("pushing " + key + " index")
        dest['wsheet'].update_cell(dest['next_i'], 1, currentDate)
        dest['wsheet'].update_cell(dest['next_i'], 2, entries[0])


def main():
    currentDate = datetime.today().strftime('%Y-%m-%d')
    print(currentDate)
    print(os.environ.get('DRYRUN'))
    for key, value in links_dict.items():
        print(key)
        if "adv_decl" in key:
            entries = get_all_data(value)
            dest = get_dest(key)
            print(entries)
        else:
            entries = get_quote(value)
            dest = get_dest(key)
            print(entries)
        if 'DRYRUN' in os.environ:
            if "dry" in os.environ.get('DRYRUN'): 
                print("Running dry. No changes will be made.")
            else:
                print("Have we already done this?")
                if currentDate not in dest['last']:
                    print("No, let's do it then")
                    push_data(entries,dest,key)
                else:
                    print("Yes, nothing to do then")
        sleep(15)


if __name__ == "__main__":

    main()
    