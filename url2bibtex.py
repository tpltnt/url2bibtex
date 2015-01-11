#!/usr/bin/env python

import requests
import sys
import datetime

def getWaybackData(url):
    """
    Get data from the wayback machine at archive.org
    if feasible.

    :param url: URL to check
    :type url: str
    :returns: dict
    """
    if 0 == len(url):
        return {}
    p = {'url': url}
    r = requests.get('https://archive.org/wayback/available', params=p)
    print(r.url)
    if 200 == r.status_code:
        wb = r.json()
        if 'archived_snapshots' not in wb.keys():
            return {}
        else:
            wb = wb['archived_snapshots']
        if 0 == len(wb):
            return {}
    return {}

urldata = {'urldate': str(datetime.date.today()), 'year': str(datetime.date.today().year)}
print(getWaybackData(sys.argv[1]))
print(urldata)
"""
@ONLINE{bla_foo:2023:Online,
author = {Doe, John},
title = {this is a test},
month = jun,
year = {2023},
url = {http://www.bla.foo},
urldate = {2023-05-42}
}
"""
